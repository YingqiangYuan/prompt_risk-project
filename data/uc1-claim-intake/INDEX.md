# UC1 — Multi-Step Claim Intake Processing

Five-prompt chained pipeline (A → B → C → D → E) that transforms raw FNOL (First Notice of Loss) narratives into structured claim records.

## How shared-inputs and test-inputs relate

[shared-inputs/](shared-inputs/) stores **raw FNOL narratives** — the actual data that enters the pipeline. Each file is a self-contained scenario with metadata and a narrative field.

[test-inputs/](prompts/prompt-a-extraction/test-inputs/) under each prompt are **lightweight test definitions** that either:
- **Reference** a shared input by ID (`shared_input_ref = "bi-01"`) — avoids duplicating the same narrative across prompts, or
- **Define inline data** for edge cases specific to that prompt

This separation means one shared narrative (e.g. a multi-vehicle accident) can be reused as input for Prompt A extraction tests, Prompt C triage tests, and pipeline-level end-to-end tests — without copying the text.

## Directory layout

- [shared-inputs/benign/](shared-inputs/benign/) — Normal FNOL narratives across lines of business (auto, property, workers comp, GL). One `.toml` per scenario.
- [shared-inputs/adversarial/](shared-inputs/adversarial/) — FNOL narratives with embedded attacks (prompt injection, hidden instructions, role confusion). One `.toml` per attack technique.
- [prompts/](prompts/) — One subdirectory per prompt in the pipeline:
  - [prompt-a-extraction/](prompts/prompt-a-extraction/) — Extracts structured fields from raw FNOL narrative
    - `v01.md` — Prompt template (versioned)
    - [test-inputs/benign/](prompts/prompt-a-extraction/test-inputs/benign/) — Benign test cases (refs to shared-inputs or inline edge cases)
    - [test-inputs/adversarial/](prompts/prompt-a-extraction/test-inputs/adversarial/) — Adversarial test cases (refs to shared adversarial inputs)
    - [expected-outputs/](prompts/prompt-a-extraction/expected-outputs/) — Expected extraction results for benign cases (exact-match + semantic-match fields)
    - [attack-criteria/](prompts/prompt-a-extraction/attack-criteria/) — Pass/fail criteria for adversarial cases (attack-success vs. defense-success conditions)
  - `prompt-b-classification/` — Determines line of business *(not yet populated)*
  - `prompt-c-triage/` — Assigns severity and priority *(not yet populated)*
  - `prompt-d-coverage-check/` — Cross-references against policy rules *(not yet populated)*
  - `prompt-e-routing/` — Generates summary and routing recommendation *(not yet populated)*
- `pipeline-tests/` — End-to-end tests that run a shared input through all five prompts and check results at each stage *(not yet populated)*
