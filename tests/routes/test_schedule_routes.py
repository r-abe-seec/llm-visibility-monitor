from fastapi.testclient import TestClient

from src.main import app


def test_schedule_status_disabled_by_default():
    with TestClient(app) as client:
        resp = client.get("/schedule")

    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False
    assert data["cron"] == "0 6 * * *"
    assert data["providers"] == ["openai"]
    assert data["next_run_time"] is None


def test_schedule_status_reports_next_run_when_enabled(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "schedule_enabled", True)

    with TestClient(app) as client:
        resp = client.get("/schedule")

    data = resp.json()
    assert data["enabled"] is True
    assert data["next_run_time"] is not None
