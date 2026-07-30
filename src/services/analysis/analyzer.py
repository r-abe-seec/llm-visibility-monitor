from src.models.analysis import BrandMention, VisibilityAnalysis
from src.models.brand import Brand
from src.services.analysis import mention_detector as detector
from src.services.analysis import visibility_scorer as scorer


def analyze_visibility(text: str, brands: list[Brand]) -> VisibilityAnalysis:
    """Detect brand mentions in an LLM response and score visibility."""
    mentions: list[BrandMention] = []
    total_count = 0
    target_count = 0
    target_score = 0.0

    for brand in brands:
        terms = brand.terms()
        count = sum(detector.count_occurrences(text, term) for term in terms)
        mentioned = count > 0
        position = detector.first_position(text, terms) if mentioned else None
        rank = detector.find_rank(text, terms) if mentioned else None
        visibility = scorer.score(mentioned, count, rank)

        mentions.append(
            BrandMention(
                brand=brand.name,
                is_target=brand.is_target,
                mentioned=mentioned,
                count=count,
                first_position=position,
                rank=rank,
                visibility_score=visibility,
            )
        )

        total_count += count
        if brand.is_target:
            target_count += count
            target_score = max(target_score, visibility)

    share_of_voice = round(target_count / total_count, 4) if total_count else 0.0

    return VisibilityAnalysis(
        brands=mentions,
        target_score=target_score,
        share_of_voice=share_of_voice,
    )
