# -*- coding: utf-8 -*-

"""
J1 Over-Permissive Authorization Judge.

Evaluates a prompt's system prompt text (and optionally its user prompt
template) for over-permissive authorization risks.  The judge itself is a
prompt — it uses an LLM to perform semantic analysis against five criteria
defined in its own system prompt template.

This module is **use-case-agnostic**.  It accepts raw prompt text as strings
and knows nothing about FNOL, claims, or any specific business domain.
Use-case-specific wrappers (e.g. ``uc.uc1.j1_uc1_p1``) handle loading
prompt files and calling this function.
"""

import typing as T
import json
import re
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from ..bedrock_utils import converse

if T.TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

import jinja2

# ---------------------------------------------------------------------------
# Paths — judge prompt templates live under data/judges/j1-over-permissive/
# ---------------------------------------------------------------------------
_DIR_DATA = Path(__file__).absolute().parent.parent.parent / "data"
_DIR_J1 = _DIR_DATA / "judges" / "j1-over-permissive"


def _load_judge_template(version: str, filename: str) -> jinja2.Template:
    path = _DIR_J1 / "versions" / version / filename
    return jinja2.Template(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------
T_SEVERITY = T.Literal["major", "minor", "pass"]
T_OVERALL_RISK = T.Literal["critical", "high", "medium", "low", "pass"]


class J1Finding(BaseModel):
    """A single criterion-level finding from the J1 judge."""

    criterion: str
    severity: T_SEVERITY
    evidence: str
    explanation: str
    recommendation: str


class J1Result(BaseModel):
    """Complete J1 judge evaluation result."""

    overall_risk: T_OVERALL_RISK
    score: int = Field(ge=1, le=5)
    findings: list[J1Finding]
    summary: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
MAX_RETRIES = 3


def _extract_json(text: str) -> str:
    """Strip markdown code fences if present, return raw JSON string."""
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_j1_over_permissive(
    client: "BedrockRuntimeClient",
    target_system_prompt: str,
    target_user_prompt_template: str,
    judge_version: str = "01",
    model_id: str = "us.amazon.nova-2-lite-v1:0",
) -> J1Result:
    """Evaluate a prompt for over-permissive authorization risks.

    Parameters
    ----------
    client:
        Bedrock Runtime client.
    target_system_prompt:
        The full text of the system prompt being evaluated.
    target_user_prompt_template:
        The full text of the user prompt template being evaluated
        (with Jinja placeholders still present).
    judge_version:
        Which version of the J1 judge prompt to use.
    model_id:
        Bedrock model ID for the judge LLM.

    Returns
    -------
    J1Result
        Structured evaluation result with overall risk, score, findings,
        and summary.
    """
    judge_system_template = _load_judge_template(judge_version, "system-prompt.jinja")
    judge_user_template = _load_judge_template(judge_version, "user-prompt.jinja")

    system = [
        {"text": judge_system_template.render()},
        {"cachePoint": {"type": "default"}},
    ]

    # Build a simple namespace so the template can use {{ data.xxx }}
    data = {
        "target_system_prompt": target_system_prompt,
        "target_user_prompt_template": target_user_prompt_template,
    }
    user_prompt = judge_user_template.render(data=data)

    messages: list[dict] = [
        {"role": "user", "content": [{"text": user_prompt}]},
    ]

    for attempt in range(MAX_RETRIES):
        text = converse(client, model_id, system, messages)
        json_text = _extract_json(text)

        try:
            return J1Result(**json.loads(json_text))
        except (json.JSONDecodeError, ValidationError) as exc:
            if attempt == MAX_RETRIES - 1:
                raise

            error_msg = (
                f"Your previous response failed validation:\n{exc}\n\n"
                "Please return a corrected JSON object."
            )
            messages.append({"role": "assistant", "content": [{"text": text}]})
            messages.append({"role": "user", "content": [{"text": error_msg}]})

    raise Exception("Should never reach this line of code")  # pragma: no cover


# ---------------------------------------------------------------------------
# Pretty-print
# ---------------------------------------------------------------------------
_SEVERITY_ICON = {"pass": "✅", "minor": "⚠️", "major": "❌"}
_RISK_ICON = {"pass": "✅", "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}


def print_j1_result(result: J1Result) -> None:
    """Print J1 evaluation result to stdout."""
    for f in result.findings:
        icon = _SEVERITY_ICON.get(f.severity, "?")
        print(f"  {icon} [{f.severity.upper()}] {f.criterion}")
        print(f"      Evidence: {f.evidence}")
        print(f"      Explanation: {f.explanation}")
        if f.severity != "pass":
            print(f"      Recommendation: {f.recommendation}")
    risk_icon = _RISK_ICON.get(result.overall_risk, "?")
    print(f"  {risk_icon} Overall: {result.overall_risk.upper()} (score {result.score}/5)")
    print(f"  Summary: {result.summary}")
