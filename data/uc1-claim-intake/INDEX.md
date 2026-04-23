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
  - [p2-classification/](prompts/p2-classification/) — Classifies line of business from P1 extraction output
    - [versions/01/](prompts/p2-classification/versions/01/) — Prompt version 01
      - `system-prompt.jinja` — System prompt with classification rules and anti-injection instructions
      - `user-prompt.jinja` — User prompt template with `{{ extraction_json }}` placeholder
      - `metadata.toml` — Version description and date
    - [normal/](prompts/p2-classification/normal/) — Normal test inputs (simulated P1 output). Covers auto, property, workers comp, GL, and ambiguous multi-LoB cases.
    - [attack/](prompts/p2-classification/attack/) — Chain-propagation attack inputs where P1 output contains injected payloads attempting misclassification.
  - `p3-triage/` — Assigns severity and priority *(not yet populated)*
  - `p4-coverage-check/` — Cross-references against policy rules *(not yet populated)*
  - `p5-routing/` — Generates summary and routing recommendation *(not yet populated)*
