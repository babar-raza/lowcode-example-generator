"""Integration test: failure gates.

Verifies that the pipeline correctly blocks on invalid input and
missing prerequisites, producing clear error signals.
"""

from pathlib import Path

import pytest


class TestFailureGates:
    """Verify that bad input and missing config fail clearly."""

    def test_missing_family_config_produces_empty(self, tmp_path: Path):
        """Empty config directory must produce empty family list."""
        from plugin_examples.fixture_factory.family_status_validators import _load_family_configs

        fake_config_dir = tmp_path / "configs" / "families"
        fake_config_dir.mkdir(parents=True)
        configs = _load_family_configs(fake_config_dir)
        assert configs == [], "Empty config dir must produce empty family list"

    def test_approval_gate_blocks_without_env(self, monkeypatch):
        """Publication gate blocks when approval env var is not set."""
        monkeypatch.delenv("PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL", raising=False)

        from plugin_examples.publisher.approval_gate import check_approval
        approved, reason = check_approval(None)
        assert approved is False, "Approval gate must block when env var absent"
        assert reason, "Blocked reason must be non-empty"

    def test_approval_gate_rejects_wrong_token(self):
        """Publication gate rejects incorrect approval token."""
        from plugin_examples.publisher.approval_gate import check_approval
        approved, reason = check_approval("WRONG_TOKEN")
        assert approved is False
        assert "invalid" in reason.lower() or "blocked" in reason.lower()

    def test_evidence_chain_rejects_null_paths(self):
        """ECV-01 fails when gate results have null evidence paths."""
        from plugin_examples.fixture_factory.evidence_chain_validators import (
            validate_ecv01_non_null_evidence_paths,
        )

        gates = [
            {"gate_id": "BAD-1", "evidence_path": None, "verdict": "PASS"},
            {"gate_id": "BAD-2", "verdict": "PASS"},  # missing key entirely
        ]
        results = validate_ecv01_non_null_evidence_paths(gates)
        assert all(not r.passed for r in results), \
            "All gates with null/missing evidence_path must fail ECV-01"

    def test_run_history_handles_corrupt_file(self, tmp_path: Path):
        """RunHistory gracefully handles corrupted state file."""
        from plugin_examples.state.run_history import RunHistory

        corrupt_path = tmp_path / "corrupt.json"
        corrupt_path.write_text("{{{{not json at all", encoding="utf-8")
        h = RunHistory.load(corrupt_path)
        assert h.records == [], "Corrupted history must produce empty state, not crash"

    def test_fsv_detects_missing_status(self):
        """FSV-01 flags configs without a status field."""
        from plugin_examples.fixture_factory.family_status_validators import (
            fsv_01_status_field_present,
        )

        configs = [
            {"_filename": "test.yml", "_family_name": "test"},  # no 'status'
        ]
        results = fsv_01_status_field_present(configs)
        assert any(not r.passed for r in results), \
            "Missing status field must be flagged"
