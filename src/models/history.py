from datetime import datetime

from pydantic import BaseModel


class RunSummary(BaseModel):
    run_id: str
    provider: str
    executed_at: datetime
    requested_count: int
    success_count: int
    failure_count: int
    target_score: float | None = None


class VisibilityPoint(BaseModel):
    run_id: str
    provider: str
    executed_at: datetime
    mentioned: bool
    rank: int | None = None
    visibility_score: float


class BrandComparison(BaseModel):
    brand: str
    is_target: bool
    runs_analyzed: int
    mention_rate: float
    average_score: float
    best_rank: int | None = None
    average_rank: float | None = None


class ComparisonReport(BaseModel):
    runs_analyzed: int
    providers: list[str]
    brands: list[BrandComparison]
