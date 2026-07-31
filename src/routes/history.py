from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src.factories.reader_factory import build_result_reader
from src.models.history import ComparisonReport, RunSummary, VisibilityPoint
from src.models.prompt_run import PromptRunResult
from src.repositories.result_reader import ResultReader
from src.services.analysis.comparison import build_comparison_report

router = APIRouter(prefix="/history", tags=["history"])


def get_reader() -> ResultReader:
    return build_result_reader()


ReaderDep = Annotated[ResultReader, Depends(get_reader)]


def _target_score(run: PromptRunResult) -> float | None:
    scores = [item.analysis.target_score for item in run.results if item.analysis]
    return max(scores) if scores else None


@router.get("/runs", response_model=list[RunSummary])
def list_runs(reader: ReaderDep) -> list[RunSummary]:
    return [
        RunSummary(
            run_id=run.run_id,
            provider=run.provider,
            executed_at=run.executed_at,
            requested_count=run.requested_count,
            success_count=run.success_count,
            failure_count=run.failure_count,
            target_score=_target_score(run),
        )
        for run in reader.list_runs()
    ]


@router.get("/runs/{run_id}", response_model=PromptRunResult)
def get_run(
    run_id: str,
    reader: ReaderDep,
) -> PromptRunResult:
    try:
        return reader.get_run(run_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/visibility", response_model=list[VisibilityPoint])
def visibility(
    reader: ReaderDep,
    brand: Annotated[str, Query(min_length=1)],
) -> list[VisibilityPoint]:
    """Time series of a brand's visibility across stored runs (oldest first)."""
    points: list[VisibilityPoint] = []

    for run in reader.list_runs():
        scores: list[float] = []
        mentioned = False
        best_rank: int | None = None

        for item in run.results:
            if not item.analysis:
                continue
            for mention in item.analysis.brands:
                if mention.brand != brand:
                    continue
                scores.append(mention.visibility_score)
                mentioned = mentioned or mention.mentioned
                if mention.rank is not None and (
                    best_rank is None or mention.rank < best_rank
                ):
                    best_rank = mention.rank

        if scores:
            points.append(
                VisibilityPoint(
                    run_id=run.run_id,
                    provider=run.provider,
                    executed_at=run.executed_at,
                    mentioned=mentioned,
                    rank=best_rank,
                    visibility_score=max(scores),
                )
            )

    points.sort(key=lambda point: point.executed_at)
    return points


@router.get("/comparison", response_model=ComparisonReport)
def comparison(
    reader: ReaderDep,
    provider: Annotated[str | None, Query()] = None,
) -> ComparisonReport:
    """Compare target vs competitor visibility across stored runs."""
    return build_comparison_report(reader.list_runs(), provider=provider)
