PRESENCE_SCORE = 50.0
RANK_WEIGHT = 30.0
UNRANKED_BONUS = 10.0
FREQUENCY_WEIGHT = 20.0
FREQUENCY_CAP = 5
MAX_SCORE = 100.0


def score(mentioned: bool, count: int, rank: int | None) -> float:
    """Visibility score in the 0-100 range.

    - Not mentioned -> 0.
    - Mentioned     -> presence (50) + rank bonus + frequency bonus.
      Rank bonus is 30/rank (rank 1 = 30, rank 2 = 15, ...), or a flat 10
      when the brand is mentioned outside a ranked list.
      Frequency bonus scales up to 20 as occurrences approach the cap.
    """
    if not mentioned:
        return 0.0

    rank_bonus = (RANK_WEIGHT / rank) if rank else UNRANKED_BONUS
    frequency_bonus = min(count, FREQUENCY_CAP) / FREQUENCY_CAP * FREQUENCY_WEIGHT
    total = PRESENCE_SCORE + rank_bonus + frequency_bonus
    return round(min(total, MAX_SCORE), 2)
