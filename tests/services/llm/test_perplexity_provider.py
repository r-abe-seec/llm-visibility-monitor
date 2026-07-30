from types import SimpleNamespace

import src.services.llm.perplexity_provider as perplexity_module
from src.services.llm.perplexity_provider import PerplexityProvider


class _FakeCompletions:
    def create(self, model, messages):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="電通が1位です。"))
            ],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7),
            citations=[
                "https://example.com/a",
                {"url": "https://example.com/b"},
            ],
        )


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:
        self.chat = SimpleNamespace(completions=_FakeCompletions())


def _provider(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "perplexity_api_key", "test-key")
    monkeypatch.setattr(perplexity_module, "OpenAI", _FakeClient)
    return PerplexityProvider()


def test_generate_maps_response_fields(monkeypatch):
    result = _provider(monkeypatch).generate("おすすめの広告代理店は？")
    assert result.provider == "perplexity"
    assert result.response == "電通が1位です。"
    assert result.input_tokens == 11
    assert result.output_tokens == 7


def test_generate_extracts_citations_str_and_dict(monkeypatch):
    result = _provider(monkeypatch).generate("q")
    assert result.citations == [
        "https://example.com/a",
        "https://example.com/b",
    ]
