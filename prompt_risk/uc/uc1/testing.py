# -*- coding: utf-8 -*-

"""
Function 2: Test runner for UC1 Prompt A.

Loads test data from the data directory, calls the extraction function,
and prints the result for review.
"""

import typing as T
import tomllib
from pathlib import Path

from prompt_risk.paths import path_enum
from prompt_risk.uc.uc1.bedrock_utils import extract_fnol_fields

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text())


def _load_prompt_template(prompt_dir: Path, version: str = "v01") -> tuple[str, str]:
    """
    Load a prompt markdown file. Returns (model_id, prompt_body).

    The front matter contains ``target_model``; the body after the second
    ``---`` is the actual prompt text.
    """
    path = prompt_dir / f"{version}.md"
    text = path.read_text()
    # split on "---" fences: ['', frontmatter, body]
    parts = text.split("---", 2)
    frontmatter = parts[1]
    body = parts[2].strip()

    model_id = "us.amazon.nova-2-lite-v1:0"
    for line in frontmatter.strip().splitlines():
        if line.startswith("target_model:"):
            model_id = line.split(":", 1)[1].strip()
            break

    return model_id, body


def _resolve_narrative(test_input: dict, uc1_dir: Path) -> str:
    """
    Resolve the narrative text from a test input.

    If the test input has ``shared_input_ref``, look it up in shared-inputs/.
    Otherwise use the inline ``narrative`` field.
    """
    inp = test_input["input"]
    if "shared_input_ref" in inp:
        ref_id = inp["shared_input_ref"]
        # search both benign/ and adversarial/ for the matching file
        for subdir in ("benign", "adversarial"):
            search_dir = uc1_dir / "shared-inputs" / subdir
            for toml_path in search_dir.glob("*.toml"):
                data = _load_toml(toml_path)
                if data["meta"]["id"] == ref_id:
                    return data["input"]["narrative"]
        raise FileNotFoundError(
            f"shared input ref '{ref_id}' not found in shared-inputs/"
        )
    return inp["narrative"]


def run_prompt_a_test(
    client: "BedrockRuntimeClient",
    test_case_path: Path,
    prompt_version: str = "v01",
) -> dict:
    """
    Function 2: Run a single Prompt A test case.

    :param client: Bedrock runtime client.
    :param test_case_path: Path to a test input TOML file (benign or adversarial).
    :param prompt_version: Which prompt version to use (default "v01").
    :return: Dict with test metadata and the LLM extraction result.
    """
    uc1_dir = path_enum.dir_data_uc1
    prompt_dir = uc1_dir / "prompts" / "prompt-a-extraction"

    # Load test input
    test_input = _load_toml(test_case_path)
    meta = test_input["meta"]

    # Resolve narrative
    narrative = _resolve_narrative(test_input, uc1_dir)

    # Load prompt template
    model_id, prompt_template = _load_prompt_template(prompt_dir, prompt_version)

    # Call Function 1
    result = extract_fnol_fields(client, model_id, prompt_template, narrative)

    return {
        "test_id": meta["id"],
        "description": meta["description"],
        "prompt_version": prompt_version,
        "extraction_result": result,
    }
