import logging
from abc import ABC, abstractmethod

import httpx

logger = logging.getLogger(__name__)


class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        """Deliver a notification message."""


class SlackWebhookNotifier(Notifier):
    """Sends messages to a Slack Incoming Webhook."""

    def __init__(self, webhook_url: str, timeout_seconds: float = 10.0) -> None:
        if not webhook_url:
            raise ValueError("SLACK_WEBHOOK_URL is not configured.")

        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds

    def send(self, message: str) -> None:
        response = httpx.post(
            self.webhook_url,
            json={"text": message},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()


class GoogleChatWebhookNotifier(Notifier):
    """Sends messages to a Google Chat space webhook."""

    def __init__(self, webhook_url: str, timeout_seconds: float = 10.0) -> None:
        if not webhook_url:
            raise ValueError("GOOGLE_CHAT_WEBHOOK_URL is not configured.")

        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds

    def send(self, message: str) -> None:
        response = httpx.post(
            self.webhook_url,
            json={"text": message},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()


class ConsoleNotifier(Notifier):
    """Fallback notifier that logs messages (useful for local testing)."""

    def send(self, message: str) -> None:
        logger.info("ALERT: %s", message)
