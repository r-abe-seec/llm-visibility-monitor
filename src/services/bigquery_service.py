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