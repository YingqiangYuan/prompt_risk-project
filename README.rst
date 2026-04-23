
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
