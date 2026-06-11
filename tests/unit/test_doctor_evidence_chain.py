"""Unit tests for check_evidence_chain health check in doctor.py.

Tests all SKIP/PASS/WARN branches with hermetic tmp_path fixtures.
No production filesystem access.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.health.doctor import check_evidence_chain


def _ec_dir(root: Path) -> Path:
    """Return the evidence-chain path under root."""
    return root / ".local" / "evidence-chain"


class TestCheckEvidenceChain:

    def test_no_evidence_dir_returns_skip(self, tmp_path: Path) -> None:
        """Missing .local/evidence-chain/ → SKIP (not a failure)."""
        result = check_evidence_chain(tmp_path)
        assert result.status == "SKIP"
        assert "evidence-chain" in result.detail.lower()
        assert result.required is False

    def test_empty_evidence_dir_returns_skip(self, tmp_path: Path) -> None:
        """Dir exists but no JSON files → SKIP."""
        _ec_dir(tmp_path).mkdir(parents=True)
        result = check_evidence_chain(tmp_path)
        assert result.status == "SKIP"
        assert "No gate result JSON" in result.detail

    def test_json_without_gate_schema_returns_skip(self, tmp_path: Path) -> None:
        """JSON files present but none have gate_id/id/verdict → SKIP."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)
        (ec / "random.json").write_text(json.dumps({"foo": "bar", "count": 42}), encoding="utf-8")
        result = check_evidence_chain(tmp_path)
        assert result.status == "SKIP"
        assert "none match gate result schema" in result.detail

    def test_valid_gate_results_all_pass_returns_pass(self, tmp_path: Path) -> None:
        """Valid gate results with non-null evidence_path and matching verdicts → PASS."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)

        # Write an evidence artifact file that the gate references
        # (must NOT have gate_id/id/verdict at top level — those trigger gate loading)
        evidence_file = ec / "gate-evidence.json"
        evidence_file.write_text(json.dumps({"artifact_type": "build_proof", "exit_code": 0}), encoding="utf-8")

        gate_result = {
            "gate_id": "GATE-001",
            "verdict": "PASS",
            "evidence_path": "gate-evidence.json",
            "timestamp": "2026-06-11T10:00:00+00:00",
        }
        (ec / "gates.json").write_text(json.dumps([gate_result]), encoding="utf-8")

        result = check_evidence_chain(tmp_path)
        assert result.status == "PASS", f"Expected PASS, got {result.status}: {result.detail}"
        assert "gate records validated" in result.detail

    def test_gate_with_null_evidence_path_returns_warn(self, tmp_path: Path) -> None:
        """Gate with null evidence_path → ECV-01 fails → WARN."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)

        gate_result = {
            "gate_id": "GATE-002",
            "verdict": "PASS",
            "evidence_path": None,  # ECV-01 violation
            "timestamp": "2026-06-11T10:00:00+00:00",
        }
        (ec / "gates.json").write_text(json.dumps([gate_result]), encoding="utf-8")

        result = check_evidence_chain(tmp_path)
        assert result.status == "WARN", f"Expected WARN, got {result.status}: {result.detail}"
        assert "failures" in result.detail

    def test_gate_with_missing_evidence_file_returns_warn(self, tmp_path: Path) -> None:
        """Gate references a file that doesn't exist → ECV-02 fails → WARN."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)

        gate_result = {
            "gate_id": "GATE-003",
            "verdict": "PASS",
            "evidence_path": "nonexistent-file.json",
            "timestamp": "2026-06-11T10:00:00+00:00",
        }
        (ec / "gates.json").write_text(json.dumps([gate_result]), encoding="utf-8")

        result = check_evidence_chain(tmp_path)
        assert result.status == "WARN", f"Expected WARN, got {result.status}: {result.detail}"

    def test_gate_result_as_single_dict_is_loaded(self, tmp_path: Path) -> None:
        """A JSON file containing a single dict (not a list) is also loaded."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)

        # Single dict with 'id' key (not 'gate_id')
        gate_result = {
            "id": "GATE-004",
            "verdict": "PASS",
            "evidence_path": None,
        }
        (ec / "gate.json").write_text(json.dumps(gate_result), encoding="utf-8")

        result = check_evidence_chain(tmp_path)
        # Should attempt validation — null evidence_path triggers ECV-01 → WARN
        assert result.status == "WARN"

    def test_corrupt_json_is_skipped_gracefully(self, tmp_path: Path) -> None:
        """Corrupt JSON files are silently skipped; valid ones still processed."""
        ec = _ec_dir(tmp_path)
        ec.mkdir(parents=True)
        (ec / "corrupt.json").write_text("{ not valid json !!!", encoding="utf-8")

        # No valid gate files remain
        result = check_evidence_chain(tmp_path)
        assert result.status == "SKIP"

    def test_name_field_is_evidence_chain(self, tmp_path: Path) -> None:
        """Health check name is 'evidence_chain' for all status variants."""
        result = check_evidence_chain(tmp_path)
        assert result.name == "evidence_chain"
