from types import SimpleNamespace

import src.services.llm.gemini_search_provider as gemini_search_module
import src.services.llm.openai_search_provider as openai_search_module
from src.services.llm.gemini_search_provider import GeminiSearchProvider
from src.services.llm.openai_search_provider import OpenAISearchProvider

# ---- OpenAI search ----


class _FakeResponses:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        annotation = SimpleNamespace(
            type="url_citation", url="https://example.com/source"
        )
        block = SimpleNamespace(annotations=[annotation])
        message = SimpleNamespace(type="message", content=[block])
        return SimpleNamespace(
            output=[message],
            output_text="花葬儀が横浜でおすすめです。",
            usage=SimpleNamespace(input_tokens=12, output_tokens=34),
        )


class _FakeOpenAIClient:
    def __init__(self, *args, **kwargs) -> None:
        self.responses = _FakeResponses()


def _openai_provider(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(openai_search_module, "OpenAI", _FakeOpenAIClient)
    return OpenAISearchProvider()


def test_openai_search_enables_web_search_tool(monkeypatch):
    provider = _openai_provider(monkeypatch)
    provider.generate("おすすめの葬儀社は？")
    call = provider.client.responses.calls[0]
    assert call["tools"] == [{"type": "web_search"}]


def test_openai_search_extracts_citations(monkeypatch):
    result = _openai_provider(monkeypatch).generate("q")
    assert result.provider == "openai_search"
    assert result.citations == ["https://example.com/source"]
    assert result.response == "花葬儀が横浜でおすすめです。"


# ---- Gemini search ----


class _FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        chunk = SimpleNamespace(
            web=SimpleNamespace(uri="https://vertexaisearch.example/redirect")
        )
        candidate = SimpleNamespace(
            grounding_metadata=SimpleNamespace(grounding_chunks=[chunk])
        )
        return SimpleNamespace(
            candidates=[candidate],
            text="花葬儀は横浜の家族葬に対応しています。",
            usage_metadata=SimpleNamespace(
                prompt_token_count=10, candidates_token_count=20
            ),
        )


class _FakeGeminiClient:
    def __init__(self, *args, **kwargs) -> None:
        self.models = _FakeModels()


def _gemini_provider(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(gemini_search_module.genai, "Client", _FakeGeminiClient)
    return GeminiSearchProvider()


def test_gemini_search_enables_grounding_tool(monkeypatch):
    provider = _gemini_provider(monkeypatch)
    provider.generate("おすすめの葬儀社は？")
    config = provider.client.models.calls[0]["config"]
    assert config.tools[0].google_search is not None


def test_gemini_search_extracts_citations(monkeypatch):
    result = _gemini_provider(monkeypatch).generate("q")
    assert result.provider == "gemini_search"
    assert result.citations == ["https://vertexaisearch.example/redirect"]
