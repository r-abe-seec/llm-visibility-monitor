import json
from datetime import UTC, datetime
from uuid import uuid4

from src.models.prompt_run import PromptRunResult
from src.repositories.result_repository import ResultRepository
from src.services.bigquery_service import BigQueryService


class BigQueryResultRepository(ResultRepository):
    def __init__(self, bigquery_service: BigQueryService) -> None:
        self.bigquery_service = bigquery_service

    def save(self, run_result: PromptRunResult) -> None:
        inserted_at = datetime.now(UTC)

        rows = []

        for item in run_result.results:
            result = item.result

            rows.append(
                {
                    "result_id": str(uuid4()),
                    "run_id": run_result.run_id,
                    "executed_at": run_result.executed_at.isoformat(),
                    "inserted_at": inserted_at.isoformat(),
                    "provider": run_result.provider,
                    "model": result.model if result else None,
                    "prompt_id": item.prompt_id,
                    "prompt": result.prompt if result else None,
                    "response": result.response if result else None,
                    "success": item.success,
                    "error": item.error,
                    "input_tokens": result.input_tokens if result else None,
                    "output_tokens": result.output_tokens if result else None,
                    "latency_ms": result.latency_ms if result else None,
                    "metadata": json.dumps({}, ensure_ascii=False),
                }
            )

        self.bigquery_service.insert_rows(rows)
