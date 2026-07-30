import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

from src.models.llm_response import LLMResponse
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.bigquery_result_repository import (
    BigQueryResultRepository,
)


def test_save_maps_successful_result_to_bigquery_row() -> None:
    bigquery_service = MagicMock()
    repository = BigQueryResultRepository(bigquery_service)

    executed_at = datetime(
        2026,
        7,
        30,
        12,
        0,
        0,
        tzinfo=UTC,
    )

    run_result = PromptRunResult(
        run_id="run-123",
        provider="openai",
        executed_at=executed_at,
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[
            PromptRunItem(
                prompt_id="prompt-1",
                success=True,
                result=LLMResponse(
                    provider="openai",
                    model="gpt-test",
                    prompt="What is OpenAI?",
                    response="OpenAI is an AI research company.",
                    input_tokens=10,
                    output_tokens=20,
                    latency_ms=150,
                ),
                error=None,
            )
        ],
    )

    repository.save(run_result)

    bigquery_service.insert_rows.assert_called_once()

    rows = bigquery_service.insert_rows.call_args.args[0]

    assert len(rows) == 1

    row = rows[0]

    assert row["run_id"] == "run-123"
    assert row["executed_at"] == executed_at.isoformat()
    assert row["provider"] == "openai"
    assert row["model"] == "gpt-test"
    assert row["prompt_id"] == "prompt-1"
    assert row["prompt"] == "What is OpenAI?"
    assert row["response"] == "OpenAI is an AI research company."
    assert row["success"] is True
    assert row["error"] is None
    assert row["input_tokens"] == 10
    assert row["output_tokens"] == 20
    assert row["latency_ms"] == 150
    assert json.loads(row["metadata"]) == {}

    assert isinstance(row["result_id"], str)
    assert row["result_id"]

    inserted_at = datetime.fromisoformat(row["inserted_at"])

    assert inserted_at.tzinfo is not None


def test_save_maps_failed_result_to_bigquery_row() -> None:
    bigquery_service = MagicMock()
    repository = BigQueryResultRepository(bigquery_service)

    run_result = PromptRunResult(
        run_id="run-456",
        provider="anthropic",
        executed_at=datetime(
            2026,
            7,
            30,
            12,
            0,
            0,
            tzinfo=UTC,
        ),
        requested_count=1,
        success_count=0,
        failure_count=1,
        results=[
            PromptRunItem(
                prompt_id="prompt-2",
                success=False,
                result=None,
                error="Provider request failed",
            )
        ],
    )

    repository.save(run_result)

    rows = bigquery_service.insert_rows.call_args.args[0]

    assert len(rows) == 1

    row = rows[0]

    assert row["run_id"] == "run-456"
    assert row["provider"] == "anthropic"
    assert row["prompt_id"] == "prompt-2"
    assert row["success"] is False
    assert row["error"] == "Provider request failed"
    assert row["model"] is None
    assert row["prompt"] is None
    assert row["response"] is None
    assert row["input_tokens"] is None
    assert row["output_tokens"] is None
    assert row["latency_ms"] is None
    assert json.loads(row["metadata"]) == {}


def test_save_inserts_one_row_for_each_result() -> None:
    bigquery_service = MagicMock()
    repository = BigQueryResultRepository(bigquery_service)

    run_result = PromptRunResult(
        run_id="run-789",
        provider="openai",
        executed_at=datetime(
            2026,
            7,
            30,
            12,
            0,
            0,
            tzinfo=UTC,
        ),
        requested_count=2,
        success_count=1,
        failure_count=1,
        results=[
            PromptRunItem(
                prompt_id="prompt-1",
                success=True,
                result=LLMResponse(
                    provider="openai",
                    model="gpt-test",
                    prompt="Prompt 1",
                    response="Response 1",
                    input_tokens=5,
                    output_tokens=10,
                    latency_ms=100,
                ),
                error=None,
            ),
            PromptRunItem(
                prompt_id="prompt-2",
                success=False,
                result=None,
                error="Request failed",
            ),
        ],
    )

    repository.save(run_result)

    bigquery_service.insert_rows.assert_called_once()

    rows = bigquery_service.insert_rows.call_args.args[0]

    assert len(rows) == 2
    assert rows[0]["prompt_id"] == "prompt-1"
    assert rows[1]["prompt_id"] == "prompt-2"
