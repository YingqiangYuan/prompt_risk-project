# -*- coding: utf-8 -*-

import enum


class UseCaseIdEnum(enum.StrEnum):
    """Registry of use-case identifiers."""

    UC1_CLAIM_INTAKE = "uc1-claim-intake"


class PromptIdEnum(enum.StrEnum):
    """Registry of prompt identifiers, formatted as ``{use_case_id}:{short_name}``."""

    UC1_P1_EXTRACTION = f"{UseCaseIdEnum.UC1_CLAIM_INTAKE}:p1-extraction"
