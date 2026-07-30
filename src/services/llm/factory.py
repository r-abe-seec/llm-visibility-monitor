from src.services.llm.anthropic_provider import AnthropicProvider
from src.services.llm.base import LLMProvider


class ProviderFactory:
    @staticmethod
    def create(provider_name: str) -> LLMProvider:
        normalized_name = provider_name.strip().lower()

        if normalized_name in {"anthropic", "claude"}:
            return AnthropicProvider()

        raise ValueError(f"Unsupported provider: {provider_name}")
