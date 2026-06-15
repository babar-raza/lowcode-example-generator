"""Tests for commands/metrics_summary.py — TC-RH05."""

from __future__ import annotations

import json
from pathlib import Path

from plugin_examples.commands.metrics_summary import generate_metrics_summary


class TestMetricsSummary:
    def test_generates_summary_with_no_runs(self, tmp_path: Path):
        summary = generate_metrics_summary(tmp_path)
        assert summary["latest_run"] is None
        assert summary["llm_metrics"] == {}

    def test_doctor_section_present(self, tmp_path: Path):
        summary = generate_metrics_summary(tmp_path)
        assert "doctor" in summary
        assert "total" in summary["doctor"]
        assert "passed" in summary["doctor"]

    def test_slo_section_present(self, tmp_path: Path):
        summary = generate_metrics_summary(tmp_path)
        assert "slo" in summary
        assert "slo_count" in summary["slo"]

    def test_json_serializable(self, tmp_path: Path):
        summary = generate_metrics_summary(tmp_path)
        serialized = json.dumps(summary)
        assert isinstance(serialized, str)

    def test_with_run_data(self, tmp_path: Path):
        run_dir = tmp_path / "workspace" / "runs" / "run-001"
        run_dir.mkdir(parents=True)
        ledger = {"entries": [{"tokens": 100, "duration_ms": 500}]}
        (run_dir / "llm-usage-ledger.json").write_text(json.dumps(ledger))
        summary = generate_metrics_summary(tmp_path)
        assert summary["latest_run"] is not None
        assert summary["llm_metrics"]["total_calls"] == 1
        assert summary["llm_metrics"]["total_tokens"] == 100
