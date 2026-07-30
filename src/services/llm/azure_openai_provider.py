from time import perf_counter

from openai import AzureOpenAI

from src.config import settings
from src.models.llm_response import LLMResponse
from src.services.llm.base import LLMProvider


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI provider.

    Uses the Azure-specific client from the OpenAI SDK. ``model`` maps to the
    Azure *deployment name*, which may differ from the underlying model name.
    """

    provider_name = "azure_openai"

    def __init__(self) -> None:
        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured.")

        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not configured.")

        if not settings.azure_openai_deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is not configured.")

        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        self.deployment = settings.azure_openai_deployment

    def generate(self, prompt: str) -> LLMResponse:
        start_time = perf_counter()

        response = self.client.chat.completions.create(
            model=self.deployment,
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
            model=self.deployment,
            prompt=prompt,
            response=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
