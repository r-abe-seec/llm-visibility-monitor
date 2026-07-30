from time import perf_counter

from google import genai

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        if not settings.gemini_model:
            raise ValueError("GEMINI_MODEL is not configured.")

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
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
        )
