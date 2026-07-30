from src.models.prompt_run import PromptRunResult
from src.repositories.result_repository import ResultRepository


class ConsoleResultRepository(ResultRepository):
    def save(
        self,
        result: PromptRunResult,
    ) -> None:
        print(result.model_dump_json(indent=2))
