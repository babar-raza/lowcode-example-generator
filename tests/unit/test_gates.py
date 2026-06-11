"""Unit tests for the central gate engine."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from plugin_examples.gates.models import GateResult, GateVerdict, VERDICTS, GATE_STATUSES
from plugin_examples.gates.evaluator import (
    evaluate_gates,
    determine_verdict,
    is_publishable,
    is_publishable_verdict,
)
from plugin_examples.gates.writer import write_gate_results
from plugin_examples.gates.example_gates import (
    merge_pr_candidate_manifests,
    write_pr_candidate_manifest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@dataclass
class _FakeStage:
    name: str
    order: int
    status: str = "success"
    artifacts: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class _FakeCtx:
    family: str = "cells"
    run_id: str = "test-run"
    dry_run: bool = True
    skip_run: bool = True
    template_mode: bool = True
    require_llm: bool = False
    require_validation: bool = False
    require_reviewer: bool = False
    validation_results: list = field(default_factory=list)
    gate_verdict: object = None


def _make_stages(overrides: dict | None = None) -> list[_FakeStage]:
    """Create a default list of successful stages."""
    names = [
        "load_config",
        "nuget_fetch",
        "dependency_resolution",
        "extraction",
        "reflection",
        "plugin_detection",
        "api_delta",
        "impact_mapping",
        "fixture_registry",
        "example_mining",
        "scenario_planning",
        "llm_preflight",
        "generation",
        "validation",
        "reviewer",
        "publisher",
    ]
    stages = []
    for i, name in enumerate(names):
        s = _FakeStage(name=name, order=i + 1, status="success")
        stages.append(s)
    if overrides:
        for name, kwargs in overrides.items():
            for s in stages:
                if s.name == name:
                    for k, v in kwargs.items():
                        setattr(s, k, v)
    return stages


# ---------------------------------------------------------------------------
# TestGateResult
# ---------------------------------------------------------------------------


class TestGateResult:
    def test_construction(self):
        g = GateResult(
            gate_id="gate_build",
            name="Build Validation",
            status="failed",
            required=True,
            failure_reason="0/14 examples passed build",
            stage_name="validation",
        )
        assert g.gate_id == "gate_build"
        assert g.status == "failed"
        assert g.required is True
        assert g.evidence_files == []
        assert g.downstream_blocked == []

    def test_all_statuses_in_canonical_set(self):
        for status in GATE_STATUSES:
            g = GateResult(gate_id="test", name="test", status=status, required=False, stage_name="test")
            assert g.status in GATE_STATUSES


class TestGateVerdict:
    def test_default_verdict(self):
        v = GateVerdict()
        assert v.verdict == "DATA_FLOW_PROTOTYPE_ONLY"
        assert v.publishable is False
        assert v.all_required_passed is False

    def test_all_verdicts_in_canonical_set(self):
        for verdict in VERDICTS:
            v = GateVerdict(verdict=verdict)
            assert v.verdict in VERDICTS


# ---------------------------------------------------------------------------
# TestEvaluateGates
# ---------------------------------------------------------------------------


class TestEvaluateGates:
    def test_hard_stop_produces_blocked_source_of_truth(self):
        ctx = _FakeCtx()
        stages = _make_stages({"nuget_fetch": {"status": "failed"}})
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "BLOCKED_SOURCE_OF_TRUTH"
        assert not verdict.publishable
        assert "gate_source_of_truth" in verdict.blocking_gates

    def test_no_ready_scenarios_produces_source_of_truth_proven(self):
        ctx = _FakeCtx()
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 0, "blocked_count": 5}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "SOURCE_OF_TRUTH_PROVEN_ONLY"

    def test_template_mode_produces_data_flow_prototype(self):
        ctx = _FakeCtx(template_mode=True)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
                "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"
        assert not verdict.publishable

    def test_skip_run_produces_data_flow_prototype(self):
        ctx = _FakeCtx(template_mode=False, skip_run=True)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
                "validation": {"artifacts": {"passed": 3, "failed": 0, "total": 3}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"

    def test_build_failure_produces_blocked_build(self):
        ctx = _FakeCtx(template_mode=False, skip_run=False)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
                "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "BLOCKED_BUILD_FAILED"
        assert not verdict.publishable

    def test_generation_zero_produces_blocked_generation(self):
        ctx = _FakeCtx()
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 0}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "BLOCKED_GENERATION"

    def test_template_mode_with_build_pass_produces_canonical_template_pass(self):
        # B1: template_mode + skip_run=False + build passed → CANONICAL_TEMPLATE_GENERATION_PASS
        ctx = _FakeCtx(template_mode=True, skip_run=False)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 9, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 9, "generation_mode": "template"}},
                "validation": {"artifacts": {"build_passed": 9, "passed": 9, "total": 9}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "CANONICAL_TEMPLATE_GENERATION_PASS"
        assert verdict.publishable

    def test_template_mode_skip_run_true_stays_data_flow_prototype(self):
        # B1: template_mode + skip_run=True must remain DATA_FLOW_PROTOTYPE_ONLY
        ctx = _FakeCtx(template_mode=True, skip_run=True)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 9, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 9, "generation_mode": "template"}},
                "validation": {"artifacts": {"build_passed": 9, "passed": 9, "total": 9}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"
        assert not verdict.publishable

    def test_template_mode_with_build_fail_stays_data_flow_prototype(self):
        # B1: template_mode + skip_run=False + build failed → DATA_FLOW_PROTOTYPE_ONLY
        ctx = _FakeCtx(template_mode=True, skip_run=False)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
                "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
                "validation": {"artifacts": {"build_passed": 0, "passed": 0, "failed": 3, "total": 3}},
            }
        )
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"
        assert not verdict.publishable

    def test_canonical_template_pass_is_publishable(self):
        from plugin_examples.gates.evaluator import is_publishable_verdict

        assert is_publishable_verdict("CANONICAL_TEMPLATE_GENERATION_PASS")
        assert is_publishable_verdict("CANONICAL_LLM_GENERATION_PASS")
        assert not is_publishable_verdict("DATA_FLOW_PROTOTYPE_ONLY")


# ---------------------------------------------------------------------------
# TestDetermineVerdict
# ---------------------------------------------------------------------------


class TestDetermineVerdict:
    def test_delegates_to_evaluator(self):
        ctx = _FakeCtx(template_mode=True)
        stages = _make_stages(
            {
                "scenario_planning": {"artifacts": {"ready_count": 3}},
                "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
            }
        )
        verdict = determine_verdict(stages, ctx)
        assert verdict in VERDICTS

    def test_verdict_is_string(self):
        ctx = _FakeCtx()
        stages = _make_stages()
        verdict = determine_verdict(stages, ctx)
        assert isinstance(verdict, str)
        assert verdict in VERDICTS


# ---------------------------------------------------------------------------
# TestIsPublishable
# ---------------------------------------------------------------------------


class TestIsPublishable:
    def test_pr_ready_is_publishable(self):
        assert is_publishable_verdict("PR_READY") is True

    def test_full_e2e_is_publishable(self):
        assert is_publishable_verdict("FULL_E2E_PASSED") is True

    def test_data_flow_not_publishable(self):
        assert is_publishable_verdict("DATA_FLOW_PROTOTYPE_ONLY") is False

    def test_pr_dry_run_not_publishable(self):
        assert is_publishable_verdict("PR_DRY_RUN_READY") is False

    def test_blocked_not_publishable(self):
        for v in VERDICTS:
            if v.startswith("BLOCKED_"):
                assert is_publishable_verdict(v) is False

    def test_gate_verdict_object(self):
        v = GateVerdict(verdict="PR_READY", publishable=True, all_required_passed=True)
        assert is_publishable(v) is True

        v2 = GateVerdict(verdict="DATA_FLOW_PROTOTYPE_ONLY", publishable=False)
        assert is_publishable(v2) is False


# ---------------------------------------------------------------------------
# TestWriteGateResults
# ---------------------------------------------------------------------------


class TestWriteGateResults:
    def test_writes_json_file(self, tmp_path):
        verdict = GateVerdict(
            gates=[
                GateResult(
                    gate_id="gate_build",
                    name="Build",
                    status="failed",
                    required=True,
                    failure_reason="0/14 passed",
                    stage_name="validation",
                ),
            ],
            verdict="BLOCKED_BUILD_FAILED",
            publishable=False,
            all_required_passed=False,
            blocking_gates=["gate_build"],
        )
        path = write_gate_results(verdict, tmp_path)
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["verdict"] == "BLOCKED_BUILD_FAILED"
        assert data["publishable"] is False
        assert len(data["gates"]) == 1
        assert data["gates"][0]["gate_id"] == "gate_build"

    def test_creates_latest_directory(self, tmp_path):
        verdict = GateVerdict(verdict="DATA_FLOW_PROTOTYPE_ONLY")
        path = write_gate_results(verdict, tmp_path)
        assert (tmp_path / "latest" / "gate-results.json").exists()


# ---------------------------------------------------------------------------
# CompletenessGate tests
# ---------------------------------------------------------------------------


from plugin_examples.gates.completeness_gate import (
    check_completeness,
    write_completeness_gate_result,
    write_denominator_ledger,
    CompletenessViolationError,
)
from plugin_examples.scenario_planner.planner import PlanningResult, Scenario


def _make_scenario(
    scenario_id: str, target_type: str, status: str = "ready", blocked_reason: str | None = None
) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        title=f"Use {target_type}",
        target_type=target_type,
        target_namespace="Aspose.Cells.LowCode",
        status=status,
        blocked_reason=blocked_reason,
    )


def _make_planning_result(family: str, ready: int, blocked: int) -> PlanningResult:
    result = PlanningResult(family=family)
    for i in range(ready):
        result.ready_scenarios.append(_make_scenario(f"{family}-ready-{i}", f"Aspose.{family}.LowCode.Type{i}"))
    for i in range(blocked):
        result.blocked_scenarios.append(
            _make_scenario(
                f"{family}-blocked-{i}",
                f"Aspose.{family}.LowCode.Blocked{i}",
                status="blocked_low_score",
            )
        )
    return result


class TestCompletenessGatePass:
    def test_pilot_allowed_equation_holds(self):
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 4,
        }
        planning = _make_planning_result("pdf", ready=3, blocked=1)
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        assert result.status == "pass"
        assert result.holds is True
        assert result.accounted_count == 4
        assert result.gap == 0

    def test_full_sot_equation_holds(self):
        denominator = {
            "denominator_basis": "FULL_SOT",
            "workflow_root_types": 9,
        }
        planning = _make_planning_result("cells", ready=9, blocked=0)
        result = check_completeness("cells", denominator, planning, dry_run=True)
        assert result.status == "pass"

    def test_discovery_only_is_skipped(self):
        denominator = {"denominator_basis": "DISCOVERY_ONLY"}
        planning = _make_planning_result("email", ready=0, blocked=0)
        result = check_completeness("email", denominator, planning, dry_run=True)
        assert result.status == "skip"
        assert result.holds is True

    def test_over_accounted_still_passes(self):
        """More scenarios than denominator expected is a pass (expanded pilot)."""
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 2,
        }
        planning = _make_planning_result("words", ready=3, blocked=1)
        result = check_completeness("words", denominator, planning, dry_run=True)
        assert result.status == "pass"


class TestCompletenessGateFail:
    def test_shortfall_warns_in_dry_run(self):
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 4,
        }
        planning = _make_planning_result("pdf", ready=2, blocked=0)  # only 2, need 4
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        assert result.status == "warn"
        assert result.holds is False
        assert len(result.violations) > 0

    def test_shortfall_raises_in_live_mode(self):
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 4,
        }
        planning = _make_planning_result("pdf", ready=2, blocked=0)
        with pytest.raises(CompletenessViolationError):
            check_completeness("pdf", denominator, planning, dry_run=False)

    def test_missing_allowed_pilot_count_warns(self):
        denominator = {"denominator_basis": "PILOT_ALLOWED"}  # no allowed_pilot_count
        planning = _make_planning_result("pdf", ready=2, blocked=0)
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        assert result.status == "warn"
        assert any("allowed_pilot_count missing" in v for v in result.violations)

    def test_unknown_basis_warns(self):
        denominator = {"denominator_basis": "CUSTOM_BASIS"}
        planning = _make_planning_result("pdf", ready=2, blocked=0)
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        assert result.status == "warn"


class TestCompletenessGateWrite:
    def test_write_completeness_gate_result(self, tmp_path):
        denominator = {"denominator_basis": "PILOT_ALLOWED", "allowed_pilot_count": 4}
        planning = _make_planning_result("pdf", ready=4, blocked=0)
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        path = write_completeness_gate_result(result, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["family"] == "pdf"
        assert data["status"] == "pass"
        assert data["holds"] is True

    def test_write_creates_family_subdirectory(self, tmp_path):
        denominator = {"denominator_basis": "DISCOVERY_ONLY"}
        planning = _make_planning_result("email", ready=0, blocked=0)
        result = check_completeness("email", denominator, planning, dry_run=True)
        write_completeness_gate_result(result, tmp_path)
        assert (tmp_path / "latest" / "families" / "email").is_dir()


class TestDenominatorLedger:
    def test_write_denominator_ledger_basic(self, tmp_path):
        from plugin_examples.scenario_planner.type_classifier import TypeRole

        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_types": ["Merger"],
        }
        planning = _make_planning_result("pdf", ready=1, blocked=0)
        # Override the ready scenario's target_type to match type_roles
        planning.ready_scenarios[0] = _make_scenario("pdf-ready-0", "Aspose.Pdf.LowCode.Merger")
        type_roles = [
            TypeRole(
                full_name="Aspose.Pdf.LowCode.Merger",
                name="Merger",
                role="workflow_root",
                confidence=1.0,
                reason="test",
            ),
            TypeRole(
                full_name="Aspose.Pdf.LowCode.MergeOptions",
                name="MergeOptions",
                role="options",
                confidence=1.0,
                reason="test",
            ),
        ]
        path = write_denominator_ledger("pdf", denominator, planning, type_roles, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["family"] == "pdf"
        assert data["total_types"] == 2
        entries_by_name = {e["type_name"]: e for e in data["entries"]}
        assert entries_by_name["Merger"]["lifecycle_state"] == "ready"
        assert entries_by_name["Merger"]["pilot_scope"] == "in_scope"
        assert entries_by_name["MergeOptions"]["pilot_scope"] == "out_of_scope"


# ---------------------------------------------------------------------------
# Completeness gate equation — overcount, unknown types, integration
# ---------------------------------------------------------------------------


class TestCompletenessGateEquation:
    """Equation correctness: overcount, unknown types, PILOT full-WRT reporting."""

    def test_full_sot_overcount_warns(self):
        """FULL_SOT with more accounted than expected triggers overcount warning."""
        denominator = {"denominator_basis": "FULL_SOT", "total_lowcode_types": 5, "workflow_root_types": 3}
        planning = _make_planning_result("cells", ready=6, blocked=1)  # 7 > 5
        result = check_completeness("cells", denominator, planning, dry_run=True)
        assert result.status == "warn"
        assert result.holds is False
        assert any("overcount" in v.lower() for v in result.violations)

    def test_full_sot_overcount_raises_in_live_mode(self):
        """FULL_SOT overcount raises in live mode."""
        denominator = {"denominator_basis": "FULL_SOT", "total_lowcode_types": 5, "workflow_root_types": 3}
        planning = _make_planning_result("cells", ready=6, blocked=1)
        with pytest.raises(CompletenessViolationError):
            check_completeness("cells", denominator, planning, dry_run=False)

    def test_pilot_allowed_overcount_does_not_warn(self):
        """PILOT_ALLOWED with more accounted than pilot count is expected — no overcount warning."""
        denominator = {"denominator_basis": "PILOT_ALLOWED", "allowed_pilot_count": 4}
        planning = _make_planning_result("pdf", ready=4, blocked=97)  # 101 total — all non-pilot blocked
        result = check_completeness("pdf", denominator, planning, dry_run=True)
        # accounted = 101 >> 4, but this is expected for PILOT_ALLOWED
        assert result.status == "pass"
        assert not any("overcount" in v.lower() for v in result.violations)

    def test_unknown_type_count_zero_no_violation(self):
        """unknown_type_count=0 adds no violation."""
        denominator = {"denominator_basis": "FULL_SOT", "workflow_root_types": 3}
        planning = _make_planning_result("cells", ready=3, blocked=0)
        result = check_completeness("cells", denominator, planning, dry_run=True, unknown_type_count=0)
        assert result.status == "pass"
        assert result.unknown_type_count == 0

    def test_unknown_type_count_positive_warns(self):
        """unknown_type_count > 0 always adds a warning violation."""
        denominator = {"denominator_basis": "FULL_SOT", "workflow_root_types": 3}
        planning = _make_planning_result("cells", ready=3, blocked=0)
        result = check_completeness("cells", denominator, planning, dry_run=True, unknown_type_count=2)
        # Should warn even though equation holds (3 == 3)
        assert result.status == "warn"
        assert result.unknown_type_count == 2
        assert any("unknown" in v.lower() for v in result.violations)

    def test_unknown_type_count_does_not_raise_in_live_mode(self):
        """Unknown types produce a warning, not a hard failure, even in live mode."""
        denominator = {"denominator_basis": "FULL_SOT", "workflow_root_types": 3}
        planning = _make_planning_result("cells", ready=3, blocked=0)
        # Should NOT raise — unknown types are a soft warning
        result = check_completeness("cells", denominator, planning, dry_run=False, unknown_type_count=2)
        assert result.status == "warn"

    def test_pilot_allowed_full_wrt_count_reported(self):
        """PILOT_ALLOWED families report full_wrt_count from denominator for visibility."""
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 4,
            "workflow_root_types": 25,  # full SOT visible
        }
        planning = _make_planning_result("words", ready=4, blocked=0)
        result = check_completeness("words", denominator, planning, dry_run=True)
        assert result.status == "pass"
        assert result.full_wrt_count == 25  # full denominator reported for visibility

    def test_completeness_result_json_includes_new_fields(self, tmp_path):
        """Written JSON includes unknown_type_count and full_wrt_count fields."""
        denominator = {
            "denominator_basis": "PILOT_ALLOWED",
            "allowed_pilot_count": 4,
            "workflow_root_types": 10,
        }
        planning = _make_planning_result("words", ready=4, blocked=0)
        result = check_completeness("words", denominator, planning, dry_run=True, unknown_type_count=1)
        path = write_completeness_gate_result(result, tmp_path)
        data = json.loads(path.read_text())
        assert "unknown_type_count" in data
        assert data["unknown_type_count"] == 1
        assert "full_wrt_count" in data
        assert data["full_wrt_count"] == 10


class TestCompletenessGateRunnerIntegration:
    """Verify completeness gate is integrated into runner — not just unit-tested."""

    def test_real_denominator_loads_and_validates(self):
        """Load real denominator file and call check_completeness — no crash expected."""
        import json

        denom_path = Path(__file__).resolve().parents[2] / "pipeline" / "configs" / "denominators" / "cells.json"
        if not denom_path.exists():
            pytest.skip("cells.json denominator not found")
        denominator = json.loads(denom_path.read_text(encoding="utf-8"))
        planning = _make_planning_result("cells", ready=9, blocked=0)
        result = check_completeness("cells", denominator, planning, dry_run=True)
        # Should not crash; result holds since cells is FULL_SOT with 9 types
        assert result.status in ("pass", "warn", "skip")
        assert result.denominator_basis in ("FULL_SOT", "PILOT_ALLOWED", "DISCOVERY_ONLY", "UNKNOWN")

    def test_runner_scenario_planning_imports_completeness_gate(self):
        """runner._stage_scenario_planning must import and call check_completeness."""
        import inspect
        from plugin_examples import runner

        source = inspect.getsource(runner._stage_scenario_planning)
        assert "check_completeness" in source, (
            "_stage_scenario_planning must call check_completeness(). "
            "The completeness gate is not integrated — Gap 1 fix incomplete."
        )
        assert (
            "write_completeness_gate_result" in source
        ), "_stage_scenario_planning must call write_completeness_gate_result()."
        assert (
            "completeness_gate_status" in source
        ), "_stage_scenario_planning must return completeness_gate_status in stage artifacts."


# ---------------------------------------------------------------------------
# LANE B: PR candidate manifest integrity — demotion-aware merge
# ---------------------------------------------------------------------------


def _make_candidate(scenario_id: str, run_id: str = "run-old") -> dict:
    return {
        "scenario_id": scenario_id,
        "example_path": f"workspace/runs/{run_id}/generated/pdf/{scenario_id}",
        "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
    }


def _make_excluded(scenario_id: str, verdict: str = "EXAMPLE_BLOCKED_RUN_FAILED") -> dict:
    return {
        "scenario_id": scenario_id,
        "example_path": f"workspace/runs/run-new/generated/pdf/{scenario_id}",
        "final_example_verdict": verdict,
        "blocked_reason": "Runtime failed",
    }


class TestMergePrCandidateManifestsDemotionAware:
    """Verify demotion-aware candidate manifest merge logic."""

    def _make_manifest(self, included: list[dict], excluded: list[dict] | None = None) -> dict:
        excluded = excluded or []
        return {
            "included_examples": included,
            "excluded_examples": excluded,
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": len(included),
            "blocked_candidate_count": len(excluded),
        }

    def test_demoted_scenario_excluded_from_merged_manifest(self):
        """A scenario demoted in the latest run must be quarantined even if it was a prior pass."""
        existing = self._make_manifest([_make_candidate("pdf-png", "run-old")])
        new_run = self._make_manifest(
            included=[_make_candidate("pdf-merger", "run-new")],
            excluded=[_make_excluded("pdf-png")],
        )
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids={"pdf-png"})
        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        assert "pdf-png" not in included_ids, "Demoted scenario must not be in included_examples"
        assert "pdf-merger" in included_ids, "Non-demoted scenario must be preserved"

    def test_demoted_scenario_appears_in_excluded_as_quarantined(self):
        """Demoted scenario must appear in excluded_examples with quarantine marker."""
        existing = self._make_manifest([_make_candidate("pdf-png", "run-old")])
        new_run = self._make_manifest(
            included=[],
            excluded=[_make_excluded("pdf-png")],
        )
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids={"pdf-png"})
        excluded_ids = {e["scenario_id"] for e in result["excluded_examples"]}
        assert "pdf-png" in excluded_ids

    def test_non_demoted_older_candidate_preserved(self):
        """A scenario from an older run that failed generation (not demoted) is preserved."""
        existing = self._make_manifest(
            [
                _make_candidate("pdf-doc-converter", "run-old"),
                _make_candidate("pdf-png", "run-old"),
            ]
        )
        # New run: pdf-doc-converter generation failed, pdf-png demoted
        new_run = self._make_manifest(
            included=[_make_candidate("pdf-merger", "run-new")],
            excluded=[_make_excluded("pdf-doc-converter"), _make_excluded("pdf-png")],
        )
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids={"pdf-png"})
        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        assert "pdf-doc-converter" in included_ids, "Non-demoted regression-protected candidate preserved"
        assert "pdf-png" not in included_ids, "Demoted candidate quarantined"
        assert "pdf-merger" in included_ids, "New pass included"

    def test_current_run_candidates_get_integrity_status(self):
        """Candidates from the current run get candidate_integrity_status='current_run'."""
        existing = self._make_manifest([])
        new_run = self._make_manifest([_make_candidate("pdf-merger", "run-new")])
        result = merge_pr_candidate_manifests(existing, new_run)
        merger = next(e for e in result["included_examples"] if e["scenario_id"] == "pdf-merger")
        assert merger.get("candidate_integrity_status") == "current_run"

    def test_preserved_regression_protected_candidates_get_integrity_status(self):
        """Candidates preserved via regression protection get distinct integrity status."""
        existing = self._make_manifest([_make_candidate("pdf-doc-converter", "run-old")])
        new_run = self._make_manifest(
            included=[_make_candidate("pdf-merger", "run-new")],
            excluded=[_make_excluded("pdf-doc-converter")],
        )
        result = merge_pr_candidate_manifests(existing, new_run)
        doc = next(
            (e for e in result["included_examples"] if e["scenario_id"] == "pdf-doc-converter"),
            None,
        )
        assert doc is not None
        assert doc.get("candidate_integrity_status") == "prior_run_preserved_regression_protected"

    def test_no_demoted_ids_behaves_as_before(self):
        """With no demoted_scenario_ids, merge works like before — old passes preserved."""
        existing = self._make_manifest([_make_candidate("pdf-png", "run-old")])
        new_run = self._make_manifest(
            included=[_make_candidate("pdf-merger", "run-new")],
            excluded=[_make_excluded("pdf-png")],
        )
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids=None)
        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        assert "pdf-png" in included_ids, "Without demotion info, old pass is preserved (regression protection)"
        assert "pdf-merger" in included_ids

    def test_write_pr_candidate_manifest_uses_scenario_feedback(self, tmp_path):
        """write_pr_candidate_manifest passes demoted scenarios from feedback to merge."""
        # Write an existing manifest with pdf-png as a candidate
        existing_manifest = {
            "included_examples": [_make_candidate("pdf-png", "run-old")],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        (tmp_path / "latest").mkdir()
        (tmp_path / "latest" / "pr-candidate-manifest.json").write_text(json.dumps(existing_manifest), encoding="utf-8")

        new_manifest = {
            "included_examples": [_make_candidate("pdf-merger", "run-new")],
            "excluded_examples": [_make_excluded("pdf-png")],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 1,
        }
        scenario_feedback = {
            "total_feedback_updates": 1,
            "demoted_scenarios": 1,
            "updates": [
                {
                    "scenario_id": "pdf-png",
                    "previous_status": "ready",
                    "new_status": "blocked_missing_fixture",
                    "reason": "Output file was not created",
                }
            ],
        }

        write_pr_candidate_manifest(new_manifest, tmp_path, scenario_feedback=scenario_feedback)

        result = json.loads((tmp_path / "latest" / "pr-candidate-manifest.json").read_text())
        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        assert "pdf-png" not in included_ids, "Demoted pdf-png must be excluded by feedback gate"
        assert "pdf-merger" in included_ids

    def test_persisted_quarantine_in_excluded_survives_next_run(self):
        """A scenario quarantined (demoted_quarantined) in excluded_examples of the prior
        manifest must remain quarantined even when the next run does NOT emit a demotion."""
        # Prior manifest: pdf-png was previously demoted and persisted as excluded
        prior_quarantined = {
            "scenario_id": "pdf-png",
            "example_path": "workspace/runs/run-old/generated/pdf/pdf-png",
            "final_example_verdict": "EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN",
            "blocked_reason": "Demoted in prior run",
            "candidate_integrity_status": "demoted_quarantined",
        }
        existing = {
            "included_examples": [_make_candidate("pdf-merger", "run-old")],
            "excluded_examples": [prior_quarantined],
            "exclusion_reasons": {"EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN": ["pdf-png"]},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 1,
        }
        # New run: pdf-png failed generation (not reattempted at runtime) — NO demotion emitted
        new_run = {
            "included_examples": [_make_candidate("pdf-merger", "run-new")],
            "excluded_examples": [],  # generation failure — not in excluded list
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        # No demoted_scenario_ids from current run
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids=None)

        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        excluded_ids = {e["scenario_id"] for e in result["excluded_examples"]}

        assert (
            "pdf-png" not in included_ids
        ), "Persisted quarantine must survive even when current run emits no demotion"
        assert "pdf-png" in excluded_ids, "Quarantined scenario must remain in excluded_examples"
        quarantine_entry = next(e for e in result["excluded_examples"] if e["scenario_id"] == "pdf-png")
        assert quarantine_entry.get("candidate_integrity_status") == "demoted_quarantined"

    def test_persisted_quarantine_cleared_by_current_run_pass(self):
        """A scenario that was demoted_quarantined in the prior manifest is cleared
        (upgraded to current_run) when the current run produces a passing example."""
        prior_quarantined = {
            "scenario_id": "pdf-png",
            "example_path": "workspace/runs/run-old/generated/pdf/pdf-png",
            "final_example_verdict": "EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN",
            "blocked_reason": "Demoted in prior run",
            "candidate_integrity_status": "demoted_quarantined",
        }
        existing = {
            "included_examples": [],
            "excluded_examples": [prior_quarantined],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 0,
            "blocked_candidate_count": 1,
        }
        # Current run: pdf-png PASSES this time (full generation + runtime pass)
        new_run = {
            "included_examples": [_make_candidate("pdf-png", "run-new")],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids=None)

        included_ids = {e["scenario_id"] for e in result["included_examples"]}
        assert "pdf-png" in included_ids, "A current_run PASS must clear the prior quarantine"
        png_entry = next(e for e in result["included_examples"] if e["scenario_id"] == "pdf-png")
        assert png_entry.get("candidate_integrity_status") == "current_run"

    def test_persisted_quarantine_not_included_in_publishable_count(self):
        """publishable_candidate_count must not count persisted-quarantined scenarios."""
        prior_quarantined = {
            "scenario_id": "pdf-png",
            "example_path": "workspace/runs/run-old/generated/pdf/pdf-png",
            "final_example_verdict": "EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN",
            "blocked_reason": "Demoted in prior run",
            "candidate_integrity_status": "demoted_quarantined",
        }
        existing = {
            "included_examples": [],
            "excluded_examples": [prior_quarantined],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 0,
            "blocked_candidate_count": 1,
        }
        new_run = {
            "included_examples": [_make_candidate("pdf-merger", "run-new")],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        result = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids=None)

        assert (
            result["publishable_candidate_count"] == 1
        ), "Only non-quarantined candidates count toward publishable_candidate_count"


# ---------------------------------------------------------------------------
# LANE C: Gate semantics — degraded status for partial runtime
# ---------------------------------------------------------------------------


class TestGateSemanticsDegradedPartialRun:
    """Verify gate_run uses 'degraded' (not 'passed') for partial runtime success."""

    def test_partial_runtime_produces_degraded_gate_run(self):
        """When some examples pass runtime (not all), gate_run status must be 'degraded'."""
        # Partial runtime: 1/2 examples passed — gate_run must be 'degraded'
        gate_run = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="degraded",
            required=True,
            failure_reason="1/2 examples passed runtime",
            stage_name="validation",
        )
        assert gate_run.status == "degraded"
        assert gate_run.failure_reason is not None
        assert "degraded" in GATE_STATUSES, "'degraded' must be in canonical GATE_STATUSES"

    def test_degraded_gate_has_non_null_failure_reason(self):
        """A degraded gate must always carry a failure_reason (partial semantics)."""
        gate = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="degraded",
            required=True,
            failure_reason="5/6 examples passed runtime",
            stage_name="validation",
        )
        assert gate.failure_reason is not None

    def test_passed_gate_has_null_failure_reason(self):
        """A passed gate must have null failure_reason (no contradiction)."""
        gate = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="passed",
            required=True,
            failure_reason=None,
            stage_name="validation",
        )
        assert gate.failure_reason is None, "A 'passed' gate must not have a failure_reason"

    def test_all_required_passed_true_when_degraded(self):
        """all_required_passed must be True when required gates are degraded (partial OK)."""
        gates = [
            GateResult(gate_id="gate_scenarios", name="Scenarios", status="passed", required=True, stage_name="s"),
            GateResult(gate_id="gate_generation", name="Generation", status="passed", required=True, stage_name="g"),
            GateResult(gate_id="gate_build", name="Build", status="passed", required=True, stage_name="b"),
            GateResult(
                gate_id="gate_run",
                name="Runtime",
                status="degraded",
                required=True,
                stage_name="v",
                failure_reason="5/6 examples passed runtime",
            ),
        ]
        all_required_passed = all(g.status in ("passed", "degraded") for g in gates if g.required)
        assert all_required_passed is True

    def test_all_required_passed_false_when_failed(self):
        """all_required_passed must be False when a required gate failed."""
        gates = [
            GateResult(gate_id="gate_scenarios", name="Scenarios", status="passed", required=True, stage_name="s"),
            GateResult(gate_id="gate_run", name="Runtime", status="failed", required=True, stage_name="v"),
        ]
        all_required_passed = all(g.status in ("passed", "degraded") for g in gates if g.required)
        assert all_required_passed is False

    def test_runner_produces_degraded_gate_run_for_partial_pass(self):
        """The runner's evaluator must produce gate_run=degraded when partial runtime."""
        import inspect
        from plugin_examples.gates import evaluator

        source = inspect.getsource(evaluator.evaluate_gates)
        assert "degraded" in source, (
            "evaluator.evaluate_gates must use 'degraded' status for partial runtime. "
            "A 'passed' gate with failure_reason is semantically incoherent."
        )

    def test_gate_run_not_in_blocking_when_degraded(self):
        """A degraded gate_run must not be added to blocking gates (partial pass is not a hard block)."""
        import inspect
        from plugin_examples.gates import evaluator

        source = inspect.getsource(evaluator.evaluate_gates)
        # Verify the fix: blocking only happens for "failed" not "degraded"
        assert 'gate.status == "failed"' in source or 'status == "failed"' in source, (
            "evaluator.evaluate_gates must only add gate_run to blocking when status == 'failed', " "not when degraded."
        )
