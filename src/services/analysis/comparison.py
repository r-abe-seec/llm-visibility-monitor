from collections import defaultdict

from src.models.history import BrandComparison, ComparisonReport
from src.models.prompt_run import PromptRunResult


def build_comparison_report(
    runs: list[PromptRunResult],
    provider: str | None = None,
) -> ComparisonReport:
    """Aggregate per-brand visibility across stored runs.

    For each run, a brand's contribution is its best mention across the
    run's prompt items (max score, best rank). Rates and averages are
    then computed over the analyzed runs.
    """
    if provider:
        runs = [run for run in runs if run.provider == provider]

    runs = [run for run in runs if any(item.analysis for item in run.results)]

    scores: dict[str, list[float]] = defaultdict(list)
    sentiments: dict[str, list[str]] = defaultdict(list)
    ranks: dict[str, list[int]] = defaultdict(list)
    mentions: dict[str, int] = defaultdict(int)
    appearances: dict[str, int] = defaultdict(int)
    is_target: dict[str, bool] = {}
    providers: set[str] = set()

    for run in runs:
        providers.add(run.provider)
        run_score: dict[str, float] = {}
        run_rank: dict[str, int] = {}
        run_mentioned: dict[str, bool] = {}

        for item in run.results:
            if not item.analysis:
                continue
            for mention in item.analysis.brands:
                name = mention.brand
                is_target[name] = mention.is_target
                run_score[name] = max(
                    run_score.get(name, 0.0), mention.visibility_score
                )
                run_mentioned[name] = (
                    run_mentioned.get(name, False) or mention.mentioned
                )
                if mention.rank is not None and (
                    name not in run_rank or mention.rank < run_rank[name]
                ):
                    run_rank[name] = mention.rank
                if mention.sentiment is not None:
                    sentiments[name].append(mention.sentiment)

        for name, score in run_score.items():
            appearances[name] += 1
            scores[name].append(score)
            if run_mentioned.get(name):
                mentions[name] += 1
            if name in run_rank:
                ranks[name].append(run_rank[name])

    brands = [
        BrandComparison(
            brand=name,
            is_target=is_target[name],
            runs_analyzed=appearances[name],
            mention_rate=round(mentions[name] / appearances[name], 4),
            average_score=round(sum(scores[name]) / len(scores[name]), 2),
            best_rank=min(ranks[name]) if ranks[name] else None,
            average_rank=(
                round(sum(ranks[name]) / len(ranks[name]), 2) if ranks[name] else None
            ),
            positive_rate=(
                round(sentiments[name].count("positive") / len(sentiments[name]), 4)
                if sentiments[name]
                else None
            ),
        )
        for name in sorted(
            appearances,
            key=lambda n: sum(scores[n]) / len(scores[n]),
            reverse=True,
        )
    ]

    return ComparisonReport(
        runs_analyzed=len(runs),
        providers=sorted(providers),
        brands=brands,
    )
