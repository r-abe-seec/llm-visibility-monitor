from src.repositories.console_result_repository import (
    ConsoleResultRepository,
)
from src.repositories.json_result_repository import (
    JsonResultRepository,
)
from src.repositories.result_repository import ResultRepository


class RepositoryFactory:
    @staticmethod
    def create(repository_type: str) -> ResultRepository:
        match repository_type:
            case "console":
                return ConsoleResultRepository()

            case "json":
                return JsonResultRepository()

            case _:
                raise ValueError(
                    f"Unsupported repository: {repository_type}"
                )