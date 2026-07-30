import src.application.scheduled_runner as scheduled_module
from src.application.scheduled_runner import (
    JOB_ID,
    create_scheduler,
    parse_csv,
    resolve_prompt_ids,
    run_scheduled_batch,
)
from src.models.prompt import Prompt
from src.services.prompt_service import PromptService


def test_parse_csv():
    assert parse_csv("openai, gemini ,,perplexity") == [
        "openai",
        "gemini",
        "perplexity",
    ]
    assert parse_csv("") == []


class _FakePromptService(PromptService):
    def load_all(self) -> list[Prompt]:
        return [
            Prompt(id="p1", category="c", title="t", text="x"),
            Prompt(id="p2", category="c", title="t", text="y"),
        ]


def test_resolve_prompt_ids_defaults_to_all(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "schedule_prompt_ids", "")
    assert resolve_prompt_ids(_FakePromptService()) == ["p1", "p2"]


def test_resolve_prompt_ids_uses_configuration(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "schedule_prompt_ids", "p2, p9")
    assert resolve_prompt_ids(_FakePromptService()) == ["p2", "p9"]


def test_run_scheduled_batch_runs_each_provider(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "schedule_providers", "openai, gemini")
    monkeypatch.setattr(settings, "schedule_prompt_ids", "p1")
    monkeypatch.setattr(settings, "result_repository", "console")

    calls: list[tuple[str, list[str]]] = []

    class _FakeRunner:
        def __init__(self, **kwargs) -> None:
            pass

        def run(self, provider_name, prompt_ids):
            calls.append((provider_name, prompt_ids))

            class _R:
                run_id = "r"
                success_count = 1
                failure_count = 0

            return _R()

    monkeypatch.setattr(scheduled_module, "BatchPromptRunner", _FakeRunner)

    run_scheduled_batch()

    assert calls == [("openai", ["p1"]), ("gemini", ["p1"])]


def test_run_scheduled_batch_continues_after_provider_failure(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "schedule_providers", "bad, gemini")
    monkeypatch.setattr(settings, "schedule_prompt_ids", "p1")
    monkeypatch.setattr(settings, "result_repository", "console")

    calls: list[str] = []

    class _FakeRunner:
        def __init__(self, **kwargs) -> None:
            pass

        def run(self, provider_name, prompt_ids):
            calls.append(provider_name)
            if provider_name == "bad":
                raise RuntimeError("boom")

            class _R:
                run_id = "r"
                success_count = 1
                failure_count = 0

            return _R()

    monkeypatch.setattr(scheduled_module, "BatchPromptRunner", _FakeRunner)

    run_scheduled_batch()

    assert calls == ["bad", "gemini"]


def test_create_scheduler_registers_job():
    scheduler = create_scheduler()
    job = scheduler.get_job(JOB_ID)
    assert job is not None
