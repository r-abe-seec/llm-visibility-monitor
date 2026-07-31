from time import perf_counter
from typing import Any

from google import genai
from google.genai import types

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class GeminiSearchProvider(LLMProvider):
    """Gemini with Google Search grounding enabled.

    Measures answers grounded in live Google results — the closest API proxy
    to Google's AI Overviews / Gemini app behavior. Source URLs are captured
    as citations from the grounding metadata.
    """

    provider_name = "gemini_search"

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        if not settings.gemini_model:
            raise ValueError("GEMINI_MODEL is not configured.")

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    @staticmethod
    def _extract_citations(response: Any) -> list[str]:
        urls: list[str] = []
        for candidate in getattr(response, "candidates", None) or []:
            metadata = getattr(candidate, "grounding_metadata", None)
            if metadata is None:
                continue
            for chunk in getattr(metadata, "grounding_chunks", None) or []:
                web = getattr(chunk, "web", None)
                uri = getattr(web, "uri", None) if web else None
                if uri and uri not in urls:
                    urls.append(uri)
        return urls

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        latency_ms = int((perf_counter() - start_time) * 1000)

        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count if usage else 0
        output_tokens = usage.candidates_token_count if usage else 0

        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            prompt=prompt,
            response=response.text or "",
            input_tokens=input_tokens or 0,
            output_tokens=output_tokens or 0,
            latency_ms=latency_ms,
            citations=self._extract_citations(response),
        )
