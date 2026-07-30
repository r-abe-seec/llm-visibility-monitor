from pathlib import Path
from typing import Any

import yaml

from src.models.prompt import Prompt


class PromptService:
    def __init__(self, file_path: str | Path = "prompts/prompts.yaml") -> None:
        self.file_path = Path(file_path)

    def load_all(self) -> list[Prompt]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.file_path}")

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data: Any = yaml.safe_load(file)

        if not data or "prompts" not in data:
            return []

        return [Prompt.model_validate(prompt_data) for prompt_data in data["prompts"]]

    def get(self, prompt_id: str) -> Prompt:
        for prompt in self.load_all():
            if prompt.id == prompt_id:
                return prompt

        raise KeyError(f"Prompt not found: {prompt_id}")

    def append(self, prompts: list[Prompt]) -> None:
        """Append prompts to the YAML file, keeping existing entries."""
        existing: list[dict[str, str]] = []
        if self.file_path.exists():
            with self.file_path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
            existing = list(data.get("prompts") or [])

        existing.extend(prompt.model_dump() for prompt in prompts)

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(
                {"prompts": existing},
                file,
                allow_unicode=True,
                sort_keys=False,
            )
