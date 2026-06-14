"""Tests for cross-run state persistence (run_history.py)."""

import json
from pathlib import Path

import pytest

from plugin_examples.state.run_history import RunHistory, RunRecord


@pytest.fixture
def history_path(tmp_path: Path) -> Path:
    return tmp_path / "run-history.json"


class TestRunRecord:
    def test_defaults(self):
        r = RunRecord(family="cells", wave="26")
        assert r.family == "cells"
        assert r.wave == "26"
        assert r.timestamp  # auto-populated
        assert r.verdict == ""
        assert r.error_types == []

    def test_to_dict_roundtrip(self):
        r = RunRecord(
            family="pdf", wave="20", verdict="BUILD_PASS",
            test_count=100, error_types=["NUGET_FETCH_FAILED"],
        )
        d = r.to_dict()
        r2 = RunRecord.from_dict(d)
        assert r2.family == "pdf"
        assert r2.verdict == "BUILD_PASS"
        assert r2.error_types == ["NUGET_FETCH_FAILED"]


class TestRunHistory:
    def test_load_empty(self, history_path: Path):
        h = RunHistory.load(history_path)
        assert h.records == []

    def test_save_and_load(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="cells", wave="26", verdict="PASS"))
        h.record_run(RunRecord(family="pdf", wave="26", verdict="BLOCKED"))
        h.save()

        h2 = RunHistory.load(history_path)
        assert len(h2.records) == 2
        assert h2.records[0].family == "cells"
        assert h2.records[1].verdict == "BLOCKED"

    def test_rolling_cap(self, history_path: Path):
        h = RunHistory.load(history_path)
        for i in range(600):
            h.record_run(RunRecord(family="cells", wave=str(i), verdict="PASS"))
        h.save()
        h2 = RunHistory.load(history_path)
        assert len(h2.records) == RunHistory.MAX_RECORDS

    def test_recent_failures(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="cells", wave="1", verdict="PASS"))
        h.record_run(RunRecord(family="cells", wave="2", verdict="BLOCKED"))
        h.record_run(RunRecord(family="cells", wave="3", verdict="NUGET_FAILED"))
        h.record_run(RunRecord(family="cells", wave="4", verdict="PASS"))
        h.record_run(RunRecord(family="cells", wave="5", verdict="BLOCKED"))
        failures = h.recent_failures("cells", window=3)
        # Last 3 runs are waves 3 (NUGET_FAILED), 4 (PASS), 5 (BLOCKED) => 2 failures
        assert len(failures) == 2

    def test_consecutive_failure_count(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="pdf", wave="1", verdict="PASS"))
        h.record_run(RunRecord(family="pdf", wave="2", verdict="BLOCKED"))
        h.record_run(RunRecord(family="pdf", wave="3", verdict="NUGET_FAILED"))
        assert h.consecutive_failure_count("pdf") == 2

    def test_consecutive_failure_count_all_pass(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="pdf", wave="1", verdict="PASS"))
        assert h.consecutive_failure_count("pdf") == 0

    def test_failure_rate(self, history_path: Path):
        h = RunHistory.load(history_path)
        for i in range(10):
            verdict = "BLOCKED" if i % 3 == 0 else "PASS"
            h.record_run(RunRecord(family="cells", wave=str(i), verdict=verdict))
        rate = h.failure_rate("cells", window=10)
        assert 0.3 <= rate <= 0.5  # 4 failures out of 10

    def test_should_deprioritize(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="svg", wave="1", verdict="BLOCKED"))
        h.record_run(RunRecord(family="svg", wave="2", verdict="BLOCKED"))
        h.record_run(RunRecord(family="svg", wave="3", verdict="BLOCKED"))
        assert h.should_deprioritize("svg", threshold=3) is True
        assert h.should_deprioritize("svg", threshold=4) is False

    def test_common_error_types(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="cad", wave="1", error_types=["NUGET_FETCH", "DLL_MISSING"]))
        h.record_run(RunRecord(family="cad", wave="2", error_types=["NUGET_FETCH"]))
        errors = h.common_error_types("cad")
        assert errors["NUGET_FETCH"] == 2
        assert errors["DLL_MISSING"] == 1

    def test_corrupted_file_recovery(self, history_path: Path):
        history_path.write_text("not valid json", encoding="utf-8")
        h = RunHistory.load(history_path)
        assert h.records == []

    def test_empty_family_queries(self, history_path: Path):
        h = RunHistory.load(history_path)
        assert h.recent_failures("nonexistent") == []
        assert h.consecutive_failure_count("nonexistent") == 0
        assert h.failure_rate("nonexistent") == 0.0
        assert h.should_deprioritize("nonexistent") is False
        assert h.common_error_types("nonexistent") == {}

    def test_json_structure(self, history_path: Path):
        h = RunHistory.load(history_path)
        h.record_run(RunRecord(family="cells", wave="26", verdict="PASS"))
        h.save()
        data = json.loads(history_path.read_text(encoding="utf-8"))
        assert data["version"] == 1
        assert "updated_at" in data
        assert data["record_count"] == 1
        assert len(data["runs"]) == 1
