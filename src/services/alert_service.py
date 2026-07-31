import logging

from src.config import settings
from src.factories.reader_factory import build_result_reader
from src.models.prompt_run import PromptRunResult
from src.services.notification.notifier import (
    ConsoleNotifier,
    GoogleChatWebhookNotifier,
    Notifier,
    SlackWebhookNotifier,
)

logger = logging.getLogger(__name__)


def build_notifier() -> Notifier:
    if settings.google_chat_webhook_url:
        return GoogleChatWebhookNotifier(settings.google_chat_webhook_url)
    if settings.slack_webhook_url:
        return SlackWebhookNotifier(settings.slack_webhook_url)
    return ConsoleNotifier()


def _target_scores(run: PromptRunResult) -> dict[str, float]:
    """Best score per target brand across the run's prompt items."""
    scores: dict[str, float] = {}
    for item in run.results:
        if not item.analysis:
            continue
        for mention in item.analysis.brands:
            if not mention.is_target:
                continue
            current = scores.get(mention.brand)
            if current is None or mention.visibility_score > current:
                scores[mention.brand] = mention.visibility_score
    return scores


class AlertService:
    def __init__(self, notifier: Notifier | None = None) -> None:
        self.notifier = notifier or build_notifier()

    def evaluate(
        self,
        run: PromptRunResult,
        previous: PromptRunResult | None,
    ) -> list[str]:
        """Return alert messages for visibility loss or score drops."""
        messages: list[str] = []
        current_scores = _target_scores(run)

        for brand, score in current_scores.items():
            if score == 0.0:
                messages.append(
                    f"⚠️ *{brand}* was not mentioned by "
                    f"`{run.provider}` (run `{run.run_id}`)."
                )

        if previous is not None:
            previous_scores = _target_scores(previous)
            threshold = settings.alert_score_drop_threshold
            for brand, score in current_scores.items():
                before = previous_scores.get(brand)
                if before is None:
                    continue
                drop = before - score
                if drop >= threshold and score > 0.0:
                    messages.append(
                        f"📉 *{brand}* visibility "
                        f"dropped {before:.0f} → {score:.0f} "
                        f"on `{run.provider}` (run `{run.run_id}`)."
                    )

        return messages

    def find_previous_run(self, run: PromptRunResult) -> PromptRunResult | None:
        """Most recent stored run for the same provider before this one."""
        reader = build_result_reader()
        for candidate in reader.list_runs():
            if candidate.run_id == run.run_id:
                continue
            if candidate.provider != run.provider:
                continue
            if candidate.executed_at < run.executed_at:
                return candidate
        return None

    def check_and_notify(self, run: PromptRunResult) -> None:
        """Evaluate alerts for a finished run and send notifications.

        Never raises: alerting is best-effort and must not break runs.
        """
        try:
            previous = self.find_previous_run(run)
            for message in self.evaluate(run, previous):
                self.notifier.send(message)
        except Exception:
            logger.exception("Alert notification failed for run %s", run.run_id)
