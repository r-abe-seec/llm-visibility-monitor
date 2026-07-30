from src.services.analysis import visibility_scorer as scorer


def test_not_mentioned_is_zero():
    assert scorer.score(False, 0, None) == 0.0


def test_rank_one_high_frequency_is_max():
    assert scorer.score(True, 5, 1) == 100.0


def test_rank_two_reduces_score():
    # 50 presence + 15 rank + (1/5*20=4) freq = 69
    assert scorer.score(True, 1, 2) == 69.0


def test_mentioned_without_rank_uses_flat_bonus():
    # 50 + 10 + (2/5*20=8) = 68
    assert scorer.score(True, 2, None) == 68.0


def test_score_never_exceeds_max():
    assert scorer.score(True, 100, 1) == 100.0
