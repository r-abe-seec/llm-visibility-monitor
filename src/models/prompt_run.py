from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from src.models.analysis import VisibilityAnalysis
from src.models.llm_response import LLMResponse


class PromptRunRequest(BaseModel):
    provider: str = Field(min_length=1)
    prompt_ids: list[str] = Field(min_length=1)


class PromptRunItem(BaseModel):
    prompt_id: str
    success: bool
    result: LLMResponse | None = None
    analysis: VisibilityAnalysis | None = None
    error: str | None = None


class PromptRunResult(BaseModel):
    run_id: str
    provider: str
    executed_at: datetime
    requested_count: int
    success_count: int
    failure_count: int
    results: list[PromptRunItem]

    @classmethod
    def create(
        cls,
        provider: str,
        results: list[PromptRunItem],
    ) -> "PromptRunResult":
        success_count = sum(item.success for item in results)

        return cls(
            run_id=str(uuid4()),
            provider=provider,
            executed_at=datetime.now(UTC),
            requested_count=len(results),
            success_count=success_count,
            failure_count=len(results) - success_count,
            results=results,
        )
