import json
from collections import defaultdict
from typing import Any

from src.models.analysis import VisibilityAnalysis
from src.models.llm_response import LLMResponse
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.result_reader import ResultReader
from src.services.bigquery_service import BigQueryService

_RECENT_RUNS_SQL = """\
SELECT *
FROM `{table}`
WHERE run_id IN (
  SELECT run_id
  FROM `{table}`
  GROUP BY run_id
  ORDER BY MAX(executed_at) DESC
  LIMIT @max_runs
)
ORDER BY executed_at DESC
"""

_SINGLE_RUN_SQL = """\
SELECT *
FROM `{table}`
WHERE run_id = @run_id
"""


class BigQueryResultReader(ResultReader):
    """Reads stored prompt runs back from BigQuery.

    Rows are stored one-per-prompt-execution; this reader groups them by
    ``run_id`` and reconstructs :class:`PromptRunResult` objects.
    """

    def __init__(
        self,
        bigquery_service: BigQueryService,
        max_runs: int = 100,
    ) -> None:
        self.bigquery_service = bigquery_service
        self.max_runs = max_runs

    def list_runs(self) -> list[PromptRunResult]:
        rows = self.bigquery_service.query_rows(
            _RECENT_RUNS_SQL,
            {"max_runs": self.max_runs},
        )
        runs = self._group_rows(rows)
        runs.sort(key=lambda run: run.executed_at, reverse=True)
        return runs

    def get_run(self, run_id: str) -> PromptRunResult:
        rows = self.bigquery_service.query_rows(
            _SINGLE_RUN_SQL,
            {"run_id": run_id},
        )
        runs = self._group_rows(rows)
        if not runs:
            raise KeyError(f"Run not found: {run_id}")
        return runs[0]

    @staticmethod
    def _group_rows(rows: list[dict[str, Any]]) -> list[PromptRunResult]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row["run_id"]].append(row)

        runs: list[PromptRunResult] = []
        for run_id, run_rows in grouped.items():
            items = [_row_to_item(row) for row in run_rows]
            success_count = sum(item.success for item in items)
            first = run_rows[0]
            runs.append(
                PromptRunResult(
                    run_id=run_id,
                    provider=first["provider"],
                    executed_at=first["executed_at"],
                    requested_count=len(items),
                    success_count=success_count,
                    failure_count=len(items) - success_count,
                    results=items,
                )
            )
        return runs


def _row_to_item(row: dict[str, Any]) -> PromptRunItem:
    result: LLMResponse | None = None
    if row.get("response") is not None:
        citations_raw = row.get("citations")
        citations = json.loads(citations_raw) if citations_raw else []
        result = LLMResponse(
            provider=row["provider"],
            model=row.get("model") or "",
            prompt=row.get("prompt") or "",
            response=row.get("response") or "",
            input_tokens=row.get("input_tokens") or 0,
            output_tokens=row.get("output_tokens") or 0,
            latency_ms=row.get("latency_ms") or 0,
            citations=citations,
        )

    analysis: VisibilityAnalysis | None = None
    analysis_raw = row.get("analysis")
    if analysis_raw:
        analysis = VisibilityAnalysis.model_validate_json(analysis_raw)

    return PromptRunItem(
        prompt_id=row["prompt_id"],
        success=bool(row["success"]),
        result=result,
        analysis=analysis,
        error=row.get("error"),
    )
