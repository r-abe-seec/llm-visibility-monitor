from pathlib import Path

from src.models.prompt_run import PromptRunResult
from src.repositories.result_repository import ResultRepository


class JsonResultRepository(ResultRepository):
    def __init__(
        self,
        output_dir: str | Path = "data/results",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        result: PromptRunResult,
    ) -> None:
        output_path = self.output_dir / f"{result.run_id}.json"

        output_path.write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )