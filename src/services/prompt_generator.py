import re
from pathlib import Path
from typing import Any

import yaml

from src.models.prompt import Prompt


class PromptGenerator:
    """Generates visibility-measurement prompts from category templates."""

    def __init__(
        self,
        templates_path: str | Path = "prompts/templates.yaml",
    ) -> None:
        self.templates_path = Path(templates_path)

    def load_templates(self) -> list[dict[str, str]]:
        if not self.templates_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.templates_path}")

        with self.templates_path.open("r", encoding="utf-8") as file:
            data: Any = yaml.safe_load(file)

        if not data or "templates" not in data:
            return []

        return list(data["templates"])

    def generate(
        self,
        industry: str,
        target: str | None = None,
        categories: list[str] | None = None,
        existing_ids: set[str] | None = None,
    ) -> list[Prompt]:
        """Fill templates with the given industry / target brand.

        Templates that require ``{target}`` are skipped when no target is
        provided. Generated ids are made unique against ``existing_ids``.
        """
        taken = set(existing_ids or set())
        prompts: list[Prompt] = []

        for template in self.load_templates():
            category = template["category"]
            if categories and category not in categories:
                continue

            text = template["text"]
            if "{target}" in text and not target:
                continue

            filled = text.format(industry=industry, target=target or "")
            prompt_id = self._unique_id(f"gen_{category}", taken)
            taken.add(prompt_id)

            prompts.append(
                Prompt(
                    id=prompt_id,
                    category=category,
                    title=template.get("title", category),
                    text=filled,
                )
            )

        return prompts

    @staticmethod
    def _unique_id(base: str, taken: set[str]) -> str:
        slug = re.sub(r"[^a-z0-9_]+", "_", base.lower())
        if slug not in taken:
            return slug
        index = 2
        while f"{slug}_{index}" in taken:
            index += 1
        return f"{slug}_{index}"
