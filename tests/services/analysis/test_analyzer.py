from src.models.brand import Brand
from src.services.analysis.analyzer import analyze_visibility

BRANDS = [
    Brand(name="電通", aliases=["Dentsu"], is_target=True),
    Brand(name="博報堂", aliases=["Hakuhodo"]),
    Brand(name="ADK"),
]


def test_analyze_detects_target_and_competitor():
    text = "1. 電通\n2. 博報堂\n電通は最大手です。"
    result = analyze_visibility(text, BRANDS)

    by_name = {m.brand: m for m in result.brands}
    assert by_name["電通"].mentioned is True
    assert by_name["電通"].rank == 1
    assert by_name["電通"].count == 2
    assert by_name["博報堂"].mentioned is True
    assert by_name["ADK"].mentioned is False
    assert by_name["ADK"].visibility_score == 0.0


def test_target_score_and_share_of_voice():
    text = "1. 電通 Dentsu\n2. 博報堂"
    result = analyze_visibility(text, BRANDS)
    # target (電通) appears twice (name + alias), 博報堂 once -> SoV 2/3
    assert result.share_of_voice == round(2 / 3, 4)
    assert result.target_score == result.brands[0].visibility_score
    assert result.target_score > 0


def test_no_brands_all_zero_share():
    result = analyze_visibility("no brands mentioned", BRANDS)
    assert result.share_of_voice == 0.0
    assert result.target_score == 0.0
