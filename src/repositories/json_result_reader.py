from pathlib import Path

from src.models.prompt_run import PromptRunResult
from src.repositories.result_reader import ResultReader


class JsonResultReader(ResultReader):
    def __init__(self, results_dir: str | Path = "data/results") -> None:
        self.results_dir = Path(results_dir)

    def list_runs(self) -> list[PromptRunResult]:
        if not self.results_dir.exists():
            return []

        runs = [
            PromptRunResult.model_validate_json(path.read_text(encoding="utf-8"))
            for path in self.results_dir.glob("*.json")
        ]
        runs.sort(key=lambda run: run.executed_at, reverse=True)
        return runs

    def get_run(self, run_id: str) -> PromptRunResult:
        path = self.results_dir / f"{run_id}.json"
        if not path.exists():
            raise KeyError(f"Run not found: {run_id}")

        return PromptRunResult.model_validate_json(path.read_text(encoding="utf-8"))
