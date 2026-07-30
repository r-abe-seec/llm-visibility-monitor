from src.config import settings
from src.models.analysis import VisibilityAnalysis
from src.models.brand import Brand
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.console_result_repository import (
    ConsoleResultRepository,
)
from src.repositories.result_repository import ResultRepository
from src.services.alert_service import AlertService
from src.services.analysis.analyzer import analyze_visibility
from src.services.analysis.sentiment import judge_sentiments
from src.services.llm.base import LLMProvider
from src.services.llm.factory import ProviderFactory
from src.services.prompt_service import PromptService


class BatchPromptRunner:
    def __init__(
        self,
        prompt_service: PromptService | None = None,
        result_repository: ResultRepository | None = None,
        brands: list[Brand] | None = None,
    ) -> None:
        self.prompt_service = prompt_service or PromptService()
        self.result_repository = result_repository or ConsoleResultRepository()
        self.brands = brands or []

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

                analysis = (
                    analyze_visibility(llm_response.response, self.brands)
                    if self.brands
                    else None
                )

                if analysis and settings.sentiment_enabled:
                    self._enrich_sentiment(provider, llm_response.response, analysis)

                results.append(
                    PromptRunItem(
                        prompt_id=prompt_id,
                        success=True,
                        result=llm_response,
                        analysis=analysis,
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

        if settings.alert_enabled:
            AlertService().check_and_notify(run_result)

        return run_result

    @staticmethod
    def _enrich_sentiment(
        provider: LLMProvider,
        response_text: str,
        analysis: VisibilityAnalysis,
    ) -> None:
        mentioned = [m.brand for m in analysis.brands if m.mentioned]
        if not mentioned:
            return
        try:
            sentiments = judge_sentiments(provider, response_text, mentioned)
        except Exception:
            return
        for mention in analysis.brands:
            if mention.brand in sentiments:
                mention.sentiment = sentiments[mention.brand]
