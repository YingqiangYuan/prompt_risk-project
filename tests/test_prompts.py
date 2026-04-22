# -*- coding: utf-8 -*-

from prompt_risk.prompts import Prompt
from prompt_risk.constants import PromptIdEnum


def test_read_prompt():
    prompt = Prompt(
        id=PromptIdEnum.UC1_A_EXTRACTION.value,
        version=1,
    )
    _ = prompt.content


if __name__ == "__main__":
    from prompt_risk.tests import run_cov_test

    run_cov_test(
        __file__,
        "prompt_risk.prompts",
        preview=False,
    )
