"""Tests for portfolio_action_planner module."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest import mock

import pytest

from plugin_examples.portfolio_action_planner import (
    ACTION_TYPES,
    ACTIVE_FAMILIES,
    BLOCKED_FAMILIES,
    EXECUTION_STATES,
    PERMANENTLY_BLOCKED,
    RECURRING_CHECK_IDS,
    Action,
    ActionBoard,
    DirtyState,
    _classify_dirty_path,
    _parse_porcelain_path,
    compute_action_board,
    render_markdown,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Test Action model
# ---------------------------------------------------------------------------

class TestActionModel:
    def test_action_to_dict_has_required_fields(self):
        a = Action(id="TEST", family="pdf", type="BLOCKER_RETEST",
                   current_state="blocked", desired_state="unblocked")
        d = a.to_dict()
        assert d["id"] == "TEST"
        assert d["family"] == "pdf"
        assert d["type"] == "BLOCKER_RETEST"
        assert "safe_to_execute_now" in d
        assert "impact" in d
        assert "blocker" in d

    def test_action_board_to_json_is_valid(self):
        board = ActionBoard(actions=[
            Action(id="A1", family="cells", type="DENOMINATOR_RECONCILIATION",
                   current_state="x", desired_state="y", impact=50),
        ])
        j = board.to_json()
        parsed = json.loads(j)
        assert len(parsed["actions"]) == 1
        assert parsed["actions"][0]["id"] == "A1"

    def test_safe_actions_filters_correctly(self):
        board = ActionBoard(actions=[
            Action(id="SAFE", family="cells", type="DENOMINATOR_RECONCILIATION",
                   current_state="x", desired_state="y", safe_to_execute_now=True),
            Action(id="BLOCKED", family="pdf", type="MERGE_READY_PR",
                   current_state="x", desired_state="y", safe_to_execute_now=False),
        ])
        assert len(board.safe_actions()) == 1
        assert board.safe_actions()[0].id == "SAFE"
        assert len(board.blocked_actions()) == 1
        assert board.blocked_actions()[0].id == "BLOCKED"


# ---------------------------------------------------------------------------
# Test compute_action_board against real repo
# ---------------------------------------------------------------------------

class TestComputeActionBoard:
    @pytest.fixture(scope="class")
    def board(self):
        return compute_action_board(_REPO_ROOT)

    def test_board_has_actions(self, board):
        assert len(board.actions) >= 1

    def test_actions_sorted_by_impact_descending(self, board):
        impacts = [a.impact for a in board.actions]
        assert impacts == sorted(impacts, reverse=True)

    def test_board_has_notes(self, board):
        assert len(board.notes) >= 1

    def test_board_to_json_roundtrips(self, board):
        j = board.to_json()
        parsed = json.loads(j)
        assert "actions" in parsed
        assert "notes" in parsed

    def test_pdf_merge_action_absent_when_all_published(self, board):
        """PDF_MERGE_PRS should not appear when pr_dry_run_ready_count is 0."""
        ids = [a.id for a in board.actions]
        assert "PDF_MERGE_PRS" not in ids

    def test_formimporter_retest_present(self, board):
        ids = [a.id for a in board.actions]
        assert "FORMIMPORTER_RETEST" in ids

    def test_ocr_dependency_recheck_present(self, board):
        ids = [a.id for a in board.actions]
        assert "OCR_DEPENDENCY_RECHECK" in ids

    def test_psd_dependency_recheck_present(self, board):
        ids = [a.id for a in board.actions]
        assert "PSD_DEPENDENCY_RECHECK" in ids

    def test_permanently_blocked_watch_present(self, board):
        ids = [a.id for a in board.actions]
        assert "PERMANENTLY_BLOCKED_WATCH" in ids

    def test_version_drift_check_present(self, board):
        ids = [a.id for a in board.actions]
        assert "VERSION_DRIFT_CHECK" in ids

    def test_portfolio_conservation_check_present(self, board):
        ids = [a.id for a in board.actions]
        assert "PORTFOLIO_CONSERVATION_CHECK" in ids

    def test_no_silent_drop(self, board):
        """No active family should be absent from the board."""
        families_in_board = {a.family for a in board.actions}
        # pdf and cross-family must be present
        assert "pdf" in families_in_board
        assert "cross-family" in families_in_board


# ---------------------------------------------------------------------------
# Test gate-dependent behavior
# ---------------------------------------------------------------------------

class TestGateBehavior:
    def test_pdf_merge_absent_when_no_pr_ready(self):
        """With pr_dry_run_ready_count=0, PDF_MERGE_PRS is not generated regardless of gate."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PLUGIN_EXAMPLES_MERGE_PR_APPROVAL", None)
            board = compute_action_board(_REPO_ROOT)
            pdf_merge = [a for a in board.actions if a.id == "PDF_MERGE_PRS"]
            assert len(pdf_merge) == 0

    def test_pdf_merge_absent_even_with_gate_present(self):
        """With pr_dry_run_ready_count=0, gate presence doesn't create merge action."""
        with mock.patch.dict(os.environ, {"PLUGIN_EXAMPLES_MERGE_PR_APPROVAL": "APPROVE_MERGE_PR"}):
            board = compute_action_board(_REPO_ROOT)
            pdf_merge = [a for a in board.actions if a.id == "PDF_MERGE_PRS"]
            assert len(pdf_merge) == 0


# ---------------------------------------------------------------------------
# Test dirty state ranking
# ---------------------------------------------------------------------------

class TestDirtyStateRanking:
    def test_dirty_state_ranks_first(self):
        mock_dirty = DirtyState(source=["src/fake_dirty_file.py"])
        with mock.patch("plugin_examples.portfolio_action_planner._check_dirty_state",
                        return_value=mock_dirty):
            board = compute_action_board(_REPO_ROOT)
            assert board.actions[0].id == "CLOSE_DIRTY_STATE"
            assert board.actions[0].impact == 100

    def test_no_dirty_action_when_clean(self):
        mock_dirty = DirtyState()
        with mock.patch("plugin_examples.portfolio_action_planner._check_dirty_state",
                        return_value=mock_dirty):
            board = compute_action_board(_REPO_ROOT)
            ids = [a.id for a in board.actions]
            assert "CLOSE_DIRTY_STATE" not in ids


# ---------------------------------------------------------------------------
# Test contract conservation feed
# ---------------------------------------------------------------------------

class TestContractConservation:
    def test_no_backfill_when_contracts_match_pilot(self):
        """All 6 active families should have contracts == pilot_allowed."""
        board = compute_action_board(_REPO_ROOT)
        backfill_ids = [a.id for a in board.actions if a.type == "CONTRACT_BACKFILL"]
        assert len(backfill_ids) == 0, f"Unexpected backfill needed: {backfill_ids}"


# ---------------------------------------------------------------------------
# Test render_markdown
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def test_render_produces_markdown_table(self):
        board = ActionBoard(actions=[
            Action(id="A1", family="cells", type="DENOMINATOR_RECONCILIATION",
                   current_state="x", desired_state="y", impact=50,
                   safe_to_execute_now=True),
        ])
        md = render_markdown(board)
        assert "| Rank |" in md
        assert "| 1 | A1 |" in md

    def test_render_includes_notes(self):
        board = ActionBoard(notes=["test note"])
        md = render_markdown(board)
        assert "- test note" in md


# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_active_families_count(self):
        assert len(ACTIVE_FAMILIES) == 6

    def test_blocked_families_count(self):
        assert len(BLOCKED_FAMILIES) == 2

    def test_permanently_blocked_contains_known_roots(self):
        assert "pdf/Timestamp" in PERMANENTLY_BLOCKED
        assert "pdf/Ofd" in PERMANENTLY_BLOCKED
        assert "words/Processor" in PERMANENTLY_BLOCKED

    def test_email_and_slides_in_active(self):
        assert "email" in ACTIVE_FAMILIES
        assert "slides" in ACTIVE_FAMILIES

    def test_conflict_recovery_in_action_types(self):
        assert "PDF_PR_CONFLICT_RECOVERY" in ACTION_TYPES


# ---------------------------------------------------------------------------
# Test v2 freshness metadata
# ---------------------------------------------------------------------------

class TestFreshnessMetadata:
    def test_board_has_generated_from_head(self):
        board = compute_action_board(_REPO_ROOT)
        assert board.generated_from_head != ""
        assert len(board.generated_from_head) >= 7  # short SHA

    def test_board_has_git_dirty_summary(self):
        board = compute_action_board(_REPO_ROOT)
        assert isinstance(board.git_dirty_summary, str)
        assert len(board.git_dirty_summary) > 0

    def test_freshness_in_json_output(self):
        board = compute_action_board(_REPO_ROOT)
        parsed = json.loads(board.to_json())
        assert "generated_from_head" in parsed
        assert "git_dirty_summary" in parsed

    def test_freshness_in_markdown(self):
        board = compute_action_board(_REPO_ROOT)
        md = render_markdown(board)
        assert "HEAD:" in md
        assert "Dirty:" in md


# ---------------------------------------------------------------------------
# Test v2 conflict recovery action
# ---------------------------------------------------------------------------

class TestConflictRecoveryAction:
    def test_conflict_recovery_absent_when_all_published(self):
        """PDF_PR_CONFLICT_RECOVERY should not appear when pr_dry_run_ready_count is 0."""
        board = compute_action_board(_REPO_ROOT)
        ids = [a.id for a in board.actions]
        assert "PDF_PR_CONFLICT_RECOVERY" not in ids

    def test_conflict_recovery_absent_regardless_of_gate(self):
        """With pr_dry_run_ready_count=0, gate presence doesn't create conflict recovery."""
        with mock.patch.dict(os.environ, {"PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL": "APPROVE_LIVE_PR"}):
            board = compute_action_board(_REPO_ROOT)
            cr = [a for a in board.actions if a.id == "PDF_PR_CONFLICT_RECOVERY"]
            assert len(cr) == 0


# ---------------------------------------------------------------------------
# Test v2 taskcard IDs
# ---------------------------------------------------------------------------

class TestTaskcardIds:
    def test_blocker_actions_have_taskcard_ids(self):
        board = compute_action_board(_REPO_ROOT)
        formimporter = [a for a in board.actions if a.id == "FORMIMPORTER_RETEST"][0]
        assert formimporter.taskcard_id == "TC-PDF-FORMIMPORTER-RETEST"
        ocr = [a for a in board.actions if a.id == "OCR_DEPENDENCY_RECHECK"][0]
        assert ocr.taskcard_id == "TC-OCR-REFLECTION"
        psd = [a for a in board.actions if a.id == "PSD_DEPENDENCY_RECHECK"][0]
        assert psd.taskcard_id == "TC-PSD-REFLECTION"

    def test_taskcard_id_omitted_from_dict_when_none(self):
        a = Action(id="X", family="cells", type="BLOCKER_RETEST",
                   current_state="x", desired_state="y")
        d = a.to_dict()
        assert "taskcard_id" not in d

    def test_taskcard_id_present_in_dict_when_set(self):
        a = Action(id="X", family="pdf", type="BLOCKER_RETEST",
                   current_state="x", desired_state="y",
                   taskcard_id="TC-TEST")
        d = a.to_dict()
        assert d["taskcard_id"] == "TC-TEST"


# ---------------------------------------------------------------------------
# Test v2 metrics summary
# ---------------------------------------------------------------------------

class TestMetricsSummary:
    def test_metrics_summary_structure(self):
        board = compute_action_board(_REPO_ROOT)
        m = board.metrics_summary()
        assert "generated_at" in m
        assert "generated_from_head" in m
        assert "total_actions" in m
        assert "safe_count" in m
        assert "blocked_count" in m
        assert "action_ids" in m
        assert "blocked_ids" in m
        assert "max_impact" in m

    def test_metrics_counts_consistent(self):
        board = compute_action_board(_REPO_ROOT)
        m = board.metrics_summary()
        assert m["total_actions"] == m["safe_count"] + m["blocked_count"]
        assert m["total_actions"] == len(m["action_ids"])


# ---------------------------------------------------------------------------
# Test v3 dirty-state categorization
# ---------------------------------------------------------------------------

class TestDirtyStateCategorization:
    def test_source_file_classified_as_source(self):
        assert _classify_dirty_path("src/plugin_examples/foo.py") == "source"

    def test_config_file_classified_as_config(self):
        assert _classify_dirty_path("pipeline/configs/denominators/cells.json") == "config"
        assert _classify_dirty_path("pipeline/contracts/pdf/merger.json") == "config"
        assert _classify_dirty_path(".gitignore") == "config"

    def test_test_file_classified_as_test(self):
        assert _classify_dirty_path("tests/unit/test_foo.py") == "test"

    def test_evidence_file_classified_as_evidence(self):
        assert _classify_dirty_path("workspace/verification/latest/release-status.json") == "evidence"

    def test_artifact_file_classified_as_artifact(self):
        assert _classify_dirty_path("output.pdf") == "artifact"
        assert _classify_dirty_path("input.pdf") == "artifact"
        assert _classify_dirty_path("output.jpg/") == "artifact"
        assert _classify_dirty_path("leg.zip") == "artifact"
        assert _classify_dirty_path("test.pfx") == "artifact"
        assert _classify_dirty_path("output.json") == "artifact"

    def test_unknown_file_defaults_to_unknown(self):
        assert _classify_dirty_path("pyproject.toml") == "unknown"

    def test_package_artifact_classified(self):
        assert _classify_dirty_path("workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/jpeg/input.pdf") == "package_artifact"
        assert _classify_dirty_path("workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/test.pfx") == "package_artifact"

    def test_package_artifact_does_not_create_close_dirty_state(self):
        dirty = DirtyState(package_artifact=["workspace/pr-dry-run/foo/input.pdf"])
        assert dirty.actionable_count == 0

    def test_artifacts_do_not_create_close_dirty_state(self):
        dirty = DirtyState(artifact=["output.pdf", "input.pdf", "leg.zip"])
        assert dirty.actionable_count == 0

    def test_evidence_does_not_create_close_dirty_state(self):
        dirty = DirtyState(evidence=["workspace/verification/latest/foo.json"])
        assert dirty.actionable_count == 0

    def test_source_creates_close_dirty_state(self):
        dirty = DirtyState(source=["src/foo.py"])
        assert dirty.actionable_count == 1

    def test_config_creates_close_dirty_state(self):
        dirty = DirtyState(config=["pipeline/configs/denominators/cells.json"])
        assert dirty.actionable_count == 1

    def test_test_creates_close_dirty_state(self):
        dirty = DirtyState(test=["tests/unit/test_foo.py"])
        assert dirty.actionable_count == 1

    def test_mixed_dirty_state_summary(self):
        dirty = DirtyState(
            source=["src/a.py"], config=["pipeline/configs/x.json"],
            evidence=["workspace/foo.json"], artifact=["output.pdf"]
        )
        s = dirty.summary()
        assert "1 source" in s
        assert "1 config" in s
        assert "1 evidence" in s
        assert "1 artifact" in s
        assert dirty.actionable_count == 2

    def test_dirty_state_to_dict_has_all_counts(self):
        dirty = DirtyState(source=["a.py"], test=["t.py"], artifact=["o.pdf"],
                           package_artifact=["workspace/pr-dry-run/x/input.pdf"])
        d = dirty.to_dict()
        assert d["source_dirty_count"] == 1
        assert d["config_dirty_count"] == 0
        assert d["test_dirty_count"] == 1
        assert d["evidence_dirty_count"] == 0
        assert d["generated_artifact_count"] == 1
        assert d["package_artifact_count"] == 1
        assert d["unknown_dirty_count"] == 0
        assert d["actionable_count"] == 2
        assert d["package_artifact_files"] == ["workspace/pr-dry-run/x/input.pdf"]

    def test_board_includes_dirty_categories_in_json(self):
        board = compute_action_board(_REPO_ROOT)
        parsed = json.loads(board.to_json())
        if parsed.get("dirty_categories"):
            assert "source_dirty_count" in parsed["dirty_categories"]
            assert "actionable_count" in parsed["dirty_categories"]

    def test_evidence_only_dirty_no_close_action(self):
        """Only evidence/artifact dirty should NOT produce CLOSE_DIRTY_STATE."""
        dirty = DirtyState(evidence=["workspace/foo.json"], artifact=["output.pdf"])
        with mock.patch("plugin_examples.portfolio_action_planner._check_dirty_state",
                        return_value=dirty):
            board = compute_action_board(_REPO_ROOT)
            ids = [a.id for a in board.actions]
            assert "CLOSE_DIRTY_STATE" not in ids


class TestPorcelainPathParsing:
    def test_parse_modified_worktree(self):
        assert _parse_porcelain_path(" M src/foo.py") == "src/foo.py"

    def test_parse_staged(self):
        assert _parse_porcelain_path("M  src/foo.py") == "src/foo.py"

    def test_parse_untracked(self):
        assert _parse_porcelain_path("?? output.pdf") == "output.pdf"

    def test_parse_rename(self):
        assert _parse_porcelain_path("R  old.py -> new.py") == "new.py"

    def test_parse_short_line(self):
        assert _parse_porcelain_path("") == ""
        assert _parse_porcelain_path("M") == ""


# ---------------------------------------------------------------------------
# Test execution state semantics
# ---------------------------------------------------------------------------

class TestExecutionStateSemantics:
    """Verify planner distinguishes executed no-op checks from required next actions."""

    def test_recurring_check_ids_are_defined(self):
        assert len(RECURRING_CHECK_IDS) >= 5

    def test_execution_states_are_defined(self):
        assert "safe_unexecuted" in EXECUTION_STATES
        assert "recurring_check_satisfied" in EXECUTION_STATES
        assert "blocked_by_approval" in EXECUTION_STATES

    def test_mark_executed_noop_recurring_check(self):
        board = ActionBoard()
        board.actions = [
            Action(
                id="PORTFOLIO_CONSERVATION_CHECK",
                family="cross-family",
                type="DENOMINATOR_RECONCILIATION",
                current_state="needs check",
                desired_state="verified",
                safe_to_execute_now=True,
            ),
        ]
        board.mark_executed("PORTFOLIO_CONSERVATION_CHECK", changed=False, cycle=1)
        a = board.actions[0]
        assert a.execution_state == "recurring_check_satisfied"
        assert a.next_required is False
        assert a.executed_this_sprint is True

    def test_mark_executed_with_change(self):
        board = ActionBoard()
        board.actions = [
            Action(
                id="PORTFOLIO_CONSERVATION_CHECK",
                family="cross-family",
                type="DENOMINATOR_RECONCILIATION",
                current_state="needs check",
                desired_state="verified",
                safe_to_execute_now=True,
            ),
        ]
        board.mark_executed("PORTFOLIO_CONSERVATION_CHECK", changed=True, cycle=1)
        a = board.actions[0]
        assert a.execution_state == "safe_executed_changed"
        assert a.next_required is True  # changed state means re-check needed

    def test_approval_blocked_remains_next_required(self):
        a = Action(
            id="PDF_MERGE_PRS",
            family="pdf",
            type="MERGE_READY_PR",
            current_state="14 PR-ready",
            desired_state="published",
            safe_to_execute_now=False,
            approval_required="APPROVE_MERGE_PR",
            gate_present=False,
            execution_state="blocked_by_approval",
        )
        assert a.next_required is True

    def test_next_required_actions_excludes_executed_noops(self):
        board = ActionBoard()
        board.actions = [
            Action(id="VERSION_DRIFT_CHECK", family="x", type="VERSION_DRIFT_RERUN",
                   current_state="", desired_state="", safe_to_execute_now=True),
            Action(id="PDF_MERGE_PRS", family="pdf", type="MERGE_READY_PR",
                   current_state="", desired_state="", safe_to_execute_now=False,
                   approval_required="APPROVE_MERGE_PR", execution_state="blocked_by_approval"),
        ]
        board.mark_executed("VERSION_DRIFT_CHECK", changed=False, cycle=1)
        required = board.next_required_actions()
        ids = [a.id for a in required]
        assert "VERSION_DRIFT_CHECK" not in ids
        assert "PDF_MERGE_PRS" in ids

    def test_design_review_blocked_visible_not_safe(self):
        a = Action(
            id="CONTRACT_FIRST_CODEGEN",
            family="cross-family",
            type="GOVERNANCE_HARDENING",
            current_state="not implemented",
            desired_state="contract-first codegen",
            safe_to_execute_now=False,
            taskcard_id="TC-CONTRACT-FIRST-CODEGEN",
            execution_state="blocked_by_design_review",
        )
        assert a.next_required is True
        assert a.safe_to_execute_now is False

    def test_action_to_dict_includes_execution_state(self):
        a = Action(id="TEST", family="x", type="TEST",
                   current_state="", desired_state="",
                   execution_state="recurring_check_satisfied",
                   executed_this_sprint=True, next_required=False)
        d = a.to_dict()
        assert d["execution_state"] == "recurring_check_satisfied"
        assert d["executed_this_sprint"] is True
        assert d["next_required"] is False

    def test_board_blocked_actions_have_execution_state(self):
        dirty = DirtyState()
        with mock.patch("plugin_examples.portfolio_action_planner._check_dirty_state",
                        return_value=dirty), \
             mock.patch("plugin_examples.portfolio_action_planner._get_head_sha",
                        return_value="abc1234"):
            board = compute_action_board(_REPO_ROOT)
            for a in board.blocked_actions():
                assert a.execution_state.startswith("blocked_by_"), \
                    f"{a.id} has execution_state={a.execution_state}"
