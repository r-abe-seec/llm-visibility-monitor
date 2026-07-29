from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.console_result_repository import (
    ConsoleResultRepository,
)
from src.repositories.result_repository import ResultRepository
from src.services.llm.factory import ProviderFactory
from src.services.prompt_service import PromptService


class BatchPromptRunner:
    def __init__(
        self,
        prompt_service: PromptService | None = None,
        result_repository: ResultRepository | None = None,
    ) -> None:
        self.prompt_service = prompt_service or PromptService()
        self.result_repository = (
            result_repository or ConsoleResultRepository()
        )

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

        run_result = PromptRunResult.create(
            provider=provider_name,
            results=results,
        )

        self.result_repository.save(run_result)

        return run_result