# UC1 — Multi-Step Claim Intake Processing

Five-prompt chained pipeline (P1 → P2 → P3 → P4 → P5) that transforms raw FNOL (First Notice of Loss) narratives into structured claim records.

## Directory layout

- [prompts/](prompts/) — One subdirectory per prompt in the pipeline:
  - [p1-extraction/](prompts/p1-extraction/) — Extracts structured fields from raw FNOL narrative
    - [versions/01/](prompts/p1-extraction/versions/01/) — Prompt version 01
      - `system-prompt.jinja` — System prompt (fixed instructions, sent as Bedrock `system` parameter)
      - `user-prompt.jinja` — User prompt template with `{{ narrative }}` placeholder
      - `metadata.toml` — Version description and date
    - [normal/](prompts/p1-extraction/normal/) — Normal (non-malicious) FNOL test inputs. One `.toml` per scenario, covering auto, property, workers comp, GL, and edge cases.
    - [attack/](prompts/p1-extraction/attack/) — Malicious FNOL test inputs with embedded attacks (prompt injection, hidden instructions, role confusion). One `.toml` per attack technique.
  - `p2-classification/` — Determines line of business *(not yet populated)*
  - `p3-triage/` — Assigns severity and priority *(not yet populated)*
  - `p4-coverage-check/` — Cross-references against policy rules *(not yet populated)*
  - `p5-routing/` — Generates summary and routing recommendation *(not yet populated)*
