# -*- coding: utf-8 -*-

from prompt_risk.uc.uc1.p1_extraction_runner import run_p1_extraction
from prompt_risk.uc.uc1.prompt import P1LoaderEnum
from prompt_risk.evaluations import evaluate, print_eval_result
from prompt_risk.one.api import one

client = one.bedrock_runtime_client

for case in P1LoaderEnum:
    loader = case.value
    print(f"\n{'='*60}")
    print(f"{case.name}  ({loader.type}/{loader.name})")

    output = run_p1_extraction(client=client, data=loader.data, prompt_version="01")

    if loader.expected or loader.attack_target:
        result = evaluate(output, loader.expected, loader.attack_target)
        print_eval_result(result)
    else:
        print("  (no assertions defined)")
        print(output)
