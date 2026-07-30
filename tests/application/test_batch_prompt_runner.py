import src.application.batch_prompt_runner as runner_module
from src.application.batch_prompt_runner import BatchPromptRunner
from src.models.brand import Brand
from src.models.llm_response import LLMResponse
from src.models.prompt import Prompt
from src.repositories.result_repository import ResultRepository
from src.services.llm.base import LLMProvider
from src.services.prompt_service import PromptService

BRANDS = [
    Brand(name="電通", is_target=True),
    Brand(name="博報堂"),
]


class _FakeProvider(LLMProvider):
    provider_name = "fake"

    def __init__(self, replies: list[str]) -> None:
        self.replies = list(replies)

    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            provider="fake",
            model="fake",
            prompt=prompt,
            response=self.replies.pop(0),
            input_tokens=1,
            output_tokens=1,
            latency_ms=1,
        )


class _FakePromptService(PromptService):
    def get(self, prompt_id: str) -> Prompt:
        return Prompt(id=prompt_id, category="c", title="t", text="質問")


class _CapturingRepository(ResultRepository):
    def __init__(self) -> None:
        self.saved = None

    def save(self, result) -> None:
        self.saved = result


def _make_runner(repository):
    return BatchPromptRunner(
        prompt_service=_FakePromptService(),
        result_repository=repository,
        brands=BRANDS,
    )


def test_run_attaches_analysis_and_sentiment(monkeypatch):
    provider = _FakeProvider(
        [
            "1. 電通\n2. 博報堂",
            '{"電通": "positive", "博報堂": "neutral"}',
        ]
    )
    monkeypatch.setattr(runner_module.ProviderFactory, "create", lambda name: provider)
    repository = _CapturingRepository()

    result = _make_runner(repository).run("fake", ["p1"])

    item = result.results[0]
    assert item.success is True
    assert item.analysis is not None
    by_name = {m.brand: m for m in item.analysis.brands}
    assert by_name["電通"].sentiment == "positive"
    assert by_name["博報堂"].sentiment == "neutral"
    assert repository.saved is result


def test_sentiment_failure_does_not_break_run(monkeypatch):
    class _FlakyProvider(_FakeProvider):
        def generate(self, prompt: str) -> LLMResponse:
            if not self.replies:
                raise RuntimeError("sentiment call failed")
            return super().generate(prompt)

    provider = _FlakyProvider(["1. 電通"])
    monkeypatch.setattr(runner_module.ProviderFactory, "create", lambda name: provider)
    repository = _CapturingRepository()

    result = _make_runner(repository).run("fake", ["p1"])

    item = result.results[0]
    assert item.success is True
    assert item.analysis is not None
    assert all(m.sentiment is None for m in item.analysis.brands)


def test_sentiment_disabled(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "sentiment_enabled", False)
    provider = _FakeProvider(["1. 電通"])
    monkeypatch.setattr(runner_module.ProviderFactory, "create", lambda name: provider)
    repository = _CapturingRepository()

    result = _make_runner(repository).run("fake", ["p1"])

    item = result.results[0]
    assert item.analysis is not None
    assert all(m.sentiment is None for m in item.analysis.brands)
    # only one call was made (no sentiment prompt)
    assert provider.replies == []


def test_alerts_triggered_when_enabled(monkeypatch):
    import src.application.batch_prompt_runner as runner_mod
    from src.config import settings

    monkeypatch.setattr(settings, "alert_enabled", True)

    sent: list[str] = []

    class _FakeAlertService:
        def check_and_notify(self, run) -> None:
            sent.append(run.run_id)

    monkeypatch.setattr(runner_mod, "AlertService", lambda: _FakeAlertService())

    provider = _FakeProvider(["1. 電通", '{"電通": "positive"}'])
    monkeypatch.setattr(runner_module.ProviderFactory, "create", lambda name: provider)
    repository = _CapturingRepository()

    result = _make_runner(repository).run("fake", ["p1"])
    assert sent == [result.run_id]
