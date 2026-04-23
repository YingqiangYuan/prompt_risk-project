# -*- coding: utf-8 -*-

import typing as T
import json
import re
from pydantic import BaseModel, Field, ValidationError, field_validator

from ...constants import PromptIdEnum
from ...prompts import Prompt
from .prompt import P1ExtractionUserPromptData

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

T_INJURY_INDICATOR = T.Literal["none", "minor", "moderate", "severe", "fatal"]
T_ESTIMATE_SEVERITY = T.Literal["low", "medium", "high"]


class P1ExtractionOutput(BaseModel):
    # fmt: off
    date_of_loss: str = Field(description="Date of the incident (YYYY-MM-DD or 'unknown')")
    time_of_loss: str = Field(description="Time of the incident (HH:MM 24-hour or 'unknown')")
    location: str = Field(description="Where the incident occurred")
    line_of_business_hint: str = Field(description="One of auto, property, workers_comp, general_liability, or ambiguous")
    parties_involved: list[str] = Field(description="List of party roles")
    damage_description: str = Field(description="Brief summary of damage")
    injury_indicator: T_INJURY_INDICATOR = Field(description="none, minor, moderate, severe, or fatal")
    police_report: str = Field(description="Report number if mentioned, otherwise 'none'")
    evidence_available: list[str] = Field(description="List of available evidence types")
    estimated_severity: T_ESTIMATE_SEVERITY = Field(description="low, medium, or high")
    # fmt: on

    @field_validator("date_of_loss")
    @classmethod
    def validate_date_of_loss(cls, v: str) -> str:
        if v == "unknown":
            return v
        from datetime import datetime

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"date_of_loss must be 'YYYY-MM-DD' or 'unknown', got '{v}'"
            )
        return v


MAX_RETRIES = 3


def _extract_json(text: str) -> str:
    """Strip markdown code fences if present, return raw JSON string."""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text


def _converse(
    client: "BedrockRuntimeClient",
    model_id: str,
    system: list[dict],
    messages: list[dict],
) -> str:
    """Call Bedrock converse and return the assistant text."""
    response = client.converse(
        modelId=model_id,
        system=system,
        messages=messages,
    )
    return response["output"]["message"]["content"][0]["text"]


def run(
    client: "BedrockRuntimeClient",
    data: P1ExtractionUserPromptData,
    prompt_version: str = "01",
    model_id: str = "us.amazon.nova-2-lite-v1:0",
) -> P1ExtractionOutput:
    prompt = Prompt(id=PromptIdEnum.UC1_P1_EXTRACTION.value, version=prompt_version)
    system = [
        {"text": prompt.system_prompt_template.render()},
        {"cachePoint": {"type": "default"}},
    ]
    user_prompt = prompt.user_prompt_template.render(data=data)
    messages: list[dict] = [
        {"role": "user", "content": [{"text": user_prompt}]},
    ]

    for attempt in range(MAX_RETRIES):
        text = _converse(client, model_id, system, messages)
        json_text = _extract_json(text)

        try:
            return P1ExtractionOutput(**json.loads(json_text))
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == MAX_RETRIES - 1:
                raise

            error_msg = (
                f"Your previous response failed validation:\n{exc}\n\n"
                "Please return a corrected JSON object."
            )
            # Append the assistant's reply and the error feedback
            messages.append({"role": "assistant", "content": [{"text": text}]})
            messages.append({"role": "user", "content": [{"text": error_msg}]})
