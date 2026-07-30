import pytest

import src.services.llm.anthropic_provider as anthropic_module
import src.services.llm.openai_provider as openai_module
from src.services.llm.factory import ProviderFactory


class _DummyClient:
    def __init__(self, *args, **kwargs) -> None:
        pass


def test_unsupported_provider_raises():
    with pytest.raises(ValueError, match="Unsupported provider"):
        ProviderFactory.create("does-not-exist")


@pytest.mark.parametrize("name", ["openai", "gpt", "OpenAI", " openai "])
def test_openai_aliases_select_openai_provider(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(openai_module, "OpenAI", _DummyClient)

    provider = ProviderFactory.create(name)
    assert provider.provider_name == "openai"


@pytest.mark.parametrize("name", ["anthropic", "claude", "Claude"])
def test_anthropic_aliases_select_anthropic_provider(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    monkeypatch.setattr(anthropic_module, "Anthropic", _DummyClient)

    provider = ProviderFactory.create(name)
    assert provider.provider_name == "anthropic"


def test_openai_provider_requires_api_key(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "openai_api_key", None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        ProviderFactory.create("openai")
