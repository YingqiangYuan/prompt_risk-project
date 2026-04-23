# -*- coding: utf-8 -*-

import typing as T
import json
import re
from pydantic import BaseModel, Field

from ...constants import PromptIdEnum
from ...prompts import Prompt
from .prompt import P1ExtractionUserPromptData

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient


class P1ExtractionOutput(BaseModel):
    date_of_loss: str = Field(
        description="Date of the incident (YYYY-MM-DD or 'unknown')"
    )
    time_of_loss: str = Field(
        description="Time of the incident (HH:MM 24-hour or 'unknown')"
    )
    location: str = Field(description="Where the incident occurred")
    line_of_business_hint: str = Field(
        description="One of auto, property, workers_comp, general_liability, or ambiguous"
    )
    parties_involved: T.List[str] = Field(description="List of party roles")
    damage_description: str = Field(description="Brief summary of damage")
    injury_indicator: str = Field(description="none, minor, moderate, severe, or fatal")
    police_report: str = Field(
        description="Report number if mentioned, otherwise 'none'"
    )
    evidence_available: T.List[str] = Field(
        description="List of available evidence types"
    )
    estimated_severity: str = Field(description="low, medium, or high")


def run(
    client: "BedrockRuntimeClient",
    data: P1ExtractionUserPromptData,
    prompt_version: str = "01",
    model_id: str = "us.amazon.nova-2-lite-v1:0",
) -> Output:
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
    return Output(**json.loads(json_text))
