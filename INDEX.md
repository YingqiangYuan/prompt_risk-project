# Project Source Code Index

## `prompt_risk/` — Python Package

Core library for prompt risk evaluation. Loads versioned prompt templates from data files, invokes LLM via AWS Bedrock, parses structured output, and evaluates results against data-driven assertions.

### Top-level modules

- [prompts.py](prompt_risk/prompts.py) — `Prompt` dataclass: resolves versioned prompt templates (Jinja2) from the `data/` directory and renders them with runtime data.
- [evaluations.py](prompt_risk/evaluations.py) — Generic, model-agnostic evaluation engine. Compares LLM output against assertions defined in test-case TOML files. Supports three assertion types: `expected` (ground-truth match), `attack_target` (injection detection via `!=`).
- [bedrock_utils.py](prompt_risk/bedrock_utils.py) — Thin wrapper around the AWS Bedrock Converse API. Sends system/user messages and returns the assistant's text response.
- [llm_output.py](prompt_risk/llm_output.py) — Post-processing utilities for raw LLM text responses (e.g. JSON extraction from fenced code blocks).
- [constants.py](prompt_risk/constants.py) — Enumerations for use-case IDs (`UseCaseIdEnum`) and prompt IDs (`PromptIdEnum`). Each prompt ID encodes its use case and short name (e.g. `uc1-claim-intake:p1-extraction`).
- [paths.py](prompt_risk/paths.py) — `PathEnum` singleton providing absolute paths to all project directories and files (source, tests, data, docs, build artifacts).
- [exc.py](prompt_risk/exc.py) — Custom exceptions (`JsonExtractionError`).

### `prompt_risk/judges/` — Judge modules

LLM-as-judge implementations. Each judge evaluates a target prompt for a specific risk category.

- [j1_over_permissive.py](prompt_risk/judges/j1_over_permissive.py) — J1 Over-Permissive Authorization Judge. Use-case-agnostic: accepts raw prompt text and returns a structured `J1Result` with per-criterion findings and an overall risk score.

### `prompt_risk/uc/` — Use-case runners

Use-case-specific modules that wire together prompts, test data loaders, and runners.

- [uc/uc1/](prompt_risk/uc/uc1/) — UC1 Claim Intake use case:
  - [p1_extraction_runner.py](prompt_risk/uc/uc1/p1_extraction_runner.py) — Runs the P1 FNOL extraction prompt via Bedrock and parses output into `P1ExtractionOutput`.
  - [p1_test_data.py](prompt_risk/uc/uc1/p1_test_data.py) — Data loader for P1 normal and attack test cases (reads TOML files from `data/`).
  - [p2_classification_runner.py](prompt_risk/uc/uc1/p2_classification_runner.py) — Runs the P2 classification prompt.
  - [p2_test_data.py](prompt_risk/uc/uc1/p2_test_data.py) — Data loader for P2 test cases.
  - [p3_triage_runner.py](prompt_risk/uc/uc1/p3_triage_runner.py) — Runs the P3 triage prompt.
  - [p3_test_data.py](prompt_risk/uc/uc1/p3_test_data.py) — Data loader for P3 test cases.
  - [j1_uc1_p1.py](prompt_risk/uc/uc1/j1_uc1_p1.py) — Wrapper: runs J1 judge on UC1-P1 extraction prompt with concrete test data.

### `prompt_risk/one/` — Runtime environment

Singleton (`one`) that provides project configuration and AWS session/client access.

- [one_01_main.py](prompt_risk/one/one_01_main.py) — `One` class composing all mixins; exports the `one` singleton.
- [one_02_config.py](prompt_risk/one/one_02_config.py) — Configuration mixin (placeholder).
- [one_03_boto_ses.py](prompt_risk/one/one_03_boto_ses.py) — Boto3 session and Bedrock runtime client mixin.
- [api.py](prompt_risk/one/api.py) — Re-exports `one` for convenient import.

### `prompt_risk/tests/` — Test helpers

- [helper.py](prompt_risk/tests/helper.py) — Wrappers around `pytest_cov_helper` for running unit tests and coverage from `if __name__ == "__main__":` blocks.

### `prompt_risk/vendor/` — Vendored utilities

- [pytest_cov_helper.py](prompt_risk/vendor/pytest_cov_helper.py) — Helper for running pytest with coverage as a subprocess.

---

## `examples/` — Runnable Scripts

End-to-end example scripts demonstrating how to use the library. Each script pins a prompt version and test case, then runs the pipeline.

- [uc1-claim-intake/](examples/uc1-claim-intake/) — UC1 Claim Intake examples:
  - [run_uc1_p1_extraction.py](examples/uc1-claim-intake/run_uc1_p1_extraction.py) — Run P1 extraction on a selected test case and evaluate the output.
  - [run_uc1_p2_classification.py](examples/uc1-claim-intake/run_uc1_p2_classification.py) — Run P2 classification.
  - [run_uc1_p3_triage.py](examples/uc1-claim-intake/run_uc1_p3_triage.py) — Run P3 triage.
- [judges/](examples/judges/) — Judge examples:
  - [run_j1_on_uc1_p1.py](examples/judges/run_j1_on_uc1_p1.py) — Run J1 Over-Permissive judge on UC1-P1 prompt across all test data loaders.
