"""Tests for audit trail + compliance trend wiring in planner_loop — TC-S4-07."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from plugin_examples.compliance.audit_trail import AuditTrail
from plugin_examples.planner_loop import run_execution_loop


def _make_fake_board(actions=None):
    """Create a minimal ActionBoard-like object for testing."""
    from types import SimpleNamespace

    if actions is None:
        actions = [
            SimpleNamespace(
                id="PORTFOLIO_CONSERVATION_CHECK",
                type="CONSERVATION_CHECK",
                current_state="needs_recheck",
                safe_to_execute_now=True,
                gate_present=False,
                family="cells",
                blocker=None,
                approval_required=None,
                taskcard_id="TC-TEST-01",
                impact="medium",
            ),
        ]

    board = SimpleNamespace(
        generated_at="2026-06-13T00:00:00Z",
        generated_from_head="abc123",
        git_dirty_summary="clean",
        actions=actions,
        dirty_categories=None,
        notes=[],
        safe_actions=lambda: [a for a in actions if a.safe_to_execute_now],
        blocked_actions=lambda: [a for a in actions if not a.safe_to_execute_now],
        to_json=lambda: json.dumps({"actions": [a.id for a in actions]}),
    )
    return board


class TestAuditTrailWritten:

    def test_audit_trail_written_on_loop_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board()

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1)

            audit_path = evidence_dir / "audit-trail.json"
            assert audit_path.exists(), "audit-trail.json must be written"
            data = json.loads(audit_path.read_text(encoding="utf-8"))
            assert "audit_trail" in data
            assert len(data["audit_trail"]) >= 1

    def test_audit_entry_for_executed_action(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board()

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1)

            data = json.loads((evidence_dir / "audit-trail.json").read_text(encoding="utf-8"))
            entries = data["audit_trail"]
            execute_entries = [e for e in entries if e["decision"] == "EXECUTE"]
            assert len(execute_entries) >= 1
            assert execute_entries[0]["policy_rule"] == "handler_dispatch"

    def test_audit_entry_for_approval_gated_defer(self):
        from types import SimpleNamespace

        action = SimpleNamespace(
            id="MERGE_READY_PR",
            type="MERGE_READY_PR",
            current_state="ready",
            safe_to_execute_now=True,
            gate_present=False,
            family="pdf",
            blocker=None,
            approval_required="APPROVE_MERGE_PR",
            taskcard_id="TC-TEST-02",
            impact="high",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board(actions=[action])

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1, dry_run_remote=True)

            data = json.loads((evidence_dir / "audit-trail.json").read_text(encoding="utf-8"))
            defer_entries = [e for e in data["audit_trail"] if e["decision"] == "DEFER"]
            assert len(defer_entries) >= 1
            assert defer_entries[0]["policy_rule"] == "approval_gated_type"

    def test_audit_entry_for_no_handler_block(self):
        from types import SimpleNamespace

        action = SimpleNamespace(
            id="UNKNOWN_ACTION",
            type="UNKNOWN_TYPE",
            current_state="pending",
            safe_to_execute_now=True,
            gate_present=False,
            family=None,
            blocker=None,
            approval_required=None,
            taskcard_id="",
            impact="low",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board(actions=[action])

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1)

            data = json.loads((evidence_dir / "audit-trail.json").read_text(encoding="utf-8"))
            block_entries = [e for e in data["audit_trail"] if e["decision"] == "BLOCK"]
            assert len(block_entries) >= 1
            assert block_entries[0]["policy_rule"] == "no_registered_handler"


class TestComplianceTrendReport:

    def test_compliance_trend_report_written_with_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            history_path = Path(tmpdir) / "history.json"
            # Create minimal history
            history_data = {
                "records": [
                    {"family": "__loop__", "wave": "1", "timestamp": "",
                     "verdict": "SPRINT_COMPLETE", "test_count": 0,
                     "error_types": [], "duration_seconds": 0.0,
                     "scenarios_attempted": 5, "scenarios_succeeded": 4,
                     "scenarios_blocked": 1},
                ]
            }
            history_path.write_text(json.dumps(history_data), encoding="utf-8")

            board = _make_fake_board()
            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1, history_path=history_path)

            report_path = evidence_dir / "compliance-trend-report.json"
            assert report_path.exists(), "compliance-trend-report.json must be written when history exists"
            data = json.loads(report_path.read_text(encoding="utf-8"))
            assert "trend_direction" in data
            assert data["trend_direction"] in ("improving", "stable", "degrading")

    def test_compliance_trend_not_written_without_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board()

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1)

            report_path = evidence_dir / "compliance-trend-report.json"
            assert not report_path.exists(), "No compliance report without history"


class TestAtomicCheckpoint:

    def test_no_tmp_file_remains_after_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            evidence_dir = Path(tmpdir) / "evidence"
            board = _make_fake_board()

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                run_execution_loop(repo_root, evidence_dir, max_cycles=1)

            tmp_files = list(evidence_dir.glob("*.tmp"))
            assert tmp_files == [], f"Temporary files should not remain: {tmp_files}"
            checkpoint = evidence_dir / "loop-checkpoint.json"
            if checkpoint.exists():
                data = json.loads(checkpoint.read_text(encoding="utf-8"))
                assert "cycle" in data
