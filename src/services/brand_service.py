from pathlib import Path
from typing import Any

import yaml

from src.models.brand import Brand


class BrandService:
    def __init__(self, file_path: str | Path = "prompts/brands.yaml") -> None:
        self.file_path = Path(file_path)

    def load_all(self) -> list[Brand]:
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as file:
            data: Any = yaml.safe_load(file)

        if not data or "brands" not in data:
            return []

        return [Brand.model_validate(item) for item in data["brands"]]
