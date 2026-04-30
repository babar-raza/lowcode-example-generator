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
        "load_config", "nuget_fetch", "dependency_resolution",
        "extraction", "reflection", "plugin_detection",
        "api_delta", "impact_mapping", "fixture_registry",
        "example_mining", "scenario_planning", "llm_preflight",
        "generation", "validation", "reviewer", "publisher",
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
            g = GateResult(gate_id="test", name="test", status=status,
                           required=False, stage_name="test")
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
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 0, "blocked_count": 5}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "SOURCE_OF_TRUTH_PROVEN_ONLY"

    def test_template_mode_produces_data_flow_prototype(self):
        ctx = _FakeCtx(template_mode=True)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
            "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"
        assert not verdict.publishable

    def test_skip_run_produces_data_flow_prototype(self):
        ctx = _FakeCtx(template_mode=False, skip_run=True)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 3, "failed": 0, "total": 3}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"

    def test_build_failure_produces_blocked_build(self):
        ctx = _FakeCtx(template_mode=False, skip_run=False)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "BLOCKED_BUILD_FAILED"
        assert not verdict.publishable

    def test_generation_zero_produces_blocked_generation(self):
        ctx = _FakeCtx()
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 0}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict == "BLOCKED_GENERATION"


# ---------------------------------------------------------------------------
# TestDetermineVerdict
# ---------------------------------------------------------------------------


class TestDetermineVerdict:
    def test_delegates_to_evaluator(self):
        ctx = _FakeCtx(template_mode=True)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
        })
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
