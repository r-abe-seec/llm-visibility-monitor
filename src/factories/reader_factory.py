from src.config import settings
from src.repositories.bigquery_result_reader import BigQueryResultReader
from src.repositories.json_result_reader import JsonResultReader
from src.repositories.result_reader import ResultReader
from src.services.bigquery_service import BigQueryService


def build_result_reader() -> ResultReader:
    """Reader matching the configured result repository.

    ``bigquery`` reads history back from BigQuery; every other repository
    falls back to the local JSON store.
    """
    if settings.result_repository == "bigquery":
        if settings.gcp_project_id is None:
            raise ValueError(
                "GCP_PROJECT_ID is required when using the BigQuery reader"
            )
        if settings.bigquery_dataset is None:
            raise ValueError(
                "BIGQUERY_DATASET is required when using the BigQuery reader"
            )

        service = BigQueryService(
            project_id=settings.gcp_project_id,
            dataset=settings.bigquery_dataset,
            table=settings.bigquery_table,
        )
        return BigQueryResultReader(service, max_runs=settings.history_max_runs)

    return JsonResultReader(settings.results_dir)
