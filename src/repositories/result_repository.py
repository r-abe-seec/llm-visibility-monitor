from abc import ABC, abstractmethod

from src.models.prompt_run import PromptRunResult


class ResultRepository(ABC):
    @abstractmethod
    def save(
        self,
        result: PromptRunResult,
    ) -> None:
        """Persist a prompt run result."""
