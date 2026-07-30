from datetime import UTC, datetime

from fastapi.testclient import TestClient

from src.main import app
from src.models.analysis import BrandMention, VisibilityAnalysis
from src.models.llm_response import LLMResponse
from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.json_result_reader import JsonResultReader
from src.routes.history import get_reader


def _run(run_id, when, target_score, mentioned=True, rank=1):
    analysis = VisibilityAnalysis(
        brands=[
            BrandMention(
                brand="電通",
                is_target=True,
                mentioned=mentioned,
                count=1 if mentioned else 0,
                rank=rank,
                visibility_score=target_score,
            )
        ],
        target_score=target_score,
        share_of_voice=1.0 if mentioned else 0.0,
    )
    return PromptRunResult(
        run_id=run_id,
        provider="openai",
        executed_at=when,
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[
            PromptRunItem(
                prompt_id="p1",
                success=True,
                result=LLMResponse(
                    provider="openai",
                    model="gpt",
                    prompt="q",
                    response="電通",
                    input_tokens=1,
                    output_tokens=1,
                    latency_ms=1,
                ),
                analysis=analysis,
            )
        ],
    )


def _client(tmp_path):
    for r in [
        _run("old", datetime(2026, 1, 1, tzinfo=UTC), 80.0),
        _run("new", datetime(2026, 6, 1, tzinfo=UTC), 100.0),
    ]:
        (tmp_path / f"{r.run_id}.json").write_text(
            r.model_dump_json(), encoding="utf-8"
        )
    app.dependency_overrides[get_reader] = lambda: JsonResultReader(tmp_path)
    return TestClient(app)


def test_list_runs_endpoint(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/history/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert [d["run_id"] for d in data] == ["new", "old"]
    assert data[0]["target_score"] == 100.0
    app.dependency_overrides.clear()


def test_get_run_endpoint(tmp_path):
    client = _client(tmp_path)
    assert client.get("/history/runs/new").status_code == 200
    assert client.get("/history/runs/missing").status_code == 404
    app.dependency_overrides.clear()


def test_visibility_timeseries_endpoint(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/history/visibility", params={"brand": "電通"})
    assert resp.status_code == 200
    points = resp.json()
    # oldest first
    assert [p["run_id"] for p in points] == ["old", "new"]
    assert [p["visibility_score"] for p in points] == [80.0, 100.0]
    app.dependency_overrides.clear()


def test_comparison_endpoint(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/history/comparison")
    assert resp.status_code == 200
    data = resp.json()
    assert data["runs_analyzed"] == 2
    assert data["brands"][0]["brand"] == "電通"
    assert data["brands"][0]["mention_rate"] == 1.0

    filtered = client.get("/history/comparison", params={"provider": "openai"}).json()
    assert filtered["runs_analyzed"] == 2

    empty = client.get("/history/comparison", params={"provider": "nope"}).json()
    assert empty["runs_analyzed"] == 0
    app.dependency_overrides.clear()
