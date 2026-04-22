# -*- coding: utf-8 -*-

import enum


class UseCaseIdEnum(enum.StrEnum):
    UC1_CLAIM_INTAKE = "uc1-claim-intake"


class PromptIdEnum(enum.StrEnum):
    UC1_A_EXTRACTION = f"{UseCaseIdEnum.UC1_CLAIM_INTAKE}:prompt-a-extraction"
