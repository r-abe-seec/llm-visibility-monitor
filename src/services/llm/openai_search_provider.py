from time import perf_counter
from typing import Any

from openai import OpenAI

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class OpenAISearchProvider(LLMProvider):
    """OpenAI with the built-in web_search tool enabled.

    Unlike the plain OpenAI provider (model knowledge only), this measures
    answers grounded in live web search — the closest API proxy to what
    ChatGPT search shows end users. Source URLs are captured as citations.
    """

    provider_name = "openai_search"

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        if not settings.openai_model:
            raise ValueError("OPENAI_MODEL is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @staticmethod
    def _extract_citations(response: Any) -> list[str]:
        urls: list[str] = []
        for item in getattr(response, "output", None) or []:
            if getattr(item, "type", None) != "message":
                continue
            for block in getattr(item, "content", None) or []:
                for annotation in getattr(block, "annotations", None) or []:
                    if getattr(annotation, "type", None) == "url_citation":
                        url = getattr(annotation, "url", None)
                        if url and url not in urls:
                            urls.append(url)
        return urls

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            tools=[{"type": "web_search"}],
        )

        latency_ms = int((perf_counter() - start_time) * 1000)

        usage = response.usage
        input_tokens = usage.input_tokens if usage else 0
        output_tokens = usage.output_tokens if usage else 0

        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            prompt=prompt,
            response=response.output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            citations=self._extract_citations(response),
        )
