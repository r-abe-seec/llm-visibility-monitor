from abc import ABC, abstractmethod

from src.models.prompt_run import PromptRunResult


class ResultReader(ABC):
    @abstractmethod
    def list_runs(self) -> list[PromptRunResult]:
        """Return stored runs, newest first."""

    @abstractmethod
    def get_run(self, run_id: str) -> PromptRunResult:
        """Return a single run by id, or raise KeyError if not found."""
