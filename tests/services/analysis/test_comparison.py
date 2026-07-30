from datetime import UTC, datetime

from src.models.analysis import BrandMention, VisibilityAnalysis
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.services.analysis.comparison import build_comparison_report


def _mention(brand, is_target, mentioned, score, rank=None):
    return BrandMention(
        brand=brand,
        is_target=is_target,
        mentioned=mentioned,
        count=1 if mentioned else 0,
        rank=rank,
        visibility_score=score,
    )


def _run(run_id, provider, mentions, when=None):
    analysis = VisibilityAnalysis(
        brands=mentions,
        target_score=max(
            (m.visibility_score for m in mentions if m.is_target), default=0.0
        ),
        share_of_voice=0.5,
    )
    return PromptRunResult(
        run_id=run_id,
        provider=provider,
        executed_at=when or datetime(2026, 1, 1, tzinfo=UTC),
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[PromptRunItem(prompt_id="p1", success=True, analysis=analysis)],
    )


RUNS = [
    _run(
        "r1",
        "openai",
        [
            _mention("電通", True, True, 100.0, rank=1),
            _mention("博報堂", False, True, 69.0, rank=2),
        ],
    ),
    _run(
        "r2",
        "gemini",
        [
            _mention("電通", True, True, 68.0),
            _mention("博報堂", False, False, 0.0),
        ],
    ),
]


def test_report_aggregates_across_runs():
    report = build_comparison_report(RUNS)

    assert report.runs_analyzed == 2
    assert report.providers == ["gemini", "openai"]

    by_name = {b.brand: b for b in report.brands}
    dentsu = by_name["電通"]
    assert dentsu.is_target is True
    assert dentsu.mention_rate == 1.0
    assert dentsu.average_score == 84.0
    assert dentsu.best_rank == 1

    hakuhodo = by_name["博報堂"]
    assert hakuhodo.mention_rate == 0.5
    assert hakuhodo.average_score == 34.5
    assert hakuhodo.average_rank == 2.0


def test_brands_sorted_by_average_score_desc():
    report = build_comparison_report(RUNS)
    assert [b.brand for b in report.brands] == ["電通", "博報堂"]


def test_provider_filter():
    report = build_comparison_report(RUNS, provider="openai")
    assert report.runs_analyzed == 1
    assert report.providers == ["openai"]
    assert {b.brand: b.average_score for b in report.brands} == {
        "電通": 100.0,
        "博報堂": 69.0,
    }


def test_runs_without_analysis_are_skipped():
    bare = PromptRunResult(
        run_id="r3",
        provider="openai",
        executed_at=datetime(2026, 1, 2, tzinfo=UTC),
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[PromptRunItem(prompt_id="p1", success=True)],
    )
    report = build_comparison_report([bare])
    assert report.runs_analyzed == 0
    assert report.brands == []
