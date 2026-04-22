# -*- coding: utf-8 -*-

"""
Run Prompt A extraction on a single test case to see the result.

Usage::

    python examples/uc1-claim-intake/run_prompt_a.py
"""

import json

from prompt_risk.paths import path_enum
from prompt_risk.uc.uc1.testing import run_prompt_a_test
from prompt_risk.one.api import one

MODEL_ID = "us.amazon.nova-2-lite-v1:0"


def main():
    client = one.bedrock_runtime_client
    uc1_dir = path_enum.dir_data_uc1
    prompt_a_dir = uc1_dir / "prompts" / "prompt-a-extraction"

    # --- Run a benign test case ---
    benign_path = prompt_a_dir / "test-inputs" / "benign" / "b-01.toml"
    print("=" * 60)
    print(f"Running benign test: {benign_path.name}")
    print("=" * 60)
    result = run_prompt_a_test(client, MODEL_ID, benign_path)
    print(json.dumps(result, indent=2))

    # --- Run an adversarial test case ---
    adversarial_path = prompt_a_dir / "test-inputs" / "adversarial" / "a-01.toml"
    print()
    print("=" * 60)
    print(f"Running adversarial test: {adversarial_path.name}")
    print("=" * 60)
    result = run_prompt_a_test(client, MODEL_ID, adversarial_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
