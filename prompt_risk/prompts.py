# -*- coding: utf-8 -*-

import dataclasses
from pathlib import Path
from functools import cached_property

import jinja2

from .paths import path_enum


@dataclasses.dataclass
class Prompt:
    """A versioned prompt resolved from ``{use_case_id}/{short_name}/v{NN}.md``."""

    id: str
    version: str

    @classmethod
    def from_use_case(
        cls,
        use_case_id: str,
        short_name: str,
        version: str,
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
            self.use_case_id, "prompts", self.short_name, "versions", self.version
        )

    @cached_property
    def path_system_prompt(self) -> Path:
        return self.path.joinpath("system-prompt.jinja")

    @cached_property
    def path_user_prompt(self) -> Path:
        return self.path.joinpath("user-prompt.jinja")

    @cached_property
    def system_prompt_content(self) -> str:
        return self.path_system_prompt.read_text(encoding="utf-8")

    @cached_property
    def user_prompt_content(self) -> str:
        return self.path_user_prompt.read_text(encoding="utf-8")

    @cached_property
    def system_prompt_template(self) -> jinja2.Template:
        return jinja2.Template(self.system_prompt_content)

    @cached_property
    def user_prompt_template(self) -> jinja2.Template:
        return jinja2.Template(self.user_prompt_content)
