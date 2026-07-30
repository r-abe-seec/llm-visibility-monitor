from src.services.llm.anthropic_provider import AnthropicProvider
from src.services.llm.base import LLMProvider
from src.services.llm.gemini_provider import GeminiProvider
from src.services.llm.openai_provider import OpenAIProvider
from src.services.llm.perplexity_provider import PerplexityProvider


class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> LLMProvider:
        normalized_name = provider_name.strip().lower()

        if normalized_name in {"anthropic", "claude"}:
            return AnthropicProvider()

        if normalized_name in {"openai", "gpt"}:
            return OpenAIProvider()

        if normalized_name in {"gemini", "google"}:
            return GeminiProvider()

        if normalized_name in {"perplexity", "pplx", "sonar"}:
            return PerplexityProvider()

        raise ValueError(f"Unsupported provider: {provider_name}")
