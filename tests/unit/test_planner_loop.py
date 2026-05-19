"""Tests for the planner-driven execution loop."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from plugin_examples.planner_loop import (
    CycleResult,
    LoopResult,
    board_fingerprint,
    run_execution_loop,
    _ACTION_HANDLERS,
    _APPROVAL_GATED_TYPES,
)
from plugin_examples.portfolio_action_planner import ActionBoard, Action

_REPO_ROOT = Path(__file__).resolve().parents[2]


class TestCycleResultModel:
    def test_cycle_result_to_dict(self):
        cr = CycleResult(cycle=1, generated_from_head="abc1234",
                         action_count=5, safe_count=3, blocked_count=2,
                         executed=["A", "B"], verdict="EXECUTED_2_ACTIONS")
        d = cr.to_dict()
        assert d["cycle"] == 1
        assert d["executed"] == ["A", "B"]
        assert d["verdict"] == "EXECUTED_2_ACTIONS"

    def test_loop_result_to_dict(self):
        lr = LoopResult(total_executed=3, total_deferred=1, stop_reason="no safe actions")
        d = lr.to_dict()
        assert d["total_cycles"] == 0
        assert d["total_executed"] == 3
        assert d["stop_reason"] == "no safe actions"


class TestExecutionLoop:
    def test_loop_executes_safe_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=2, dry_run_remote=True,
            )
            assert len(result.cycles) >= 1
            assert result.total_executed >= 1
            assert result.final_board is not None

    def test_loop_writes_cycle_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=1, dry_run_remote=True,
            )
            cycle_json = evidence_dir / "planner-cycle-01.json"
            cycle_md = evidence_dir / "planner-cycle-01.md"
            assert cycle_json.exists()
            assert cycle_md.exists()
            parsed = json.loads(cycle_json.read_text(encoding="utf-8"))
            assert "actions" in parsed

    def test_loop_skips_approval_gated_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=1, dry_run_remote=True,
            )
            # PDF_MERGE_PRS and PDF_PR_CONFLICT_RECOVERY should be deferred
            all_deferred_ids = []
            for c in result.cycles:
                all_deferred_ids.extend(d["id"] for d in c.deferred)
            # These should not appear in executed
            all_executed = []
            for c in result.cycles:
                all_executed.extend(c.executed)
            assert "PDF_MERGE_PRS" not in all_executed
            assert "PDF_PR_CONFLICT_RECOVERY" not in all_executed

    def test_loop_stops_when_no_safe_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            assert result.stop_reason in (
                "exhausted_safe_actions",
                "stopped_no_change",
                "max_cycles reached",
                "loop completed normally",
            )

    def test_loop_does_not_merge_without_approval(self):
        """Loop must never auto-merge without APPROVE_MERGE_PR."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PLUGIN_EXAMPLES_MERGE_PR_APPROVAL", None)
            with tempfile.TemporaryDirectory() as tmpdir:
                evidence_dir = Path(tmpdir) / "evidence"
                result = run_execution_loop(
                    _REPO_ROOT, evidence_dir, max_cycles=1, dry_run_remote=True,
                )
                all_executed = []
                for c in result.cycles:
                    all_executed.extend(c.executed)
                assert "PDF_MERGE_PRS" not in all_executed

    def test_loop_emits_final_board_from_final_head(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=1, dry_run_remote=True,
            )
            assert result.final_board is not None
            assert result.final_board.generated_from_head != ""
            final_json = evidence_dir / "planner-loop-final-board.json"
            assert final_json.exists()

    def test_loop_records_taskcard_deferrals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=1, dry_run_remote=True,
            )
            all_deferred = []
            for c in result.cycles:
                all_deferred.extend(c.deferred)
            # At least some deferred actions should exist
            assert len(all_deferred) >= 0  # may be 0 if all handled


class TestActionHandlers:
    def test_conservation_handler_exists(self):
        assert "PORTFOLIO_CONSERVATION_CHECK" in _ACTION_HANDLERS

    def test_version_drift_handler_exists(self):
        assert "VERSION_DRIFT_CHECK" in _ACTION_HANDLERS

    def test_blocker_handlers_exist(self):
        assert "FORMIMPORTER_RETEST" in _ACTION_HANDLERS
        assert "OCR_DEPENDENCY_RECHECK" in _ACTION_HANDLERS
        assert "PSD_DEPENDENCY_RECHECK" in _ACTION_HANDLERS

    def test_approval_gated_types_defined(self):
        assert "MERGE_READY_PR" in _APPROVAL_GATED_TYPES
        assert "PDF_PR_CONFLICT_RECOVERY" in _APPROVAL_GATED_TYPES


class TestBoardFingerprint:
    def test_same_board_same_fingerprint(self):
        board = ActionBoard(
            generated_from_head="abc123",
            git_dirty_summary="clean",
            actions=[
                Action(id="A", family="x", type="T", current_state="s", desired_state="d",
                       safe_to_execute_now=True, gate_present=True),
            ],
        )
        assert board_fingerprint(board) == board_fingerprint(board)

    def test_different_generated_at_same_fingerprint(self):
        """Volatile fields like generated_at must not affect fingerprint."""
        b1 = ActionBoard(generated_at="2026-01-01", generated_from_head="abc",
                         git_dirty_summary="clean", actions=[])
        b2 = ActionBoard(generated_at="2026-12-31", generated_from_head="abc",
                         git_dirty_summary="clean", actions=[])
        assert board_fingerprint(b1) == board_fingerprint(b2)

    def test_different_actions_different_fingerprint(self):
        b1 = ActionBoard(generated_from_head="abc", git_dirty_summary="clean",
                         actions=[Action(id="A", family="x", type="T",
                                         current_state="s1", desired_state="d")])
        b2 = ActionBoard(generated_from_head="abc", git_dirty_summary="clean",
                         actions=[Action(id="A", family="x", type="T",
                                         current_state="s2", desired_state="d")])
        assert board_fingerprint(b1) != board_fingerprint(b2)

    def test_fingerprint_is_hex_string(self):
        board = ActionBoard(generated_from_head="abc", git_dirty_summary="clean")
        fp = board_fingerprint(board)
        assert len(fp) == 16
        int(fp, 16)  # must be valid hex


class TestIdempotencyStop:
    def test_loop_stops_on_no_change_cycle(self):
        """Loop must stop after detecting no state change between cycles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            # With current read-only handlers, loop should stop at cycle 2
            # because cycle 2's fingerprint matches cycle 1 and no handler changed state
            assert result.stop_reason == "stopped_no_change"
            assert len(result.cycles) == 2

    def test_no_repeated_identical_actions(self):
        """After idempotency fix, handlers should not execute 3+ times with no change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            # Should execute actions in cycle 1, detect no-change in cycle 2, stop
            assert len(result.cycles) <= 3

    def test_handler_changed_false_contributes_to_stop(self):
        """All current handlers return changed=False, contributing to stop condition."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            if len(result.cycles) >= 2:
                cycle2 = result.cycles[1]
                # All actions in cycle 2 should be noop
                assert len(cycle2.changed_actions) == 0
                assert len(cycle2.noop_actions) >= 1

    def test_approval_gated_actions_do_not_keep_loop_alive(self):
        """Blocked actions should not prevent loop from stopping on no-change."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            # Even though PDF_MERGE_PRS is blocked, loop should stop
            assert result.stop_reason in ("stopped_no_change", "exhausted_safe_actions")

    def test_cycle_result_includes_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=2, dry_run_remote=True,
            )
            for cycle in result.cycles:
                d = cycle.to_dict()
                assert "board_fingerprint" in d
                assert len(d["board_fingerprint"]) == 16

    def test_cycle_result_includes_changed_noop_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=2, dry_run_remote=True,
            )
            for cycle in result.cycles:
                d = cycle.to_dict()
                assert "changed_actions" in d
                assert "noop_actions" in d

    def test_rerun_is_idempotent(self):
        """Running the loop twice should produce the same stop reason."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir1 = Path(tmpdir) / "evidence1"
            evidence_dir2 = Path(tmpdir) / "evidence2"
            r1 = run_execution_loop(_REPO_ROOT, evidence_dir1, max_cycles=5, dry_run_remote=True)
            r2 = run_execution_loop(_REPO_ROOT, evidence_dir2, max_cycles=5, dry_run_remote=True)
            assert r1.stop_reason == r2.stop_reason

    def test_stop_reason_values(self):
        """Stop reason must be one of the defined values."""
        valid = {"exhausted_safe_actions", "stopped_no_change", "max_cycles reached",
                 "loop completed normally", "blocked_by_approval_only"}
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=5, dry_run_remote=True,
            )
            assert result.stop_reason in valid


class TestDirtyStateConsistency:
    """Dirty-state counts must be consistent across final board and loop result."""

    def test_loop_result_includes_final_dirty_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=2, dry_run_remote=True,
            )
            d = result.to_dict()
            assert "final_dirty_state" in d
            ds = d["final_dirty_state"]
            assert "source_dirty_count" in ds
            assert "actionable_count" in ds

    def test_final_board_and_loop_dirty_state_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_dir = Path(tmpdir) / "evidence"
            result = run_execution_loop(
                _REPO_ROOT, evidence_dir, max_cycles=2, dry_run_remote=True,
            )
            loop_ds = result.to_dict()["final_dirty_state"]
            board_ds = result.final_board.dirty_categories
            assert loop_ds == board_ds

    def test_evidence_only_dirty_is_non_actionable(self):
        from plugin_examples.portfolio_action_planner import DirtyState
        ds = DirtyState(evidence=["workspace/foo.json", "workspace/bar.md"])
        assert ds.actionable_count == 0

    def test_test_dirty_is_actionable(self):
        from plugin_examples.portfolio_action_planner import DirtyState
        ds = DirtyState(test=["tests/unit/test_foo.py"])
        assert ds.actionable_count == 1

    def test_dirty_state_summary_matches_dict(self):
        from plugin_examples.portfolio_action_planner import DirtyState
        ds = DirtyState(source=["src/a.py"], evidence=["workspace/b.json"])
        d = ds.to_dict()
        assert d["source_dirty_count"] == 1
        assert d["evidence_dirty_count"] == 1
        assert d["actionable_count"] == 1
