# -*- coding: utf-8 -*-

from prompt_risk.uc.uc1.p1_extraction_runner import run_p1_extraction

from prompt_risk.uc.uc1.prompt import P1LoaderEnum
from prompt_risk.one.api import one
from rich import print as rprint

output = run_p1_extraction(
    client=one.bedrock_runtime_client,
    data=P1LoaderEnum.b_01_auto_rear_end.value.data,
    prompt_version="01",
)
rprint(output)
