"""Tests for RunHistory adaptive deprioritization wiring in run_execution_loop.

Verifies that:
- Actions from a family with >= 3 consecutive failures are deferred
- Actions from a family with < 3 consecutive failures are NOT deferred
- The loop works normally when no history_path is provided
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from plugin_examples.portfolio_action_planner import Action, ActionBoard
from plugin_examples.state.run_history import RunHistory, RunRecord


def _make_board(*actions: Action) -> ActionBoard:
    """Build a minimal ActionBoard with the given actions."""
    return ActionBoard(
        generated_at="2026-06-11T00:00:00Z",
        generated_from_head="abc1234",
        git_dirty_summary="clean",
        actions=list(actions),
    )


def _make_action(family: str, action_id: str = "TEST_ACTION") -> Action:
    """Build a safe, unhandled action for the given family."""
    return Action(
        id=action_id,
        family=family,
        type="TEST_TYPE",
        current_state="DRYRUN",
        desired_state="BUILD_PASS",
        safe_to_execute_now=True,
        gate_present=False,
    )


def _write_history_with_failures(path: Path, family: str, failure_count: int) -> None:
    """Write a RunHistory JSON with failure_count consecutive failures for family."""
    history = RunHistory(path)
    for i in range(failure_count):
        history.record_run(RunRecord(
            family=family,
            wave=str(i + 1),
            verdict="FAIL",
        ))
    history.save()


class TestDeprioritizationWiring:
    """Verify should_deprioritize() is called and causes deferral in run_execution_loop."""

    def test_family_with_3_failures_is_deferred(self, tmp_path: Path) -> None:
        """Action from family with >= 3 consecutive failures is deferred, not executed."""
        from plugin_examples.planner_loop import run_execution_loop

        history_path = tmp_path / "run-history.json"
        evidence_dir = tmp_path / "evidence"
        _write_history_with_failures(history_path, "cells", failure_count=3)

        cells_action = _make_action("cells", "CELLS_TEST_ACTION")
        board = _make_board(cells_action)

        with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
            result = run_execution_loop(
                repo_root=tmp_path,
                evidence_dir=evidence_dir,
                max_cycles=1,
                history_path=history_path,
            )

        # The action must appear in deferred, NOT in executed
        all_deferred = [d for cycle in result.cycles for d in cycle.deferred]
        all_executed = [e for cycle in result.cycles for e in cycle.executed]

        assert "CELLS_TEST_ACTION" not in all_executed, "Deprioritized action should not be executed"
        deferred_ids = [d["id"] for d in all_deferred]
        assert "CELLS_TEST_ACTION" in deferred_ids, "Deprioritized action should be in deferred list"

        # Verify the reason is exactly correct
        deferred_entry = next(d for d in all_deferred if d["id"] == "CELLS_TEST_ACTION")
        assert deferred_entry["reason"] == "deprioritized_consecutive_failures"
        assert deferred_entry["family"] == "cells"

    def test_family_with_2_failures_is_not_deferred(self, tmp_path: Path) -> None:
        """Action from family with < 3 consecutive failures is NOT deprioritized."""
        from plugin_examples.planner_loop import run_execution_loop

        history_path = tmp_path / "run-history.json"
        evidence_dir = tmp_path / "evidence"
        _write_history_with_failures(history_path, "cells", failure_count=2)

        cells_action = _make_action("cells", "CELLS_TEST_ACTION")
        board = _make_board(cells_action)

        with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
            result = run_execution_loop(
                repo_root=tmp_path,
                evidence_dir=evidence_dir,
                max_cycles=1,
                history_path=history_path,
            )

        all_deferred = [d for cycle in result.cycles for d in cycle.deferred]
        deferred_reasons = {d["id"]: d.get("reason", "") for d in all_deferred}
        assert deferred_reasons.get("CELLS_TEST_ACTION") != "deprioritized_consecutive_failures", (
            "Family with only 2 failures should not be deprioritized"
        )

    def test_no_history_path_does_not_deprioritize(self, tmp_path: Path) -> None:
        """Without history_path, no deprioritization occurs (default behavior unchanged)."""
        from plugin_examples.planner_loop import run_execution_loop

        evidence_dir = tmp_path / "evidence"
        cells_action = _make_action("cells", "CELLS_TEST_ACTION")
        board = _make_board(cells_action)

        with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
            result = run_execution_loop(
                repo_root=tmp_path,
                evidence_dir=evidence_dir,
                max_cycles=1,
                history_path=None,  # No history
            )

        all_deferred = [d for cycle in result.cycles for d in cycle.deferred]
        deprioritized = [d for d in all_deferred if d.get("reason") == "deprioritized_consecutive_failures"]
        assert len(deprioritized) == 0, "No deprioritization should occur without history_path"

    def test_deprioritization_uses_threshold_3(self, tmp_path: Path) -> None:
        """Threshold boundary: exactly 3 failures triggers deprioritization."""
        from plugin_examples.planner_loop import run_execution_loop

        evidence_dir = tmp_path / "evidence"
        for failure_count, should_deprioritize in [(2, False), (3, True), (5, True)]:
            history_path = tmp_path / f"history-{failure_count}.json"
            _write_history_with_failures(history_path, "words", failure_count=failure_count)
            board = _make_board(_make_action("words", "WORDS_TEST"))

            with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
                result = run_execution_loop(
                    repo_root=tmp_path,
                    evidence_dir=tmp_path / f"ev-{failure_count}",
                    max_cycles=1,
                    history_path=history_path,
                )

            all_deferred = [d for cycle in result.cycles for d in cycle.deferred]
            was_deprioritized = any(
                d.get("reason") == "deprioritized_consecutive_failures"
                for d in all_deferred
            )
            assert was_deprioritized == should_deprioritize, (
                f"failure_count={failure_count}: expected deprioritized={should_deprioritize}, got {was_deprioritized}"
            )

    def test_history_saved_after_loop(self, tmp_path: Path) -> None:
        """run_execution_loop saves history when history_path provided."""
        from plugin_examples.planner_loop import run_execution_loop

        history_path = tmp_path / "run-history.json"
        evidence_dir = tmp_path / "evidence"
        board = _make_board()  # empty board — no actions

        with patch("plugin_examples.planner_loop.compute_action_board", return_value=board):
            run_execution_loop(
                repo_root=tmp_path,
                evidence_dir=evidence_dir,
                max_cycles=1,
                history_path=history_path,
            )

        assert history_path.exists(), "History file should be written after loop completes"
        data = json.loads(history_path.read_text())
        assert data.get("version") == 1
        assert data.get("record_count", 0) >= 1
        # Should have a __loop__ summary record
        families = [r["family"] for r in data.get("runs", [])]
        assert "__loop__" in families
