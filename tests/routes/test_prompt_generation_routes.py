from fastapi.testclient import TestClient

from src.main import app
from src.routes.prompt_generation import get_generator, get_prompt_service
from src.services.prompt_generator import PromptGenerator
from src.services.prompt_service import PromptService

TEMPLATES = """\
templates:
  - category: recommendation
    title: おすすめ
    text: "{industry}でおすすめの会社を5社挙げてください。"
"""


def _client(tmp_path):
    templates = tmp_path / "templates.yaml"
    templates.write_text(TEMPLATES, encoding="utf-8")
    prompts_file = tmp_path / "prompts.yaml"

    app.dependency_overrides[get_generator] = lambda: PromptGenerator(templates)
    app.dependency_overrides[get_prompt_service] = lambda: PromptService(prompts_file)
    return TestClient(app), prompts_file


def test_generate_endpoint_returns_prompts(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/prompts/generate", json={"industry": "広告代理店"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["saved"] is False
    assert len(data["generated"]) == 1
    assert "広告代理店" in data["generated"][0]["text"]
    app.dependency_overrides.clear()


def test_generate_endpoint_saves_when_requested(tmp_path):
    client, prompts_file = _client(tmp_path)
    resp = client.post(
        "/prompts/generate",
        json={"industry": "広告代理店", "save": True},
    )
    assert resp.status_code == 200
    assert resp.json()["saved"] is True
    assert prompts_file.exists()
    assert "広告代理店" in prompts_file.read_text(encoding="utf-8")
    app.dependency_overrides.clear()


def test_generate_endpoint_validates_industry(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/prompts/generate", json={"industry": ""})
    assert resp.status_code == 422
    app.dependency_overrides.clear()
