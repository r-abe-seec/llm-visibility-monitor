from src.services.llm.anthropic_provider import AnthropicProvider
from src.services.llm.azure_openai_provider import AzureOpenAIProvider
from src.services.llm.base import LLMProvider
from src.services.llm.gemini_provider import GeminiProvider
from src.services.llm.gemini_search_provider import GeminiSearchProvider
from src.services.llm.openai_provider import OpenAIProvider
from src.services.llm.openai_search_provider import OpenAISearchProvider
from src.services.llm.perplexity_provider import PerplexityProvider


class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> LLMProvider:
        normalized_name = provider_name.strip().lower()

        if normalized_name in {"anthropic", "claude"}:
            return AnthropicProvider()

        if normalized_name in {"openai", "gpt"}:
            return OpenAIProvider()

        if normalized_name in {"openai-search", "openai_search", "chatgpt-search"}:
            return OpenAISearchProvider()

        if normalized_name in {"gemini", "google"}:
            return GeminiProvider()

        if normalized_name in {"gemini-search", "gemini_search"}:
            return GeminiSearchProvider()

        if normalized_name in {"perplexity", "pplx", "sonar"}:
            return PerplexityProvider()

        if normalized_name in {"azure", "azure-openai", "azure_openai"}:
            return AzureOpenAIProvider()

        raise ValueError(f"Unsupported provider: {provider_name}")
