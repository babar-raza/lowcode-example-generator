"""Contract tests proving the pipeline cannot produce false success verdicts.

These tests enforce the system contract:
- Build failure cannot produce FULL_E2E_PASSED
- Template mode cannot produce FULL_E2E_PASSED
- Skipped runtime cannot produce FULL_E2E_PASSED
- Reviewer unavailable blocks publishing
- Publisher rejects missing or failed gates

Tests marked with pytest.mark.skip are blocked until the corresponding
wave is implemented. They serve as living documentation of future contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from plugin_examples.gates.models import GateResult, GateVerdict, VERDICTS
from plugin_examples.gates.evaluator import (
    evaluate_gates,
    is_publishable,
    is_publishable_verdict,
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
class _FakeDotnetResult:
    success: bool = False


@dataclass
class _FakeValidationResult:
    passed: bool = False
    restore: _FakeDotnetResult | None = None
    build: _FakeDotnetResult | None = None
    run: _FakeDotnetResult | None = None


@dataclass
class _FakeCtx:
    family: str = "cells"
    run_id: str = "test-run"
    dry_run: bool = True
    skip_run: bool = False
    template_mode: bool = False
    require_llm: bool = False
    require_validation: bool = False
    require_reviewer: bool = False
    validation_results: list = field(default_factory=list)
    gate_verdict: object = None


def _make_stages(overrides: dict | None = None) -> list[_FakeStage]:
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
# Contract: Build failure blocks FULL_E2E_PASSED
# ---------------------------------------------------------------------------


class TestBuildFailureBlocksFullE2E:
    def test_build_failure_blocks_full_e2e(self):
        """Build failure must NEVER produce FULL_E2E_PASSED."""
        ctx = _FakeCtx(template_mode=False, skip_run=False, dry_run=False)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
            "reviewer": {"artifacts": {"available": True, "passed": True}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict != "FULL_E2E_PASSED"
        assert verdict.verdict == "BLOCKED_BUILD_FAILED"
        assert not verdict.publishable


# ---------------------------------------------------------------------------
# Contract: Reviewer unavailable blocks publishing
# ---------------------------------------------------------------------------


class TestReviewerUnavailableBlocksPublish:
    def test_reviewer_unavailable_blocks_publish(self):
        """Reviewer unavailable on publish path must NOT produce PR_READY."""
        ctx = _FakeCtx(
            template_mode=False, skip_run=False, dry_run=False,
            require_reviewer=True,
        )
        vr = _FakeValidationResult(
            passed=True,
            restore=_FakeDotnetResult(success=True),
            build=_FakeDotnetResult(success=True),
            run=_FakeDotnetResult(success=True),
        )
        ctx.validation_results = [vr]
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 3, "failed": 0, "total": 3}},
            "reviewer": {"status": "failed", "artifacts": {"available": False, "passed": False}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict != "PR_READY"
        assert verdict.verdict != "FULL_E2E_PASSED"
        assert not verdict.publishable


# ---------------------------------------------------------------------------
# Contract: Template mode never FULL_E2E_PASSED
# ---------------------------------------------------------------------------


class TestTemplateModeNeverFullE2E:
    def test_template_mode_never_full_e2e(self):
        """Template mode must NEVER produce FULL_E2E_PASSED."""
        ctx = _FakeCtx(template_mode=True, skip_run=False, dry_run=False)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 10}},
            "generation": {"artifacts": {"examples_generated": 10, "generation_mode": "template"}},
            "validation": {"artifacts": {"passed": 10, "failed": 0, "total": 10}},
            "reviewer": {"artifacts": {"available": True, "passed": True}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict != "FULL_E2E_PASSED"
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"


# ---------------------------------------------------------------------------
# Contract: Skip run never FULL_E2E_PASSED
# ---------------------------------------------------------------------------


class TestSkipRunNeverFullE2E:
    def test_skip_run_never_full_e2e(self):
        """skip_run=True must NEVER produce FULL_E2E_PASSED."""
        ctx = _FakeCtx(template_mode=False, skip_run=True, dry_run=False)
        stages = _make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 5}},
            "generation": {"artifacts": {"examples_generated": 5, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 5, "failed": 0, "total": 5}},
            "reviewer": {"artifacts": {"available": True, "passed": True}},
        })
        verdict = evaluate_gates(stages, ctx)
        assert verdict.verdict != "FULL_E2E_PASSED"
        assert verdict.verdict == "DATA_FLOW_PROTOTYPE_ONLY"


# ---------------------------------------------------------------------------
# Contract: Publisher rejects missing gate results
# ---------------------------------------------------------------------------


class TestPublisherRejectsMissingGateResults:
    def test_publisher_rejects_missing_gate_results(self):
        """No gate verdict means not publishable."""
        verdict = GateVerdict(
            verdict="DATA_FLOW_PROTOTYPE_ONLY",
            publishable=False,
            all_required_passed=False,
        )
        assert not is_publishable(verdict)

    def test_none_verdict_not_publishable(self):
        """Absent verdict string must not be publishable."""
        assert not is_publishable_verdict("DATA_FLOW_PROTOTYPE_ONLY")
        assert not is_publishable_verdict("SOURCE_OF_TRUTH_PROVEN_ONLY")


# ---------------------------------------------------------------------------
# Contract: Publisher rejects failed build
# ---------------------------------------------------------------------------


class TestPublisherRejectsFailedBuild:
    def test_publisher_rejects_failed_build(self):
        """Failed build verdict must not be publishable."""
        assert not is_publishable_verdict("BLOCKED_BUILD_FAILED")

    def test_all_blocked_verdicts_not_publishable(self):
        """Every BLOCKED_* verdict must not be publishable."""
        for v in VERDICTS:
            if v.startswith("BLOCKED_"):
                assert not is_publishable_verdict(v), f"{v} should not be publishable"


# ---------------------------------------------------------------------------
# Placeholder contracts — blocked until future waves
# ---------------------------------------------------------------------------


class TestScenarioMissingFixtureIsBlocked:
    def test_scenario_missing_fixture_unsupported_format_is_blocked(self):
        """A type needing a fixture in an unsupported format must be blocked."""
        from plugin_examples.scenario_planner.planner import _build_scenario

        type_info = {
            "full_name": "Aspose.Cells.LowCode.CustomProcessor",
            "name": "CustomProcessor",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": False,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        fixture_registry = {"fixtures": [{"filename": "other.docx", "available": True}]}
        # .psd is not supported by the fixture factory and not in registry
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", fixture_registry, ".psd")
        assert scenario.status == "blocked_no_fixture"
        assert scenario.blocked_reason is not None
        assert scenario.input_strategy == "no_valid_input_strategy"

    def test_supported_format_uses_generated_fixture_file(self):
        """A type needing .xlsx fixture should use generated_fixture_file strategy."""
        from plugin_examples.scenario_planner.planner import _build_scenario

        type_info = {
            "full_name": "Aspose.Cells.LowCode.SpreadsheetConverter",
            "name": "SpreadsheetConverter",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": True,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        fixture_registry = {"fixtures": [{"filename": "other.docx", "available": True}]}
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", fixture_registry, ".xlsx")
        assert scenario.status == "ready"
        assert scenario.input_strategy == "generated_fixture_file"
        assert scenario.input_files == ["input.xlsx"]


class TestOutputValidatorReadsExpectedOutputJson:
    def test_output_validator_reads_expected_output_json(self, tmp_path):
        """Output validator must honour expected-output.json constraints."""
        import json
        from plugin_examples.verifier_bridge.output_validator import (
            validate_output,
            load_expected_output,
        )

        # Write expected-output.json
        eo = {
            "must_contain": ["Hello"],
            "must_not_contain": ["Unhandled exception"],
            "has_output": True,
        }
        eo_path = tmp_path / "expected-output.json"
        eo_path.write_text(json.dumps(eo))
        loaded = load_expected_output(tmp_path)
        assert loaded is not None

        # Passing case
        result = validate_output("test", "Hello world", "", expected_output=loaded)
        assert result.passed

        # Failing case — missing must_contain
        result2 = validate_output("test", "Goodbye", "", expected_output=loaded)
        assert not result2.passed
        assert any("Missing required output" in i for i in result2.issues)

        # Failing case — forbidden output
        result3 = validate_output("test", "Hello Unhandled exception", "", expected_output=loaded)
        assert not result3.passed


class TestPackageWatcherDetectsNoChange:
    def test_package_watcher_detects_no_change(self, tmp_path, monkeypatch):
        """Same version = no update detected."""
        import json
        from plugin_examples.package_watcher.watcher import check_for_updates

        monkeypatch.setattr(
            "plugin_examples.package_watcher.watcher._resolve_latest_nuget_version",
            lambda pkg: "26.4.0",
        )
        lock_path = tmp_path / "package-lock.json"
        lock_path.write_text(json.dumps({
            "packages": {"Aspose.Cells": {"version": "26.4.0"}},
        }))
        families = [{"family": "cells", "enabled": True, "status": "active",
                      "nuget": {"package_id": "Aspose.Cells"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert not results[0].has_update
        assert results[0].latest_version == "26.4.0"


class TestPackageWatcherDetectsChangedVersion:
    def test_package_watcher_detects_changed_version(self, tmp_path, monkeypatch):
        """Different version = update detected."""
        import json
        from plugin_examples.package_watcher.watcher import check_for_updates

        monkeypatch.setattr(
            "plugin_examples.package_watcher.watcher._resolve_latest_nuget_version",
            lambda pkg: "26.5.0",
        )
        lock_path = tmp_path / "package-lock.json"
        lock_path.write_text(json.dumps({
            "packages": {"Aspose.Cells": {"version": "26.4.0"}},
        }))
        families = [{"family": "cells", "enabled": True, "status": "active",
                      "nuget": {"package_id": "Aspose.Cells"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert results[0].has_update
        assert results[0].latest_version == "26.5.0"
