import json
from datetime import UTC, datetime
from typing import Any

import pytest

from src.repositories.bigquery_result_reader import BigQueryResultReader
from src.services.bigquery_service import BigQueryService


class _FakeBigQueryService(BigQueryService):
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.queries: list[tuple[str, dict[str, Any] | None]] = []

    def query_rows(self, sql, parameters=None):
        self.queries.append((sql, parameters))
        run_id = (parameters or {}).get("run_id")
        if run_id is not None:
            return [row for row in self.rows if row["run_id"] == run_id]
        return self.rows


def _row(run_id, prompt_id, when, provider="openai", **overrides):
    analysis = {
        "brands": [
            {
                "brand": "電通",
                "is_target": True,
                "mentioned": True,
                "count": 1,
                "first_position": 0,
                "rank": 1,
                "visibility_score": 84.0,
                "sentiment": "positive",
            }
        ],
        "target_score": 84.0,
        "share_of_voice": 1.0,
    }
    row = {
        "result_id": f"{run_id}-{prompt_id}",
        "run_id": run_id,
        "executed_at": when,
        "provider": provider,
        "model": "gpt-test",
        "prompt_id": prompt_id,
        "prompt": "質問",
        "response": "電通が1位です。",
        "success": True,
        "error": None,
        "input_tokens": 10,
        "output_tokens": 5,
        "latency_ms": 120,
        "citations": json.dumps(["https://example.com/a"]),
        "analysis": json.dumps(analysis, ensure_ascii=False),
    }
    row.update(overrides)
    return row


def test_list_runs_groups_rows_by_run_id():
    old = datetime(2026, 7, 1, tzinfo=UTC)
    new = datetime(2026, 7, 30, tzinfo=UTC)
    service = _FakeBigQueryService(
        [
            _row("r-new", "p1", new),
            _row("r-new", "p2", new),
            _row("r-old", "p1", old),
        ]
    )
    reader = BigQueryResultReader(service)

    runs = reader.list_runs()

    assert [run.run_id for run in runs] == ["r-new", "r-old"]
    assert runs[0].requested_count == 2
    assert runs[0].success_count == 2
    assert runs[0].failure_count == 0


def test_row_reconstruction_includes_result_and_analysis():
    service = _FakeBigQueryService(
        [_row("r1", "p1", datetime(2026, 7, 30, tzinfo=UTC))]
    )
    run = BigQueryResultReader(service).list_runs()[0]
    item = run.results[0]

    assert item.result is not None
    assert item.result.citations == ["https://example.com/a"]
    assert item.analysis is not None
    assert item.analysis.target_score == 84.0
    assert item.analysis.brands[0].sentiment == "positive"


def test_failed_row_has_no_result():
    row = _row(
        "r1",
        "p1",
        datetime(2026, 7, 30, tzinfo=UTC),
        response=None,
        success=False,
        error="RuntimeError: boom",
        analysis=None,
        citations=None,
    )
    run = BigQueryResultReader(_FakeBigQueryService([row])).list_runs()[0]
    item = run.results[0]

    assert item.success is False
    assert item.result is None
    assert item.analysis is None
    assert item.error == "RuntimeError: boom"


def test_get_run_returns_match_and_raises_when_missing():
    when = datetime(2026, 7, 30, tzinfo=UTC)
    reader = BigQueryResultReader(_FakeBigQueryService([_row("r1", "p1", when)]))

    assert reader.get_run("r1").run_id == "r1"
    with pytest.raises(KeyError):
        reader.get_run("nope")


def test_max_runs_passed_to_query():
    service = _FakeBigQueryService([])
    BigQueryResultReader(service, max_runs=7).list_runs()
    _, parameters = service.queries[0]
    assert parameters == {"max_runs": 7}
