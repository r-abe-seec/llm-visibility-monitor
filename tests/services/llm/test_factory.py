import pytest

import src.services.llm.anthropic_provider as anthropic_module
import src.services.llm.azure_openai_provider as azure_module
import src.services.llm.gemini_provider as gemini_module
import src.services.llm.gemini_search_provider as gemini_search_module
import src.services.llm.openai_provider as openai_module
import src.services.llm.openai_search_provider as openai_search_module
import src.services.llm.perplexity_provider as perplexity_module
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


@pytest.mark.parametrize("name", ["gemini", "google", "Gemini"])
def test_gemini_aliases_select_gemini_provider(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(gemini_module.genai, "Client", _DummyClient)

    provider = ProviderFactory.create(name)
    assert provider.provider_name == "gemini"


def test_gemini_provider_requires_api_key(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        ProviderFactory.create("gemini")


@pytest.mark.parametrize("name", ["perplexity", "pplx", "sonar", "Perplexity"])
def test_perplexity_aliases_select_perplexity_provider(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "perplexity_api_key", "test-key")
    monkeypatch.setattr(perplexity_module, "OpenAI", _DummyClient)

    provider = ProviderFactory.create(name)
    assert provider.provider_name == "perplexity"


def test_perplexity_provider_requires_api_key(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "perplexity_api_key", None)
    with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
        ProviderFactory.create("perplexity")


@pytest.mark.parametrize("name", ["azure", "azure-openai", "Azure_OpenAI"])
def test_azure_aliases_select_azure_provider(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "azure_openai_api_key", "test-key")
    monkeypatch.setattr(settings, "azure_openai_endpoint", "https://x.openai.azure.com")
    monkeypatch.setattr(settings, "azure_openai_deployment", "gpt-4o")
    monkeypatch.setattr(azure_module, "AzureOpenAI", _DummyClient)

    provider = ProviderFactory.create(name)
    assert provider.provider_name == "azure_openai"


def test_azure_provider_requires_configuration(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "azure_openai_api_key", None)
    with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY"):
        ProviderFactory.create("azure")

    monkeypatch.setattr(settings, "azure_openai_api_key", "k")
    monkeypatch.setattr(settings, "azure_openai_endpoint", None)
    with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
        ProviderFactory.create("azure")


@pytest.mark.parametrize("name", ["openai-search", "openai_search", "chatgpt-search"])
def test_openai_search_aliases(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(openai_search_module, "OpenAI", _DummyClient)

    assert ProviderFactory.create(name).provider_name == "openai_search"


@pytest.mark.parametrize("name", ["gemini-search", "gemini_search"])
def test_gemini_search_aliases(name, monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(gemini_search_module.genai, "Client", _DummyClient)

    assert ProviderFactory.create(name).provider_name == "gemini_search"
