from datetime import UTC, datetime

from src.models.prompt_run import PromptRunItem, PromptRunResult
from src.repositories.json_result_reader import JsonResultReader


def _write_run(directory, run_id, when):
    run = PromptRunResult(
        run_id=run_id,
        provider="openai",
        executed_at=when,
        requested_count=1,
        success_count=1,
        failure_count=0,
        results=[PromptRunItem(prompt_id="p1", success=True)],
    )
    (directory / f"{run_id}.json").write_text(run.model_dump_json(), encoding="utf-8")
    return run


def test_list_runs_newest_first(tmp_path):
    _write_run(tmp_path, "old", datetime(2026, 1, 1, tzinfo=UTC))
    _write_run(tmp_path, "new", datetime(2026, 6, 1, tzinfo=UTC))

    reader = JsonResultReader(tmp_path)
    runs = reader.list_runs()

    assert [r.run_id for r in runs] == ["new", "old"]


def test_list_runs_empty_when_dir_missing(tmp_path):
    reader = JsonResultReader(tmp_path / "does-not-exist")
    assert reader.list_runs() == []


def test_get_run_returns_match(tmp_path):
    _write_run(tmp_path, "abc", datetime(2026, 1, 1, tzinfo=UTC))
    reader = JsonResultReader(tmp_path)
    assert reader.get_run("abc").run_id == "abc"


def test_get_run_missing_raises(tmp_path):
    reader = JsonResultReader(tmp_path)
    try:
        reader.get_run("nope")
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
