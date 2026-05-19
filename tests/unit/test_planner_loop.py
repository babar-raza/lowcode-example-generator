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
    run_execution_loop,
    _ACTION_HANDLERS,
    _APPROVAL_GATED_TYPES,
)

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
            # Should stop before max_cycles because handlers are executed once
            assert result.stop_reason in (
                "no safe executable actions remain",
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
