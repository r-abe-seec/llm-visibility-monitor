from pathlib import Path

import pytest

from src.services.prompt_generator import PromptGenerator
from src.services.prompt_service import PromptService

TEMPLATES = """\
templates:
  - category: recommendation
    title: おすすめ
    text: "{industry}でおすすめの会社を5社挙げてください。"
  - category: reputation
    title: 評判
    text: "{target}の評判を教えてください。"
"""


@pytest.fixture
def generator(tmp_path: Path) -> PromptGenerator:
    path = tmp_path / "templates.yaml"
    path.write_text(TEMPLATES, encoding="utf-8")
    return PromptGenerator(path)


def test_generate_fills_industry(generator):
    prompts = generator.generate(industry="広告代理店")
    assert len(prompts) == 1
    assert prompts[0].text == "広告代理店でおすすめの会社を5社挙げてください。"
    assert prompts[0].id == "gen_recommendation"


def test_target_templates_skipped_without_target(generator):
    categories = [p.category for p in generator.generate(industry="広告代理店")]
    assert "reputation" not in categories


def test_target_templates_included_with_target(generator):
    prompts = generator.generate(industry="広告代理店", target="電通")
    by_category = {p.category: p for p in prompts}
    assert by_category["reputation"].text == "電通の評判を教えてください。"


def test_category_filter(generator):
    prompts = generator.generate(
        industry="広告代理店", target="電通", categories=["reputation"]
    )
    assert [p.category for p in prompts] == ["reputation"]


def test_ids_unique_against_existing(generator):
    prompts = generator.generate(
        industry="広告代理店", existing_ids={"gen_recommendation"}
    )
    assert prompts[0].id == "gen_recommendation_2"


def test_missing_template_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        PromptGenerator(tmp_path / "nope.yaml").load_templates()


def test_prompt_service_append_roundtrip(tmp_path, generator):
    prompts_file = tmp_path / "prompts.yaml"
    prompts_file.write_text(
        "prompts:\n"
        "  - id: existing\n"
        "    category: test\n"
        "    title: 既存\n"
        "    text: 既存プロンプト\n",
        encoding="utf-8",
    )
    service = PromptService(prompts_file)

    generated = generator.generate(industry="広告代理店")
    service.append(generated)

    loaded = service.load_all()
    ids = [p.id for p in loaded]
    assert ids == ["existing", "gen_recommendation"]
    assert loaded[1].text == "広告代理店でおすすめの会社を5社挙げてください。"
