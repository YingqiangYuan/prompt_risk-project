# Author's Design Notes

## Why this project exists

We are embedded in an enterprise engagement with a large insurance carrier — covering personal, auto, home, commercial, and workers' compensation lines. The client is building AI Agents to improve customer experience and operational efficiency. Insurance is a compliance-heavy industry: every AI-assisted decision may face regulatory scrutiny. That makes **prompt risk** — the security and correctness risks embedded in the prompts that drive these agents — a first-class concern.

This library (`prompt_risk`) is the tooling layer for that concern. It provides versioned prompt management, automated evaluation, and LLM-as-judge risk assessment, all designed to slot into a governance workflow described in `docs/source/01-Project-Background/03-Governance-Recommendations/index.rst`.

---

## Mental model: Use Cases as DAGs

Each business use case (e.g., claim intake) is a **DAG of steps**. Some steps are deterministic code; others are LLM-driven. Each LLM-driven step has a **Prompt** — and that prompt is what we evaluate and judge.

Concretely, UC1 (Claim Intake) is a five-step pipeline: P1 Extraction → P2 Classification → P3 Triage → P4 Coverage Check → P5 Routing. Each step receives the output of the previous step as input. The chain-propagation property is important: an attack that corrupts P1 output can cascade through P2 and P3. Our test data includes attack cases that specifically test this propagation (`data/uc1-claim-intake/prompts/p2-classification/attack/`, `p3-triage/attack/`).

The registry of use cases and prompt IDs lives in `constants.py` — `UseCaseIdEnum` and `PromptIdEnum`. Each `PromptIdEnum` value encodes its use case and short name (e.g., `uc1-claim-intake:p1-extraction`) and computes its `dir_root` path automatically.

---

## Prompt versioning

Every prompt is a directory under `data/{use_case_id}/prompts/{short_name}/versions/{version}/` containing:

- `system-prompt.jinja` — static instructions (cached for cost savings)
- `user-prompt.jinja` — template with `{{ data.field }}` placeholders for runtime data
- `metadata.toml` — description, date, and optionally `risk_profile`

Versioning is deliberate. Version 01 of P1 Extraction is the production-quality prompt. Versions 02, 03, 04 are **intentionally vulnerable** — each with a different `risk_profile` in its metadata:

- v02: over-permissive (no refusal, no scope boundaries, unconditional compliance)
- v03: minimal (technically functional but zero protective instructions)
- v04: committee prompt (has guardrails but contradictory compliance pressure that can override them)

This lets us demonstrate how the judge system detects different risk patterns and how evaluation results degrade across versions.

The `Prompt` dataclass in `prompts.py` handles loading. It uses `@cached_property` throughout — paths, raw content, and compiled `jinja2.Template` objects are all lazy-loaded and cached on first access. The factory method `Prompt.from_use_case()` constructs the canonical ID format.

---

## System prompt caching strategy

We separate system and user prompts for a reason beyond clean architecture: **Bedrock prompt caching**.

The system prompt is static per version — same text for every request. We attach a `cachePoint` marker after it in the Bedrock API call so the prefix is cached and reused across invocations, saving cost and latency.

The user prompt changes every request (it contains the actual user data), so it is intentionally excluded from caching — caching it would just waste cache-write cost with zero hit chance. This rationale is documented in `p1_extraction_runner.py` docstring (lines 88-111).

The Bedrock API wrapper in `bedrock_utils.py` is intentionally thin — a single `converse()` function that takes `system` (list of text/cachePoint dicts) and `messages` (standard role/content format) and returns the extracted text.

---

## Input validation: Pydantic at the boundary

User prompt data is validated with Pydantic models before rendering. For example, `P1ExtractionUserPromptData` validates the FNOL narrative input, and the Jinja template renders from the validated model. This ensures the prompt never receives malformed input.

Each runner defines its own input model (e.g., `P1ExtractionUserPromptData` in `p1_test_data.py`) and output model (e.g., `P1ExtractionOutput` in `p1_extraction_runner.py`). Output models use `Field()` with constraints and descriptions, plus custom `@field_validator` decorators where needed (e.g., date format validation).

We use `T.Literal` extensively instead of Python enums for LLM output fields — Pydantic validates membership automatically, and it maps cleanly to what the LLM actually produces (plain strings).

---

## Output validation and self-correcting retry

LLM output is not trusted. The pipeline:

1. Extract JSON from the raw response — handles markdown-fenced code blocks via regex in `llm_output.py` (`extract_json()`)
2. Parse into the Pydantic output model
3. If validation fails, **do not retry from scratch** — instead, append the assistant's failed response and a user message explaining the validation error back into the conversation history, then call the LLM again
4. Repeat up to 3 times (`MAX_RETRIES = 3`)

This is multi-turn error recovery, not blind retry. The LLM sees exactly what it produced and what was wrong with it, giving it the best chance to self-correct. If all 3 retries fail, `JsonExtractionError` (defined in `exc.py`) is raised, carrying the `raw_output` for debugging.

---

## Evaluation engine

The evaluation engine in `evaluations.py` is model-agnostic. It compares any Pydantic `BaseModel` instance against assertions from TOML test case files.

Three assertion operators:

| Operator | Section in TOML | Meaning |
|----------|----------------|---------|
| `eq` | `[expected]` | Scalar field must equal expected value |
| `in` | `[expected]` | Field must be one of the acceptable values (list) |
| `ne` | `[attack_target]` | Field must NOT equal the injected value |

Evaluation is AND logic — all assertions must pass. Results are structured as `EvalResult` containing a list of `FieldEvalResult`, with a pretty-print utility that shows pass/fail with emoji indicators and full model dumps on failure.

---

## Test data: normal vs. attack

Each prompt has two test data directories:

- `normal/` — legitimate inputs covering realistic scenarios (multi-LoB, edge cases, ambiguous narratives)
- `attack/` — adversarial inputs with embedded prompt injections, role confusion attempts, and override instructions

Each test case is a single `.toml` file with sections: `[meta]`, `[input]`, `[expected]`, `[attack_target]`.

For normal cases, `[expected]` defines ground-truth assertions. For attack cases, `[attack_target]` defines the values the attacker is trying to force into the output — the test passes only if the output does NOT contain these values.

Test data loaders are Pydantic models with lazy TOML parsing (`P1ExtractionUserPromptDataLoader` etc.), registered in enum classes (`P1ExtractionUserPromptDataLoaderEnum`) for discoverability and IDE autocomplete. Naming convention: `a_01_*` for attacks, `b_01_*` for normal cases.

---

## Judge system

Judges are LLM-as-judge prompts — they use an LLM to semantically evaluate whether a production prompt has security risks. Each judge covers one risk dimension.

J1 (Over-Permissive Authorization) in `judges/j1_over_permissive.py` evaluates five criteria: refusal capability, scope boundaries, unconditional compliance, failure handling, and anti-injection guardrails. The judge's own prompt templates live in `data/judges/prompts/j1-over-permissive/versions/01/`.

Input: `J1UserPromptData` (target system prompt + optional user prompt template).
Output: `J1Result` with per-criterion `J1Finding` (severity: major/minor/pass), overall risk level (critical/high/medium/low/pass), numeric score (1-5), and summary.

The judge uses the same self-correcting retry pattern as the runners — validation errors are fed back to the LLM for multi-turn recovery.

The judge system is extensible — new judges (J2, J3, ...) follow the same pattern: a prompt template in `data/judges/`, a runner module in `prompt_risk/judges/`, and Pydantic models for input/output.

---

## Testing philosophy

Two tiers:

- **Unit tests** (`tests/`): In-memory, no LLM calls. Test the abstractions — prompt loading, evaluation logic, data parsing, path resolution. Run with `mise run cov`.
- **Integration/example scripts** (`examples/`): Hit real LLM via Bedrock. Used for manual, on-demand testing during development. Not in CI — we save cost by running these selectively.

Each test file follows the project convention of an `if __name__ == "__main__":` block that runs pytest as a subprocess with coverage for the specific module, enabling quick isolated testing during development.

---

## Code organization

The package is structured for navigability:

- `prompt_risk/` — core modules (prompts, evaluations, LLM utils, constants, paths, exceptions)
- `prompt_risk/judges/` — judge implementations
- `prompt_risk/uc/uc1/` — UC1-specific runners and data loaders
- `prompt_risk/one/` — singleton (`one`) providing config and AWS clients, composed from mixins via `One(OneConfigMixin, OneBotoSesMixin)`
- `prompt_risk/tests/` — test helpers
- `prompt_risk/vendor/` — vendored utilities

`PathEnum` in `paths.py` provides all project paths as a singleton with pre-computed `Path` attributes — no runtime directory lookups, no "what's the current directory?" ambiguity.

Everything is type-safe: Pydantic models for all structured data, `T.Literal` for LLM enums, `TYPE_CHECKING` guards for boto3 stubs (avoiding heavyweight runtime imports while keeping mypy happy), and `typing as T` convention throughout.

---

## What's not yet built

- P4 (Coverage Check) and P5 (Routing) in the UC1 pipeline — directory stubs exist but prompts are not yet populated
- LLM-as-judge integration into the evaluation engine — currently evaluation uses rule-based assertions only; judge results are separate
- Additional judge dimensions beyond J1 (Over-Permissive)
- CI integration for LLM-dependent tests (currently manual to save cost)
