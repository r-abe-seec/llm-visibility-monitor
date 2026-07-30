from src.services.analysis import mention_detector as md


def test_count_occurrences_case_insensitive():
    text = "Dentsu is great. dentsu again. DENTSU!"
    assert md.count_occurrences(text, "dentsu") == 3


def test_count_occurrences_missing_term():
    assert md.count_occurrences("no brand here", "電通") == 0


def test_first_position_returns_earliest():
    text = "prefix 博報堂 then 電通"
    assert md.first_position(text, ["電通", "博報堂"]) == text.index("博報堂")


def test_first_position_none_when_absent():
    assert md.first_position("nothing", ["電通"]) is None


def test_find_rank_numbered_list():
    text = "1. 博報堂\n2. 電通\n3. ADK"
    assert md.find_rank(text, ["電通"]) == 2


def test_find_rank_japanese_numbering():
    text = "1位 電通\n2位 博報堂"
    assert md.find_rank(text, ["博報堂"]) == 2


def test_find_rank_bullet_list_uses_running_counter():
    text = "- 電通\n- 博報堂"
    assert md.find_rank(text, ["博報堂"]) == 2


def test_find_rank_none_when_not_in_list():
    text = "電通は日本最大の広告代理店です。"
    assert md.find_rank(text, ["電通"]) is None
