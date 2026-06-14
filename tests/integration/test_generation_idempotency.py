"""Integration test: generation idempotency.

Verifies that deterministic pipeline operations produce stable output
when run twice with identical input.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def mock_family_config() -> SimpleNamespace:
    """Minimal family config for deterministic testing."""
    return SimpleNamespace(
        family="cells",
        nuget_package="Aspose.Cells",
        version="25.1.0",
        plugin_namespace="Aspose.Cells.LowCode",
        github_repo="aspose-cells/Aspose.Cells-for-.NET",
        example_repo="aspose-cells-net/Aspose.Cells-LowCode-Examples",
        validation=SimpleNamespace(
            restore=True, build=True, run=False, output=False,
        ),
    )


class TestGenerationIdempotency:
    """Verify that deterministic operations produce stable output."""

    def test_board_fingerprint_is_stable(self):
        """Same action board state produces same fingerprint twice."""
        from plugin_examples.planner_loop import board_fingerprint
        from plugin_examples.portfolio_action_planner import Action, ActionBoard

        action = Action(
            id="TEST_ACTION",
            type="PORTFOLIO_CONSERVATION_CHECK",
            family="cells",
            current_state="ready",
            desired_state="checked",
            safe_to_execute_now=True,
            gate_present=False,
        )
        board = object.__new__(ActionBoard)
        board.generated_from_head = "abc123"
        board.git_dirty_summary = ""
        board.actions = [action]
        board.generated_at = "2026-01-01T00:00:00Z"
        board.dirty_categories = {}

        fp1 = board_fingerprint(board)
        fp2 = board_fingerprint(board)
        assert fp1 == fp2, "Board fingerprint must be stable across calls"

    def test_run_history_save_is_idempotent(self, tmp_path: Path):
        """Saving run history twice produces identical file content."""
        from plugin_examples.state.run_history import RunHistory, RunRecord

        path = tmp_path / "history.json"
        h = RunHistory.load(path)
        record = RunRecord(
            family="cells", wave="26", verdict="PASS",
            timestamp="2026-06-10T00:00:00+00:00",
        )
        h.record_run(record)
        h.save()
        content1 = path.read_text(encoding="utf-8")
        data1 = json.loads(content1)

        # Load and save again — structure should be stable
        h2 = RunHistory.load(path)
        h2.save()
        content2 = path.read_text(encoding="utf-8")
        data2 = json.loads(content2)

        assert data1["runs"] == data2["runs"], "Run records must be stable across save/load"
        assert data1["record_count"] == data2["record_count"]

    def test_evidence_chain_validator_deterministic(self, tmp_path: Path):
        """Same gate results produce same validation output."""
        from plugin_examples.fixture_factory.evidence_chain_validators import (
            run_all_ecv_validators,
        )

        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()
        (evidence_dir / "g1.json").write_text(
            json.dumps({"verdict": "PASS"}), encoding="utf-8"
        )

        gates = [{
            "gate_id": "G1",
            "evidence_path": "g1.json",
            "verdict": "PASS",
            "timestamp": "2026-06-10T12:00:00+00:00",
        }]

        results1 = run_all_ecv_validators(gates, evidence_dir)
        results2 = run_all_ecv_validators(gates, evidence_dir)

        r1_dicts = [r.to_dict() for r in results1]
        r2_dicts = [r.to_dict() for r in results2]
        assert r1_dicts == r2_dicts, "Validator results must be deterministic"
