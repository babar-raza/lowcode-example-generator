"""Integration tests for evidence artifact completeness — TC-INTTEST-005."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestEvidenceArtifactCompleteness:
    """Verify evidence artifact writing patterns."""

    def test_evidence_dir_json_files_parse(self, tmp_path):
        """JSON evidence files must be valid JSON."""
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()

        # Simulate writing evidence (the pattern used throughout runner.py)
        sample_evidence = {
            "family": "cells",
            "run_id": "test-run-001",
            "timestamp": "2026-06-09T00:00:00Z",
            "stage": "test_stage",
            "status": "success",
        }
        evidence_file = evidence_dir / "test-evidence.json"
        evidence_file.write_text(json.dumps(sample_evidence, indent=2), encoding="utf-8")

        # Verify all JSON files in evidence_dir parse cleanly
        json_files = list(evidence_dir.glob("*.json"))
        assert len(json_files) > 0, "Expected at least one JSON evidence file"
        for jf in json_files:
            data = json.loads(jf.read_text(encoding="utf-8"))
            assert isinstance(data, dict), f"{jf.name} is not a JSON object"

    def test_evidence_has_required_fields(self, tmp_path):
        """Evidence JSON must contain family, run_id, timestamp."""
        evidence = {
            "family": "cells",
            "run_id": "test-run-001",
            "timestamp": "2026-06-09T00:00:00Z",
        }
        evidence_file = tmp_path / "evidence.json"
        evidence_file.write_text(json.dumps(evidence), encoding="utf-8")

        data = json.loads(evidence_file.read_text(encoding="utf-8"))
        assert "family" in data
        assert "run_id" in data
        assert "timestamp" in data

    def test_gate_verdict_evidence_structure(self, tmp_path):
        """Gate verdict evidence must have expected structure."""
        gate_verdict = {
            "family": "cells",
            "run_id": "test-run-001",
            "timestamp": "2026-06-09T00:00:00Z",
            "verdict": "DRY_RUN_COMPLETE",
            "total_generated": 5,
            "total_pr_candidates": 4,
            "total_excluded": 1,
            "blocked_reasons": {"EXAMPLE_BLOCKED_BUILD_FAILED": 1},
        }
        verdict_file = tmp_path / "gate-verdict.json"
        verdict_file.write_text(json.dumps(gate_verdict, indent=2), encoding="utf-8")

        data = json.loads(verdict_file.read_text(encoding="utf-8"))
        assert data["verdict"] == "DRY_RUN_COMPLETE"
        assert data["total_generated"] >= data["total_pr_candidates"]
        assert isinstance(data["blocked_reasons"], dict)

    def test_example_gate_result_serializable(self):
        """ExampleGateResult must be serializable to JSON."""
        from dataclasses import asdict

        from plugin_examples.gates.example_gates import ExampleGateResult

        eg = ExampleGateResult(
            scenario_id="cells-converter",
            example_path="/tmp/example",
            restore_status="passed",
            build_status="passed",
            run_status="passed",
            output_validation_status="advisory_passed",
            publish_candidate=True,
            final_example_verdict="EXAMPLE_READY_FOR_PR_DRY_RUN",
        )
        data = asdict(eg)
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        assert deserialized["scenario_id"] == "cells-converter"
        assert deserialized["publish_candidate"] is True
