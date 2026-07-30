from datetime import UTC, datetime

import src.services.notification.notifier as notifier_module
from src.models.analysis import BrandMention, VisibilityAnalysis
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.services.alert_service import AlertService, build_notifier
from src.services.notification.notifier import (
    ConsoleNotifier,
    GoogleChatWebhookNotifier,
    Notifier,
    SlackWebhookNotifier,
)


class _CapturingNotifier(Notifier):
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, message: str) -> None:
        self.messages.append(message)


def _run(run_id, score, mentioned=True, provider="openai", when=None):
    analysis = VisibilityAnalysis(
        brands=[
            BrandMention(
                brand="電通",
                is_target=True,
                mentioned=mentioned,
                count=1 if mentioned else 0,
                visibility_score=score,
            )
        ],
        target_score=score,
        share_of_voice=1.0 if mentioned else 0.0,
    )
    return PromptRunResult(
        run_id=run_id,
        provider=provider,
        executed_at=when or datetime(2026, 7, 30, tzinfo=UTC),
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[PromptRunItem(prompt_id="p1", success=True, analysis=analysis)],
    )


def test_alert_when_target_not_mentioned():
    service = AlertService(notifier=_CapturingNotifier())
    messages = service.evaluate(_run("r1", 0.0, mentioned=False), None)
    assert len(messages) == 1
    assert "was not mentioned" in messages[0]


def test_alert_on_score_drop_over_threshold(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "alert_score_drop_threshold", 20.0)
    service = AlertService(notifier=_CapturingNotifier())
    previous = _run("r0", 90.0)
    current = _run("r1", 60.0)
    messages = service.evaluate(current, previous)
    assert len(messages) == 1
    assert "dropped" in messages[0]


def test_no_alert_below_threshold(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "alert_score_drop_threshold", 20.0)
    service = AlertService(notifier=_CapturingNotifier())
    messages = service.evaluate(_run("r1", 80.0), _run("r0", 90.0))
    assert messages == []


def test_no_drop_alert_without_previous_run():
    service = AlertService(notifier=_CapturingNotifier())
    assert service.evaluate(_run("r1", 80.0), None) == []


def test_check_and_notify_sends_messages(monkeypatch):
    notifier = _CapturingNotifier()
    service = AlertService(notifier=notifier)
    monkeypatch.setattr(service, "find_previous_run", lambda run: None)

    service.check_and_notify(_run("r1", 0.0, mentioned=False))
    assert len(notifier.messages) == 1


def test_check_and_notify_never_raises(monkeypatch):
    class _FailingNotifier(Notifier):
        def send(self, message: str) -> None:
            raise RuntimeError("slack down")

    service = AlertService(notifier=_FailingNotifier())
    monkeypatch.setattr(service, "find_previous_run", lambda run: None)

    # must not raise
    service.check_and_notify(_run("r1", 0.0, mentioned=False))


def test_slack_notifier_posts_payload(monkeypatch):
    calls: dict[str, object] = {}

    class _Resp:
        def raise_for_status(self):
            calls["checked"] = True

    def _fake_post(url, json=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        return _Resp()

    monkeypatch.setattr(notifier_module.httpx, "post", _fake_post)

    SlackWebhookNotifier("https://hooks.slack.com/services/X").send("hello")
    assert calls["url"] == "https://hooks.slack.com/services/X"
    assert calls["json"] == {"text": "hello"}
    assert calls["checked"] is True


def test_google_chat_notifier_posts_payload(monkeypatch):
    calls: dict[str, object] = {}

    class _Resp:
        def raise_for_status(self):
            calls["checked"] = True

    def _fake_post(url, json=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        return _Resp()

    monkeypatch.setattr(notifier_module.httpx, "post", _fake_post)

    GoogleChatWebhookNotifier(
        "https://chat.googleapis.com/v1/spaces/X/messages?key=k&token=t"
    ).send("hello")
    assert calls["json"] == {"text": "hello"}
    assert calls["checked"] is True


def test_build_notifier_prefers_google_chat(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(
        settings,
        "google_chat_webhook_url",
        "https://chat.googleapis.com/v1/spaces/X/messages?key=k&token=t",
    )
    monkeypatch.setattr(settings, "slack_webhook_url", "https://hooks.slack.com/x")
    assert isinstance(build_notifier(), GoogleChatWebhookNotifier)


def test_build_notifier_falls_back_to_console(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "google_chat_webhook_url", None)
    monkeypatch.setattr(settings, "slack_webhook_url", None)
    assert isinstance(build_notifier(), ConsoleNotifier)
