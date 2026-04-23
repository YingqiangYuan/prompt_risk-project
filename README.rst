
.. image:: https://readthedocs.org/projects/yq-prompt-risk/badge/?version=latest
    :target: https://yq-prompt-risk.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/YingqiangYuan/prompt_risk-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/YingqiangYuan/prompt_risk-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/YingqiangYuan/prompt_risk-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/YingqiangYuan/prompt_risk-project

.. .. image:: https://img.shields.io/pypi/v/prompt-risk.svg
    :target: https://pypi.python.org/pypi/prompt-risk

.. .. image:: https://img.shields.io/pypi/l/prompt-risk.svg
    :target: https://pypi.python.org/pypi/prompt-risk

.. .. image:: https://img.shields.io/pypi/pyversions/prompt-risk.svg
    :target: https://pypi.python.org/pypi/prompt-risk

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/YingqiangYuan/prompt_risk-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/YingqiangYuan/prompt_risk-project

------

.. .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://prompt-risk.readthedocs.io/en/latest/py-modindex.html

.. .. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/YingqiangYuan/prompt_risk-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/YingqiangYuan/prompt_risk-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/YingqiangYuan/prompt_risk-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/prompt-risk#files


Welcome to ``prompt_risk`` Documentation
==============================================================================
.. image:: https://yq-prompt-risk.readthedocs.io/en/latest/_static/prompt_risk-logo.png
    :target: https://yq-prompt-risk.readthedocs.io/en/latest/

``prompt_risk`` is a Python framework for detecting, scoring, and mitigating security risks in LLM prompts deployed across enterprise environments. It combines deterministic rule-based scanning (secrets detection, keyword blocklists) with LLM-as-Judge semantic analysis to catch vulnerabilities that regex alone cannot find — over-permissive authorization, hardcoded sensitive data, role confusion, instruction conflicts, and logic ambiguity.

The project ships with six insurance-industry use cases (from FNOL (First Notice of Loss) claim intake pipelines to autonomous claims agents) as reference implementations, each with versioned prompt templates, normal and adversarial test data, and automated evaluation pipelines. Prompts and test cases are stored as Jinja templates and TOML files under a structured ``data/`` directory, making it easy to version, review, and extend.

Designed for integration into CI/CD workflows and prompt registries, ``prompt_risk`` turns prompt security from a manual, ad-hoc review process into a repeatable, auditable engineering practice. Install via ``pip install prompt-risk`` and start scanning your prompts programmatically.

- `Documentation & Demo <https://yq-prompt-risk.readthedocs.io/en/latest/>`_
- `GitHub Repository <https://github.com/YingqiangYuan/prompt_risk-project>`_
- `Submit an Issue <https://github.com/YingqiangYuan/prompt_risk-project/issues>`_


How It Works
------------------------------------------------------------------------------

**1. Use Case Pipeline** — Each business use case is a chain of LLM-driven steps. UC1 (Claim Intake) transforms a raw narrative into a structured, classified, triaged claim record:

.. code-block:: mermaid

    graph LR
        IN["FNOL Narrative"] --> P1["P1<br/>Extraction"]
        P1 -- "JSON" --> P2["P2<br/>Classification"]
        P2 -- "JSON" --> P3["P3<br/>Triage"]
        P3 -- "JSON" --> P4["P4<br/>Coverage"]
        P4 -- "JSON" --> P5["P5<br/>Routing"]

        style P1 fill:#1a5276,stroke:#2e86c1,color:#fff
        style P2 fill:#1a5276,stroke:#2e86c1,color:#fff
        style P3 fill:#1a5276,stroke:#2e86c1,color:#fff
        style P4 fill:#2c3e50,stroke:#7f8c8d,color:#aaa
        style P5 fill:#2c3e50,stroke:#7f8c8d,color:#aaa
        style IN fill:#1a1a2e,stroke:#3d3d5c,color:#eee

Each step receives the previous step's JSON output as input. P1-P3 are implemented; P4-P5 are planned (shown in gray).

----

**2. Single Step — LLM Call with Validation & Retry** — Every LLM-driven step follows the same pattern: render the prompt, call the model, validate the output, retry on failure:

.. code-block:: mermaid

    graph TD
        RENDER["Render Jinja template<br/>with input data"]
        CALL["Call LLM<br/>(Bedrock Converse API)"]
        EXTRACT["Extract JSON<br/>from response"]
        VALIDATE{"Pydantic<br/>validation"}
        OK["Return validated output"]
        FEEDBACK["Append error to<br/>conversation history"]
        FAIL["Raise exception"]

        RENDER --> CALL
        CALL --> EXTRACT
        EXTRACT --> VALIDATE
        VALIDATE -- "pass" --> OK
        VALIDATE -- "fail, attempt < 3" --> FEEDBACK
        FEEDBACK --> CALL
        VALIDATE -- "fail, attempt = 3" --> FAIL

        style OK fill:#1e6f3e,stroke:#27ae60,color:#fff
        style FAIL fill:#922b21,stroke:#c0392b,color:#fff
        style VALIDATE fill:#7d6608,stroke:#d4ac0d,color:#fff

The retry loop feeds the Pydantic ``ValidationError`` back to the LLM as a user message, giving it concrete feedback to self-correct rather than retrying blindly.

----

**3. Automated Evaluation** — Each prompt is tested against TOML-defined test cases with two types of assertions:

.. code-block:: mermaid

    graph LR
        subgraph tc["Test Case (TOML)"]
            INPUT["[input]<br/>FNOL narrative"]
            EXP["[expected]<br/>date = 2026-04-15<br/>police = HPD-04153"]
            ATK["[attack_target]<br/>injury ≠ none<br/>severity ≠ low"]
        end

        RUN["Run prompt<br/>on input"] --> CHECK

        subgraph CHECK["Assertions"]
            EQ["expected: eq / in<br/><i>output must match</i>"]
            NE["attack_target: ne<br/><i>output must NOT match</i>"]
        end

        CHECK --> PASS["All pass → ✅"]
        CHECK --> FAILR["Any fail → ❌"]

        INPUT --> RUN

        style EXP fill:#1e6f3e,stroke:#27ae60,color:#fff
        style ATK fill:#922b21,stroke:#c0392b,color:#fff
        style PASS fill:#1e6f3e,stroke:#27ae60,color:#fff
        style FAILR fill:#922b21,stroke:#c0392b,color:#fff

Normal cases verify correct extraction (``eq``/``in``). Attack cases verify the prompt resisted injection — the output must NOT contain attacker-injected values (``ne``).

----

**4. LLM-as-Judge Security Assessment** — Five judges evaluate prompt text for distinct risk dimensions. Each judge is itself a prompt that performs semantic analysis:

.. code-block:: mermaid

    graph LR
        PROMPT["Target Prompt<br/>(system + user template)"]

        PROMPT --> J1["<b>J1</b><br/>Over-Permissive"]
        PROMPT --> J2["<b>J2</b><br/>Sensitive Data"]
        PROMPT --> J3["<b>J3</b><br/>Role Confusion"]
        PROMPT --> J4["<b>J4</b><br/>Instruction Conflict"]
        PROMPT --> J5["<b>J5</b><br/>Logic Ambiguity"]

        J1 --> S1["Score 1-5<br/>+ per-criterion findings"]
        J2 --> S2["Score 1-5"]
        J3 --> S3["Score 1-5"]
        J4 --> S4["Score 1-5"]
        J5 --> S5["Score 1-5"]

        style J1 fill:#784212,stroke:#e67e22,color:#fff
        style J2 fill:#4a3520,stroke:#784212,color:#aaa
        style J3 fill:#4a3520,stroke:#784212,color:#aaa
        style J4 fill:#4a3520,stroke:#784212,color:#aaa
        style J5 fill:#4a3520,stroke:#784212,color:#aaa

        style S1 fill:#784212,stroke:#e67e22,color:#fff
        style S2 fill:#4a3520,stroke:#784212,color:#aaa
        style S3 fill:#4a3520,stroke:#784212,color:#aaa
        style S4 fill:#4a3520,stroke:#784212,color:#aaa
        style S5 fill:#4a3520,stroke:#784212,color:#aaa

J1 (implemented) evaluates 5 criteria: refusal capability, scope boundaries, unconditional compliance, failure handling, and anti-injection guardrails. J2-J5 are planned (shown in muted colors).

----

**5. Prompt Versioning** — Every prompt (including judges) is versioned with its own template files and metadata:

.. code-block:: mermaid

    graph TD
        subgraph uc["Use Case: uc1-claim-intake"]
            subgraph p1["Prompt: p1-extraction"]
                V1P["v01 — production<br/>✅ guardrails"]
                V2P["v02 — over-permissive<br/>❌ 'never refuse'"]
                V3P["v03 — minimal<br/>❌ no protections"]
                V4P["v04 — conflicting<br/>⚠️ mixed signals"]
            end
        end

        subgraph jd["Judges"]
            subgraph j1["Judge: j1-over-permissive"]
                V1J["v01"]
            end
        end

        subgraph files["Each version contains"]
            SYS["system-prompt.jinja"]
            USR["user-prompt.jinja"]
            META["metadata.toml<br/>description · date · risk_profile"]
        end

        V1P --- files
        V1J --- files

        style V1P fill:#1e6f3e,stroke:#27ae60,color:#fff
        style V2P fill:#922b21,stroke:#c0392b,color:#fff
        style V3P fill:#922b21,stroke:#c0392b,color:#fff
        style V4P fill:#7d6608,stroke:#d4ac0d,color:#fff
        style V1J fill:#784212,stroke:#e67e22,color:#fff

Multiple versions coexist — production-quality and intentionally vulnerable — so the judge system can demonstrate detection across risk profiles.


Learn More
------------------------------------------------------------------------------

- `Full Documentation <https://yq-prompt-risk.readthedocs.io/en/latest/>`_ — Project background, risk taxonomy, governance recommendations, and API reference.
- `Prompt Evaluation Demo <https://yq-prompt-risk.readthedocs.io/en/latest/06-Prompt-Runner-And-Evaluation-Demo/index.html>`_ — Interactive notebook: run prompts against test cases and evaluate outputs.
- `Judge Assessment Demo <https://yq-prompt-risk.readthedocs.io/en/latest/08-Judge-Demo/index.html>`_ — Interactive notebook: run LLM-as-Judge on prompt versions and inspect risk scores.
