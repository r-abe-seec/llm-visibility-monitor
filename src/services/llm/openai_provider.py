from time import perf_counter

from openai import OpenAI

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    provider_name = "openai"

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        if not settings.openai_model:
            raise ValueError("OPENAI_MODEL is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
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
        )
