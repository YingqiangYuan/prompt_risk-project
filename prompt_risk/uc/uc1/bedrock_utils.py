# -*- coding: utf-8 -*-

"""
Bedrock Converse API wrapper and UC1 Prompt A business function.
"""

import typing as T
import json

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient


def converse(
    client: "BedrockRuntimeClient",
    model_id: str,
    user_message: str,
) -> str:
    """
    Minimal wrapper around the Bedrock Converse API.

    Sends a single user message and returns the response text.
    """
    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        ],
    )
    return response["output"]["message"]["content"][0]["text"]


def extract_fnol_fields(
    client: "BedrockRuntimeClient",
    model_id: str,
    prompt_template: str,
    narrative: str,
) -> dict:
    """
    Function 1: Prompt A business function.

    Takes a prompt template with a ``{narrative}`` placeholder and a raw FNOL
    narrative, calls the LLM, and returns the extracted fields as a dict.
    """
    user_message = prompt_template.replace("{narrative}", narrative)
    raw = converse(client, model_id, user_message)

    # The model may wrap JSON in a markdown code block — strip it
    text = raw.strip()
    if text.startswith("```"):
        # remove first and last lines (``` markers)
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    return json.loads(text)
