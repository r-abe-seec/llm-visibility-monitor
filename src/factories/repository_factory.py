from src.config import settings
from src.repositories.bigquery_result_repository import (
    BigQueryResultRepository,
)
from src.repositories.console_result_repository import (
    ConsoleResultRepository,
)
from src.repositories.json_result_repository import (
    JsonResultRepository,
)
from src.repositories.result_repository import ResultRepository
from src.services.bigquery_service import BigQueryService


class RepositoryFactory:
    @staticmethod
    def create(repository_type: str) -> ResultRepository:
        match repository_type:
            case "console":
                return ConsoleResultRepository()

            case "json":
                return JsonResultRepository(settings.results_dir)

            case "bigquery":
                if settings.gcp_project_id is None:
                    raise ValueError(
                        "GCP_PROJECT_ID is required when using the BigQuery repository"
                    )

                if settings.bigquery_dataset is None:
                    raise ValueError(
                        "BIGQUERY_DATASET is required when using "
                        "the BigQuery repository"
                    )

                service = BigQueryService(
                    project_id=settings.gcp_project_id,
                    dataset=settings.bigquery_dataset,
                    table=settings.bigquery_table,
                )
                return BigQueryResultRepository(service)

            case _:
                raise ValueError(f"Unsupported repository: {repository_type}")
