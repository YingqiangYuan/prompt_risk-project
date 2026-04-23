# -*- coding: utf-8 -*-

import typing as T
import json
import re
from pydantic import BaseModel, Field, field_validator

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


def run(
    client: "BedrockRuntimeClient",
    data: P1ExtractionUserPromptData,
    prompt_version: str = "01",
    model_id: str = "us.amazon.nova-2-lite-v1:0",
) -> P1ExtractionOutput:
    prompt = Prompt(id=PromptIdEnum.UC1_P1_EXTRACTION.value, version=prompt_version)
    system_prompt = prompt.system_prompt_template.render()
    user_prompt = prompt.user_prompt_template.render(data=data)
    response = client.converse(
        modelId=model_id,
        system=[{"text": system_prompt}],
        messages=[
            {
                "role": "user",
                "content": [{"text": user_prompt}],
            }
        ],
    )
    text = response["output"]["message"]["content"][0]["text"]
    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    json_text = match.group(1) if match else text
    return P1ExtractionOutput(**json.loads(json_text))
