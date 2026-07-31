"""Isolate tests from the developer's local .env.

Settings load .env at import time, so a developer's real configuration
(e.g. SCHEDULE_ENABLED=true) would otherwise leak into tests and make
them environment-dependent. This autouse fixture resets the
behavior-affecting fields to their code defaults before every test;
individual tests still override them via monkeypatch as needed.
"""

import pytest

from src.config import Settings, settings

_RESET_FIELDS = (
    "result_repository",
    "results_dir",
    "history_max_runs",
    "analysis_enabled",
    "sentiment_enabled",
    "brands_file",
    "schedule_enabled",
    "schedule_cron",
    "schedule_timezone",
    "schedule_providers",
    "schedule_prompt_ids",
    "alert_enabled",
    "alert_score_drop_threshold",
    "slack_webhook_url",
    "google_chat_webhook_url",
)


@pytest.fixture(autouse=True)
def _isolate_settings(monkeypatch):
    defaults = Settings(_env_file=None)
    for field in _RESET_FIELDS:
        monkeypatch.setattr(settings, field, getattr(defaults, field))
