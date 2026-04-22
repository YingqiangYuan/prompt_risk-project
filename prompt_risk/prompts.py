# -*- coding: utf-8 -*-

import dataclasses
from pathlib import Path

from cryptography.utils import cached_property

from .paths import path_enum


@dataclasses.dataclass
class Prompt:
    id: str
    version: int

    @classmethod
    def from_use_case(
        cls,
        use_case_id: str,
        short_name: str,
        version: int,
    ):
        return cls(
            id=f"{use_case_id}:{short_name}",
            version=version,
        )

    @property
    def use_case_id(self) -> str:
        return self.id.split(":", 1)[0]

    @property
    def short_name(self) -> str:
        return self.id.split(":", 1)[1]

    @cached_property
    def path(self) -> Path:
        return path_enum.dir_data.joinpath(
            self.use_case_id,
            "prompts",
            self.short_name,
            f"v{str(self.version).zfill(2)}.md",
        )

    @cached_property
    def content(self) -> str:
        return self.path.read_text(encoding="utf-8")
