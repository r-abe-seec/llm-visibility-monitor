from time import perf_counter

from anthropic import Anthropic

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    provider_name = "anthropic"

    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        if not settings.anthropic_model:
            raise ValueError("ANTHROPIC_MODEL is not configured.")

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        latency_ms = int((perf_counter() - start_time) * 1000)

        text_parts = [
            block.text
            for block in message.content
            if block.type == "text"
        ]

        response_text = "\n".join(text_parts)

        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            prompt=prompt,
            response=response_text,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            latency_ms=latency_ms,
        )