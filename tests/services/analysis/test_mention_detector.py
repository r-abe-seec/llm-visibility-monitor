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


def test_find_rank_bold_numbered_list():
    text = "**1. イオンのお葬式**\n- 特徴の説明\n\n**2. 公益社**\n- 説明"
    assert md.find_rank(text, ["公益社"]) == 2
    assert md.find_rank(text, ["イオンのお葬式"]) == 1


def test_find_rank_heading_numbered():
    text = "## 1. 電通\n説明\n## 2. 博報堂"
    assert md.find_rank(text, ["博報堂"]) == 2


def test_find_rank_markdown_table_skips_header_and_separator():
    text = (
        "| 会社名 | 特徴 |\n"
        "|---|---|\n"
        "| 小さなお葬式 | 低価格 |\n"
        "| よりそうのお葬式 | ネット完結 |\n"
        "| イオンのお葬式 | 大手流通系 |"
    )
    assert md.find_rank(text, ["小さなお葬式"]) == 1
    assert md.find_rank(text, ["よりそうのお葬式"]) == 2
    assert md.find_rank(text, ["イオンのお葬式"]) == 3
    # header row is not ranked
    assert md.find_rank(text, ["会社名"]) is None


def test_find_rank_two_separate_tables_reset_counter():
    text = "| A | x |\n|---|---|\n| 電通 | y |\n\n| B | x |\n|---|---|\n| 博報堂 | y |"
    assert md.find_rank(text, ["電通"]) == 1
    assert md.find_rank(text, ["博報堂"]) == 1


def test_plain_bullets_still_work_after_table():
    text = "| H | x |\n|---|---|\n| 電通 | y |\n\n- 博報堂\n- ADK"
    assert md.find_rank(text, ["ADK"]) == 2
