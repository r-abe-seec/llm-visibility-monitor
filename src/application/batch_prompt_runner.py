from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.services.llm.factory import ProviderFactory
from src.services.prompt_service import PromptService


class BatchPromptRunner:
    def __init__(
        self,
        prompt_service: PromptService | None = None,
    ) -> None:
        self.prompt_service = prompt_service or PromptService()

    def run(
        self,
        provider_name: str,
        prompt_ids: list[str],
    ) -> PromptRunResult:
        provider = ProviderFactory.create(provider_name)
        results: list[PromptRunItem] = []

        for prompt_id in prompt_ids:
            try:
                prompt = self.prompt_service.get(prompt_id)
                llm_response = provider.generate(prompt.text)

                results.append(
                    PromptRunItem(
                        prompt_id=prompt_id,
                        success=True,
                        result=llm_response,
                    )
                )

            except Exception as error:
                results.append(
                    PromptRunItem(
                        prompt_id=prompt_id,
                        success=False,
                        error=f"{type(error).__name__}: {error}",
                    )
                )

        return PromptRunResult.create(
            provider=provider_name,
            results=results,
        )