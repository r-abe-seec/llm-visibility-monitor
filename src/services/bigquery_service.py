from collections.abc import Sequence
from typing import Any

from google.cloud import bigquery


class BigQueryInsertError(RuntimeError):
    """Raised when BigQuery fails to insert one or more rows."""


class BigQueryService:
    def __init__(
        self,
        project_id: str,
        dataset: str,
        table: str,
        client: bigquery.Client | None = None,
    ) -> None:
        if not project_id:
            raise ValueError("project_id is required")
        if not dataset:
            raise ValueError("dataset is required")
        if not table:
            raise ValueError("table is required")

        self.client = client or bigquery.Client(project=project_id)
        self.table_id = f"{project_id}.{dataset}.{table}"

    def insert_rows(
        self,
        rows: Sequence[dict[str, Any]],
    ) -> None:
        if not rows:
            return

        errors = self.client.insert_rows_json(
            self.table_id,
            list(rows),
        )

        if errors:
            raise BigQueryInsertError(
                f"Failed to insert rows into {self.table_id}: {errors}"
            )

    def query_rows(
        self,
        sql: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a parameterized query and return rows as dictionaries.

        ``sql`` may reference the configured table as ``{table}``.
        """
        query_parameters = [
            bigquery.ScalarQueryParameter(name, _bq_type(value), value)
            for name, value in (parameters or {}).items()
        ]
        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)

        job = self.client.query(
            sql.format(table=self.table_id),
            job_config=job_config,
        )
        return [dict(row) for row in job.result()]


def _bq_type(value: Any) -> str:
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    return "STRING"
