import pytest

import src.factories.reader_factory as factory_module
from src.factories.reader_factory import build_result_reader
from src.repositories.bigquery_result_reader import BigQueryResultReader
from src.repositories.json_result_reader import JsonResultReader


def test_json_reader_by_default(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "result_repository", "json")
    assert isinstance(build_result_reader(), JsonResultReader)


def test_console_repository_falls_back_to_json_reader(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "result_repository", "console")
    assert isinstance(build_result_reader(), JsonResultReader)


def test_bigquery_reader_when_configured(monkeypatch):
    from src.config import settings

    class _DummyService:
        def __init__(self, project_id, dataset, table) -> None:
            self.table_id = f"{project_id}.{dataset}.{table}"

    monkeypatch.setattr(settings, "result_repository", "bigquery")
    monkeypatch.setattr(settings, "gcp_project_id", "proj")
    monkeypatch.setattr(settings, "bigquery_dataset", "ds")
    monkeypatch.setattr(settings, "history_max_runs", 42)
    monkeypatch.setattr(factory_module, "BigQueryService", _DummyService)

    reader = build_result_reader()
    assert isinstance(reader, BigQueryResultReader)
    assert reader.max_runs == 42


def test_bigquery_reader_requires_project(monkeypatch):
    from src.config import settings

    monkeypatch.setattr(settings, "result_repository", "bigquery")
    monkeypatch.setattr(settings, "gcp_project_id", None)
    with pytest.raises(ValueError, match="GCP_PROJECT_ID"):
        build_result_reader()
