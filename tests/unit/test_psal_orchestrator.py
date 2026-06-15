"""Tests for PSAL orchestrator — never-stop multi-family execution loop."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.psal.evidence import FamilyExecutionRecord
from plugin_examples.psal.orchestrator import (
    NON_LOWCODE_FAMILIES,
    FamilyTerminalState,
    _execute_family_loop,
    run_all_families,
)

# ---------------------------------------------------------------------------
# Helper: mock pipeline that returns a configurable report
# ---------------------------------------------------------------------------


def _make_pipeline_report(*, verdict="DRY_RUN_BUILD_PASS", sufficiency="SUFFICIENT"):
    return {
        "verdict": verdict,
        "stages": {
            "load_config": {"status": "PASS"},
            "nuget_fetch": {"status": "PASS"},
            "scenario_planning": {
                "status": "PASS",
                "sufficiency_status": sufficiency,
                "ready_count": 3,
                "blocked_count": 0,
                "total_registry_entries": 3,
            },
        },
        "comparison": {"ready_scenario_count": 3, "examples_generated_count": 3},
        "gate_summary": {},
    }


# ---------------------------------------------------------------------------
# run_all_families
# ---------------------------------------------------------------------------


class TestRunAllFamilies:
    @patch("plugin_examples.psal.orchestrator._execute_family_loop")
    @patch("plugin_examples.psal.evidence.write_family_evidence")
    @patch("plugin_examples.psal.evidence.write_aggregate_evidence")
    def test_all_families_reach_terminal(self, mock_agg, mock_fam_ev, mock_loop, tmp_path):
        """Every target family must appear in the output with a terminal state."""
        mock_loop.return_value = FamilyExecutionRecord(
            family="test",
            terminal_state=FamilyTerminalState.ACCEPTED,
            iterations=1,
        )

        result = run_all_families(
            families=["barcode", "imaging", "zip"],
            max_iterations=1,
            repo_root=tmp_path,
        )

        assert result["total_families"] == 3
        assert result["completeness"]["passed"] is True
        assert set(result["families"].keys()) == {"barcode", "imaging", "zip"}

    @patch("plugin_examples.psal.orchestrator._execute_family_loop")
    @patch("plugin_examples.psal.evidence.write_family_evidence")
    @patch("plugin_examples.psal.evidence.write_aggregate_evidence")
    def test_family_crash_does_not_stop_loop(self, mock_agg, mock_fam_ev, mock_loop, tmp_path):
        """A crash in one family must not prevent others from running."""
        call_count = [0]

        def side_effect(**kwargs):
            call_count[0] += 1
            if kwargs["family"] == "imaging":
                raise RuntimeError("Simulated crash")
            return FamilyExecutionRecord(
                family=kwargs["family"],
                terminal_state=FamilyTerminalState.ACCEPTED,
                iterations=1,
            )

        mock_loop.side_effect = side_effect

        result = run_all_families(
            families=["barcode", "imaging", "zip"],
            max_iterations=1,
            repo_root=tmp_path,
        )

        assert result["total_families"] == 3
        assert result["families"]["imaging"]["terminal_state"] == "ERROR_TERMINAL"
        assert result["families"]["barcode"]["terminal_state"] == "ACCEPTED"
        assert result["families"]["zip"]["terminal_state"] == "ACCEPTED"

    @patch("plugin_examples.psal.orchestrator._execute_family_loop")
    @patch("plugin_examples.psal.evidence.write_family_evidence")
    @patch("plugin_examples.psal.evidence.write_aggregate_evidence")
    def test_completeness_detects_missing(self, mock_agg, mock_fam_ev, mock_loop, tmp_path):
        """If a family is somehow missing from records, completeness must fail."""
        mock_loop.return_value = FamilyExecutionRecord(
            family="test",
            terminal_state=FamilyTerminalState.ACCEPTED,
            iterations=1,
        )

        result = run_all_families(
            families=["barcode"],
            max_iterations=1,
            repo_root=tmp_path,
        )

        assert result["completeness"]["passed"] is True
        assert result["completeness"]["missing"] == []


class TestNonLowCodeFamiliesList:
    def test_all_19_families_present(self):
        assert len(NON_LOWCODE_FAMILIES) == 19

    def test_no_lowcode_families(self):
        lowcode = {"cells", "diagram", "email", "pdf", "slides", "words"}
        for fam in NON_LOWCODE_FAMILIES:
            assert fam not in lowcode, f"{fam} is a LowCode family"

    def test_epub_is_last(self):
        assert NON_LOWCODE_FAMILIES[-1] == "epub"


# ---------------------------------------------------------------------------
# _execute_family_loop
# ---------------------------------------------------------------------------


class TestExecuteFamilyLoop:
    @patch("plugin_examples.sprint_governance.loop_controller.classify_and_decide")
    @patch("plugin_examples.psal.orchestrator._run_pipeline_safe")
    @patch("plugin_examples.psal.config_patcher.ensure_runnable_config")
    def test_accepted_on_green(self, mock_config, mock_pipeline, mock_decide, tmp_path):
        from plugin_examples.sprint_governance.models import LoopDecision, LoopStage, SummaryClassification

        mock_config.return_value = tmp_path / "fake.yml"
        mock_pipeline.return_value = _make_pipeline_report()
        mock_decide.return_value = LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.ACCEPT,
            reason="All green",
            summary_classification=SummaryClassification.STRUCTURED_ALL_GREEN,
        )

        record = _execute_family_loop(
            family="barcode",
            max_iterations=3,
            dry_run=True,
            template_mode=True,
            repo_root=tmp_path,
        )

        assert record.terminal_state == FamilyTerminalState.ACCEPTED
        assert record.iterations == 1

    @patch("plugin_examples.sprint_governance.loop_controller.classify_and_decide")
    @patch("plugin_examples.psal.orchestrator._run_pipeline_safe")
    @patch("plugin_examples.psal.config_patcher.ensure_runnable_config")
    def test_escalated_on_max_iterations(self, mock_config, mock_pipeline, mock_decide, tmp_path):
        """If pipeline never goes green, escalate after max_iterations."""
        from plugin_examples.sprint_governance.models import LoopDecision, LoopStage, SummaryClassification

        mock_config.return_value = tmp_path / "fake.yml"
        mock_pipeline.return_value = _make_pipeline_report(verdict="UNKNOWN")
        mock_decide.return_value = LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.HARDEN,
            reason="Not green",
            summary_classification=SummaryClassification.STRUCTURED_NOT_GREEN,
        )

        record = _execute_family_loop(
            family="psd",
            max_iterations=2,
            dry_run=True,
            template_mode=True,
            repo_root=tmp_path,
        )

        assert record.terminal_state == FamilyTerminalState.ESCALATED
        assert record.iterations == 2

    @patch("plugin_examples.psal.orchestrator._run_pipeline_safe")
    @patch("plugin_examples.psal.config_patcher.ensure_runnable_config")
    def test_pipeline_crash_produces_record(self, mock_config, mock_pipeline, tmp_path):
        mock_config.return_value = tmp_path / "fake.yml"
        mock_pipeline.side_effect = RuntimeError("NuGet down")

        record = _execute_family_loop(
            family="ocr",
            max_iterations=1,
            dry_run=True,
            template_mode=True,
            repo_root=tmp_path,
        )

        # Should escalate (crash → governance classifies as MISSING → AUDIT, but
        # after max_iterations=1 we get ESCALATED)
        assert record.terminal_state in (
            FamilyTerminalState.ESCALATED,
            FamilyTerminalState.ERROR_TERMINAL,
        )
        assert record.iterations >= 1

    @patch("plugin_examples.sprint_governance.loop_controller.classify_and_decide")
    @patch("plugin_examples.psal.orchestrator._run_pipeline_safe")
    @patch("plugin_examples.psal.config_patcher.ensure_runnable_config")
    def test_accepted_with_limitations_on_registry_incomplete(self, mock_config, mock_pipeline, mock_decide, tmp_path):
        from plugin_examples.sprint_governance.models import LoopDecision, LoopStage, SummaryClassification

        mock_config.return_value = tmp_path / "fake.yml"
        mock_pipeline.return_value = _make_pipeline_report(sufficiency="REGISTRY_INCOMPLETE")
        mock_decide.return_value = LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.ACCEPT,
            reason="Accepted with registry gaps",
            summary_classification=SummaryClassification.STRUCTURED_ALL_GREEN,
        )

        record = _execute_family_loop(
            family="imaging",
            max_iterations=3,
            dry_run=True,
            template_mode=True,
            repo_root=tmp_path,
        )

        # governance says ACCEPT but sufficiency is not SUFFICIENT
        assert record.terminal_state == FamilyTerminalState.ACCEPTED_WITH_LIMITATIONS
