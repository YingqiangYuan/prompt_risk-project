# -*- coding: utf-8 -*-

import typing as T

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

def func(
    client: "BedrockRuntimeClient",

    system_prompt: str,
    user_prompt
):
    pass