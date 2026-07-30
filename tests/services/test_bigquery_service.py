from unittest.mock import MagicMock

import pytest

from src.services.bigquery_service import (
    BigQueryInsertError,
    BigQueryService,
)


def test_insert_rows_calls_bigquery_client() -> None:
    client = MagicMock()
    client.insert_rows_json.return_value = []

    service = BigQueryService(
        project_id="test-project",
        dataset="test_dataset",
        table="test_table",
        client=client,
    )

    rows = [
        {
            "run_id": "run-1",
            "provider": "openai",
        }
    ]

    service.insert_rows(rows)

    client.insert_rows_json.assert_called_once_with(
        "test-project.test_dataset.test_table",
        rows,
    )


def test_insert_rows_does_not_call_client_when_rows_are_empty() -> None:
    client = MagicMock()

    service = BigQueryService(
        project_id="test-project",
        dataset="test_dataset",
        table="test_table",
        client=client,
    )

    service.insert_rows([])

    client.insert_rows_json.assert_not_called()


def test_insert_rows_raises_error_when_bigquery_returns_errors() -> None:
    client = MagicMock()
    client.insert_rows_json.return_value = [
        {
            "index": 0,
            "errors": [
                {
                    "reason": "invalid",
                    "message": "Invalid row",
                }
            ],
        }
    ]

    service = BigQueryService(
        project_id="test-project",
        dataset="test_dataset",
        table="test_table",
        client=client,
    )

    with pytest.raises(
        BigQueryInsertError,
        match="Failed to insert rows into "
        "test-project.test_dataset.test_table",
    ):
        service.insert_rows([{"run_id": "run-1"}])