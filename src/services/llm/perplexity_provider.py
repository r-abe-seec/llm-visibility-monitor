from time import perf_counter
from typing import Any

from openai import OpenAI

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class PerplexityProvider(LLMProvider):
    """Perplexity provider.

    Perplexity exposes an OpenAI-compatible Chat Completions API, so we reuse
    the OpenAI SDK pointed at Perplexity's base URL. Perplexity additionally
    returns the web sources it used, which we capture as ``citations`` — the
    main reason this provider is valuable for AI-search visibility.
    """

    provider_name = "perplexity"

    def __init__(self) -> None:
        if not settings.perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY is not configured.")

        if not settings.perplexity_model:
            raise ValueError("PERPLEXITY_MODEL is not configured.")

        self.client = OpenAI(
            api_key=settings.perplexity_api_key,
            base_url=settings.perplexity_base_url,
        )
        self.model = settings.perplexity_model

    @staticmethod
    def _extract_citations(response: Any) -> list[str]:
        citations = getattr(response, "citations", None)
        if citations is None:
            extra = getattr(response, "model_extra", None)
            if extra:
                citations = extra.get("citations") or extra.get("search_results")
        if not citations:
            return []
        result: list[str] = []
        for item in citations:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                url = item.get("url") or item.get("link")
                if url:
                    result.append(url)
        return result

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = int((perf_counter() - start_time) * 1000)

        message = response.choices[0].message if response.choices else None
        response_text = (message.content if message else None) or ""

        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            prompt=prompt,
            response=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            citations=self._extract_citations(response),
        )
