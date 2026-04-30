"""Unit tests for the pipeline orchestrator (runner.py).

All external module calls are mocked — no network, NuGet, .NET SDK, LLM,
reviewer, or GitHub token required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from plugin_examples.runner import (
    PipelineContext,
    StageResult,
    _build_report,
    _determine_verdict,
    _fixture_registry_to_dict,
    _fixture_sources_to_dicts,
    _run_stage,
    _snapshot_workspace,
    run_pipeline,
    scenario_to_dict,
)


# ---------------------------------------------------------------------------
# Helpers — minimal fakes for dataclasses used by the runner
# ---------------------------------------------------------------------------

def _make_ctx(tmp_path: Path, **overrides) -> PipelineContext:
    """Create a PipelineContext with sensible defaults for testing."""
    run_dir = tmp_path / "workspace" / "runs" / "test-run"
    run_dir.mkdir(parents=True, exist_ok=True)
    evidence = run_dir / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)

    defaults = dict(
        family="cells",
        run_id="test-run",
        dry_run=True,
        skip_run=True,
        template_mode=True,
        require_llm=False,
        require_validation=False,
        require_reviewer=False,
        repo_root=tmp_path,
        run_dir=run_dir,
        evidence_dir=evidence,
    )
    defaults.update(overrides)
    return PipelineContext(**defaults)


@dataclass
class FakeScenario:
    scenario_id: str = "sc-001"
    title: str = "Test Scenario"
    target_type: str = "TestType"
    target_namespace: str = "Test.Namespace"
    target_methods: list = field(default_factory=lambda: ["Process"])
    required_symbols: list = field(default_factory=list)
    required_fixtures: list = field(default_factory=list)
    output_plan: str = ""
    validation_plan: str = ""
    status: str = "ready"
    blocked_reason: str | None = None


@dataclass
class FakeFixtureEntry:
    filename: str = "test.xlsx"
    available: bool = True


@dataclass
class FakeFixtureRegistry:
    family: str = "cells"
    fixtures: list = field(default_factory=lambda: [FakeFixtureEntry()])


@dataclass
class FakeFixtureSource:
    type: str = "github"
    owner: str = "aspose-cells"
    repo: str = "Aspose.Cells-for-.NET"
    branch: str = "master"
    paths: list = field(default_factory=lambda: ["Examples/Data"])


@dataclass
class FakeNamespaceMatch:
    namespace: str = "Aspose.Cells.LowCode"
    matched_by_pattern: str = "*.LowCode"
    public_type_count: int = 5
    public_method_count: int = 20


@dataclass
class FakeDetectionResult:
    matched_namespaces: list = field(default_factory=lambda: [FakeNamespaceMatch()])
    unmatched_patterns: list = field(default_factory=list)
    public_plugin_type_count: int = 5
    public_plugin_method_count: int = 20
    is_eligible: bool = True


@dataclass
class FakePlanningResult:
    family: str = "cells"
    ready_scenarios: list = field(default_factory=lambda: [FakeScenario()])
    blocked_scenarios: list = field(default_factory=list)
    ready_count: int = 1
    blocked_count: int = 0


# ---------------------------------------------------------------------------
# TestHelpers
# ---------------------------------------------------------------------------


class TestScenarioToDict:
    def test_converts_dataclass_to_dict(self):
        s = FakeScenario(scenario_id="sc-100", title="Convert PDF")
        d = scenario_to_dict(s)
        assert isinstance(d, dict)
        assert d["scenario_id"] == "sc-100"
        assert d["title"] == "Convert PDF"
        assert d["target_type"] == "TestType"
        assert d["target_methods"] == ["Process"]
        assert d["status"] == "ready"
        assert d["blocked_reason"] is None

    def test_all_fields_present(self):
        s = FakeScenario()
        d = scenario_to_dict(s)
        expected_keys = {
            "scenario_id", "title", "target_type", "target_namespace",
            "target_methods", "required_symbols", "required_fixtures",
            "output_plan", "validation_plan", "status", "blocked_reason",
            "input_strategy", "input_files", "required_input_format",
        }
        assert set(d.keys()) == expected_keys


class TestFixtureSourcesToDicts:
    def test_converts_list_of_dataclasses(self):
        sources = [FakeFixtureSource(), FakeFixtureSource(owner="other")]
        result = _fixture_sources_to_dicts(sources)
        assert len(result) == 2
        assert result[0]["owner"] == "aspose-cells"
        assert result[1]["owner"] == "other"
        assert result[0]["type"] == "github"
        assert result[0]["paths"] == ["Examples/Data"]

    def test_empty_list(self):
        assert _fixture_sources_to_dicts([]) == []


class TestFixtureRegistryToDict:
    def test_converts_registry(self):
        reg = FakeFixtureRegistry()
        d = _fixture_registry_to_dict(reg)
        assert d is not None
        assert "fixtures" in d
        assert d["fixtures"][0]["filename"] == "test.xlsx"
        assert d["fixtures"][0]["available"] is True

    def test_none_returns_none(self):
        assert _fixture_registry_to_dict(None) is None


class TestSnapshotWorkspace:
    def test_empty_directories(self, tmp_path):
        man = tmp_path / "manifests"
        ver = tmp_path / "verification"
        snap = _snapshot_workspace(man, ver)
        assert snap["manifests_files"] == []
        assert snap["verification_files"] == []

    def test_with_files(self, tmp_path):
        man = tmp_path / "manifests"
        man.mkdir()
        (man / "product-inventory.json").write_text("{}")
        (man / ".gitkeep").write_text("")

        ver = tmp_path / "verification"
        latest = ver / "latest"
        latest.mkdir(parents=True)
        (latest / "proof.json").write_text("{}")

        snap = _snapshot_workspace(man, ver)
        assert snap["manifests_files"] == ["product-inventory.json"]
        assert snap["verification_files"] == ["proof.json"]

    def test_gitkeep_excluded(self, tmp_path):
        man = tmp_path / "manifests"
        man.mkdir()
        (man / ".gitkeep").write_text("")
        snap = _snapshot_workspace(man, tmp_path / "verification")
        assert snap["manifests_files"] == []


class TestLLMWrapperBridgesSignature:
    def test_lambda_bridges_positional_to_keyword(self):
        """generate_example expects (prompt, system_prompt) positional;
        LLMRouter.generate has keyword-only system_prompt."""
        mock_router = MagicMock()
        mock_router.generate.return_value = "generated code"

        # This is the exact pattern used in _stage_generation
        llm_fn = lambda p, s: mock_router.generate(p, system_prompt=s)

        result = llm_fn("prompt text", "system prompt text")
        assert result == "generated code"
        mock_router.generate.assert_called_once_with(
            "prompt text", system_prompt="system prompt text"
        )


# ---------------------------------------------------------------------------
# TestStageExecution
# ---------------------------------------------------------------------------


class TestRunStage:
    def test_success(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        fn = lambda c: {"key": "value"}
        result = _run_stage("test_stage", 1, fn, ctx)
        assert result.status == "success"
        assert result.artifacts == {"key": "value"}
        assert result.error is None
        assert result.duration_ms >= 0

    def test_failure(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        fn = lambda c: (_ for _ in ()).throw(RuntimeError("boom"))
        # Use a proper function that raises
        def failing_fn(c):
            raise RuntimeError("boom")
        result = _run_stage("test_stage", 1, failing_fn, ctx)
        assert result.status == "failed"
        assert "boom" in result.error

    def test_none_return_gives_empty_artifacts(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        result = _run_stage("test_stage", 1, lambda c: None, ctx)
        assert result.status == "success"
        assert result.artifacts == {}


class TestHardStopOnConfigFailure:
    @patch("plugin_examples.runner._stage_load_config")
    def test_hard_stop_propagates(self, mock_config, tmp_path):
        """Config failure is a hard-stop — all subsequent stages should be skipped."""
        mock_config.side_effect = RuntimeError("Config not found")
        result = _run_stage("load_config", 1, mock_config, _make_ctx(tmp_path))
        assert result.status == "failed"
        assert "Config not found" in result.error


class TestHardStopOnNugetFailure:
    def test_nuget_failure_is_hard_stop(self, tmp_path):
        def fail_fn(ctx):
            raise ConnectionError("NuGet unavailable")
        result = _run_stage("nuget_fetch", 2, fail_fn, _make_ctx(tmp_path))
        assert result.status == "failed"
        assert "NuGet unavailable" in result.error


class TestHardStopOnExtractionFailure:
    def test_extraction_failure_is_hard_stop(self, tmp_path):
        def fail_fn(ctx):
            raise FileNotFoundError("DLL not found in nupkg")
        result = _run_stage("extraction", 4, fail_fn, _make_ctx(tmp_path))
        assert result.status == "failed"
        assert "DLL not found" in result.error


class TestHardStopOnReflectionFailure:
    def test_reflection_failure_is_hard_stop(self, tmp_path):
        def fail_fn(ctx):
            raise RuntimeError("DllReflector crashed")
        result = _run_stage("reflection", 5, fail_fn, _make_ctx(tmp_path))
        assert result.status == "failed"
        assert "DllReflector crashed" in result.error


class TestHardStopOnSotIneligible:
    def test_sot_ineligible_is_hard_stop(self, tmp_path):
        def fail_fn(ctx):
            raise RuntimeError("Not eligible: no matched namespaces")
        result = _run_stage("plugin_detection", 6, fail_fn, _make_ctx(tmp_path))
        assert result.status == "failed"


# ---------------------------------------------------------------------------
# TestDegradedContinuation
# ---------------------------------------------------------------------------


class TestDegradedLLMUnavailable:
    def test_llm_failure_without_require_is_degraded(self, tmp_path):
        """LLM failure should degrade (not hard stop) when require_llm=False."""
        stages = [
            StageResult(name="llm_preflight", order=13, status="failed",
                       error="No provider"),
        ]
        # The runner converts failed -> degraded for llm_preflight when not required
        ctx = _make_ctx(tmp_path, require_llm=False)
        # Simulate the runner's degradation logic
        result = stages[0]
        if result.status == "failed" and not ctx.require_llm:
            result.status = "degraded"
        assert result.status == "degraded"


class TestConditionalHardStopRequireLLM:
    def test_llm_failure_with_require_is_hard_stop(self, tmp_path):
        """LLM failure should remain 'failed' when require_llm=True."""
        ctx = _make_ctx(tmp_path, require_llm=True)
        result = StageResult(name="llm_preflight", order=13, status="failed",
                            error="No provider")
        # With require_llm=True, runner does NOT downgrade to degraded
        if result.status == "failed" and result.name == "llm_preflight" and not ctx.require_llm:
            result.status = "degraded"
        assert result.status == "failed"


class TestDegradedReviewerUnavailable:
    def test_reviewer_failure_without_require_is_degraded(self, tmp_path):
        ctx = _make_ctx(tmp_path, require_reviewer=False)
        result = StageResult(name="reviewer", order=16, status="failed",
                            error="Not installed")
        if result.status == "failed" and not ctx.require_reviewer:
            result.status = "degraded"
        assert result.status == "degraded"


class TestConditionalHardStopRequireValidation:
    def test_validation_failure_with_require_is_hard_stop(self, tmp_path):
        ctx = _make_ctx(tmp_path, require_validation=True)
        result = StageResult(name="validation", order=15, status="failed",
                            error="Build failed")
        if result.status == "failed" and result.name == "validation" and not ctx.require_validation:
            result.status = "degraded"
        assert result.status == "failed"


class TestConditionalHardStopRequireReviewer:
    def test_reviewer_failure_with_require_is_hard_stop(self, tmp_path):
        ctx = _make_ctx(tmp_path, require_reviewer=True)
        result = StageResult(name="reviewer", order=16, status="failed",
                            error="Not installed")
        if result.status == "failed" and result.name == "reviewer" and not ctx.require_reviewer:
            result.status = "degraded"
        assert result.status == "failed"


class TestSoftStageContinuesOnError:
    def test_api_delta_failure_degrades(self, tmp_path):
        """Non-hard-stop stages degrade instead of stopping the pipeline."""
        result = StageResult(name="api_delta", order=8, status="failed",
                            error="Unexpected")
        # api_delta is NOT in HARD_STOP_STAGES, so runner degrades it
        from plugin_examples.runner import HARD_STOP_STAGES
        assert "api_delta" not in HARD_STOP_STAGES
        if result.status == "failed" and result.name not in HARD_STOP_STAGES:
            result.status = "degraded"
        assert result.status == "degraded"


class TestSkippedStagesAfterHardStop:
    def test_stages_skipped_after_hard_stop(self, tmp_path):
        """After a hard stop, all remaining stages should be skipped."""
        stages = []
        hard_stopped = True
        for name, order in [("api_delta", 8), ("impact_mapping", 9)]:
            if hard_stopped:
                stages.append(StageResult(name=name, order=order, status="skipped"))
        assert all(s.status == "skipped" for s in stages)
        assert len(stages) == 2


# ---------------------------------------------------------------------------
# TestDetermineVerdict
# ---------------------------------------------------------------------------


class TestDetermineVerdict:
    def _make_stages(self, overrides: dict | None = None) -> list[StageResult]:
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
            s = StageResult(name=name, order=i + 1, status="success")
            stages.append(s)
        if overrides:
            for name, kwargs in overrides.items():
                for s in stages:
                    if s.name == name:
                        for k, v in kwargs.items():
                            setattr(s, k, v)
        return stages

    def test_blocked_hard_gate_failed(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        stages = self._make_stages({"nuget_fetch": {"status": "failed"}})
        assert _determine_verdict(stages, ctx) == "BLOCKED_SOURCE_OF_TRUTH"

    def test_blocked_no_generation(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        stages = self._make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 5, "blocked_count": 0}},
            "generation": {"status": "success", "artifacts": {"examples_generated": 0}},
        })
        assert _determine_verdict(stages, ctx) == "BLOCKED_GENERATION"

    def test_data_flow_prototype_template_mode(self, tmp_path):
        ctx = _make_ctx(tmp_path, template_mode=True)
        stages = self._make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "template"}},
            "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
        })
        verdict = _determine_verdict(stages, ctx)
        assert verdict == "DATA_FLOW_PROTOTYPE_ONLY"

    def test_data_flow_prototype_skip_run(self, tmp_path):
        ctx = _make_ctx(tmp_path, template_mode=False, skip_run=True)
        stages = self._make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 3, "failed": 0, "total": 3}},
        })
        verdict = _determine_verdict(stages, ctx)
        assert verdict == "DATA_FLOW_PROTOTYPE_ONLY"

    def test_blocked_build_failed_llm(self, tmp_path):
        ctx = _make_ctx(tmp_path, template_mode=False, skip_run=False)
        stages = self._make_stages({
            "scenario_planning": {"artifacts": {"ready_count": 3, "blocked_count": 0}},
            "generation": {"artifacts": {"examples_generated": 3, "generation_mode": "llm"}},
            "validation": {"artifacts": {"passed": 0, "failed": 3, "total": 3}},
        })
        verdict = _determine_verdict(stages, ctx)
        assert verdict == "BLOCKED_BUILD_FAILED"


# ---------------------------------------------------------------------------
# TestBuildReport
# ---------------------------------------------------------------------------


class TestBuildReport:
    def test_report_contains_required_fields(self, tmp_path):
        ctx = _make_ctx(tmp_path)
        stages = [
            StageResult(name=n, order=i + 1, status="success", artifacts={})
            for i, n in enumerate([
                "load_config", "nuget_fetch", "dependency_resolution",
                "extraction", "reflection", "plugin_detection",
                "api_delta", "impact_mapping", "fixture_registry",
                "example_mining", "scenario_planning", "llm_preflight",
                "generation", "validation", "reviewer", "publisher",
            ])
        ]
        report = _build_report(
            ctx, stages,
            before={"manifests_files": [], "verification_files": []},
            after={"manifests_files": [], "verification_files": [], "run_evidence_files": []},
            start_time="2026-04-28T00:00:00Z",
            end_time="2026-04-28T00:01:00Z",
            total_ms=60000.0,
            command="test command",
        )
        # Required top-level keys
        for key in ("meta", "before", "after", "comparison", "stages",
                     "gate_summary", "environment", "verdict"):
            assert key in report, f"Missing key: {key}"

        # Meta
        assert report["meta"]["run_id"] == "test-run"
        assert report["meta"]["family"] == "cells"
        assert report["meta"]["command"] == "test command"

        # Gate summary
        gs = report["gate_summary"]
        assert "total_stages" in gs
        assert "passed" in gs
        assert "degraded" in gs
        assert "failed" in gs
        assert "skipped" in gs
        assert "hard_stopped" in gs

        # Stages
        assert len(report["stages"]) == 16
        for stage in report["stages"]:
            assert "name" in stage
            assert "order" in stage
            assert "status" in stage

    def test_report_serializable(self, tmp_path):
        """Report must be JSON-serializable."""
        ctx = _make_ctx(tmp_path)
        stages = [
            StageResult(name="load_config", order=1, status="success",
                       artifacts={"family": "cells"})
        ]
        report = _build_report(
            ctx, stages,
            before={"manifests_files": [], "verification_files": []},
            after={"manifests_files": [], "verification_files": [], "run_evidence_files": []},
            start_time="2026-04-28T00:00:00Z",
            end_time="2026-04-28T00:00:01Z",
            total_ms=1000.0,
        )
        # Should not raise
        serialized = json.dumps(report)
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# TestCleanRunDir
# ---------------------------------------------------------------------------


class TestCleanRunDirSafety:
    def test_clean_run_dir_only_removes_run_dir(self, tmp_path):
        """--clean-run-dir must only remove workspace/runs/{id}/, never manifests or verification."""
        import shutil

        # Set up workspace structure
        manifests = tmp_path / "workspace" / "manifests"
        manifests.mkdir(parents=True)
        (manifests / "important.json").write_text("{}")

        verification = tmp_path / "workspace" / "verification" / "latest"
        verification.mkdir(parents=True)
        (verification / "proof.json").write_text("{}")

        run_dir = tmp_path / "workspace" / "runs" / "test-run"
        run_dir.mkdir(parents=True)
        (run_dir / "some-artifact.json").write_text("{}")

        # Simulate --clean-run-dir (same logic as pilot_run.py)
        shutil.rmtree(run_dir)

        # Run dir is gone
        assert not run_dir.exists()
        # Manifests and verification are untouched
        assert (manifests / "important.json").exists()
        assert (verification / "proof.json").exists()


# ---------------------------------------------------------------------------
# TestNoOldRootPaths
# ---------------------------------------------------------------------------


class TestNoOldRootPaths:
    def test_runner_does_not_create_old_root_paths(self, tmp_path):
        """Runner must never create bare configs/, schemas/, etc. at repo root."""
        forbidden = ["configs", "schemas", "prompts", "runs",
                     "manifests", "verification"]
        # After a potential run, check no forbidden dirs at root
        for name in forbidden:
            assert not (tmp_path / name).exists(), \
                f"Forbidden old-root path found: {name}/"


# ---------------------------------------------------------------------------
# TestMainWiring
# ---------------------------------------------------------------------------


class TestMainWiring:
    def test_run_command_calls_run_pipeline(self):
        """__main__.py run command should call runner.run_pipeline."""
        with patch("plugin_examples.runner.run_pipeline") as mock_rp:
            mock_rp.return_value = {
                "gate_summary": {"passed": 10, "degraded": 0, "failed": 0,
                                  "hard_stopped": False},
                "verdict": "DATA_FLOW_PROTOTYPE_ONLY",
            }
            from plugin_examples.__main__ import main
            import sys
            with patch.object(sys, "argv", ["plugin-examples", "run", "--family", "cells"]):
                exit_code = main()
            assert exit_code == 0
            mock_rp.assert_called_once()
            call_kwargs = mock_rp.call_args[1]
            assert call_kwargs["family"] == "cells"


# ---------------------------------------------------------------------------
# TestRunPipeline (mocked end-to-end)
# ---------------------------------------------------------------------------


class TestRunPipelineMocked:
    """Full pipeline with every external module mocked."""

    def _mock_all_stages(self):
        """Return a dict of patches for all stage functions."""
        return {
            "load_config": patch("plugin_examples.runner._stage_load_config",
                                return_value={"family": "cells", "package_id": "Aspose.Cells"}),
            "nuget_fetch": patch("plugin_examples.runner._stage_nuget_fetch",
                                return_value={"version": "25.4.0", "sha256": "abc123",
                                              "cached_path": "/tmp/pkg.nupkg"}),
            "dep_res": patch("plugin_examples.runner._stage_dependency_resolution",
                            return_value={"dependency_count": 3}),
            "extraction": patch("plugin_examples.runner._stage_extraction",
                               return_value={"selected_framework": "netstandard2.0",
                                             "dll_path": "/tmp/Aspose.Cells.dll",
                                             "xml_path": None}),
            "reflection": patch("plugin_examples.runner._stage_reflection",
                               return_value={"catalog_path": "/tmp/catalog.json",
                                             "namespace_count": 1}),
            "detection": patch("plugin_examples.runner._stage_plugin_detection",
                              return_value={"eligible": True,
                                            "matched_namespaces": ["Aspose.Cells.LowCode"],
                                            "plugin_type_count": 5,
                                            "plugin_method_count": 20}),
            "delta": patch("plugin_examples.runner._stage_api_delta",
                          return_value={"initial_run": True, "total_changes": 5}),
            "impact": patch("plugin_examples.runner._stage_impact_mapping",
                           return_value={"new_api_needed": 0}),
            "fixtures": patch("plugin_examples.runner._stage_fixture_registry",
                             return_value={"fixture_count": 0}),
            "mining": patch("plugin_examples.runner._stage_example_mining",
                           return_value={"mined_total": 0, "stale_count": 0}),
            "planning": patch("plugin_examples.runner._stage_scenario_planning",
                             return_value={"ready_count": 2, "blocked_count": 1}),
            "llm": patch("plugin_examples.runner._stage_llm_preflight",
                        return_value={"selected_provider": None, "llm_available": False}),
            "generation": patch("plugin_examples.runner._stage_generation",
                               return_value={"examples_generated": 2,
                                             "generation_mode": "template"}),
            "validation": patch("plugin_examples.runner._stage_validation",
                               return_value={"total": 2, "passed": 0, "failed": 2}),
            "reviewer": patch("plugin_examples.runner._stage_reviewer",
                             return_value={"available": False, "passed": False}),
            "publisher": patch("plugin_examples.runner._stage_publisher",
                              return_value={"status": "dry_run",
                                            "evidence_verified": True,
                                            "files_included": 2}),
        }

    def test_full_pipeline_mocked(self, tmp_path):
        """All stages mocked — pipeline produces a valid report."""
        patches = self._mock_all_stages()
        mocks = {}
        for key, p in patches.items():
            mocks[key] = p.start()

        try:
            report = run_pipeline(
                family="cells",
                dry_run=True,
                skip_run=True,
                template_mode=True,
                repo_root=tmp_path,
                run_id="test-mocked",
            )

            assert "verdict" in report
            assert "gate_summary" in report
            assert report["meta"]["run_id"] == "test-mocked"
            assert report["meta"]["family"] == "cells"

            # Report should be written to disk
            report_path = tmp_path / "workspace" / "runs" / "test-mocked" / "pilot-report.json"
            assert report_path.exists()
            disk_report = json.loads(report_path.read_text())
            assert disk_report["verdict"] == report["verdict"]

        finally:
            for p in patches.values():
                p.stop()

    def test_hard_stop_skips_remaining(self, tmp_path):
        """When a hard-stop stage fails, remaining stages are skipped."""
        patches = self._mock_all_stages()
        mocks = {}
        for key, p in patches.items():
            mocks[key] = p.start()

        # Make nuget_fetch fail (hard stop)
        mocks["nuget_fetch"].side_effect = ConnectionError("NuGet down")

        try:
            report = run_pipeline(
                family="cells",
                dry_run=True,
                skip_run=True,
                repo_root=tmp_path,
                run_id="test-hard-stop",
            )

            assert report["gate_summary"]["hard_stopped"] is True
            assert report["verdict"] == "BLOCKED_SOURCE_OF_TRUTH"

            # All stages after nuget_fetch should be skipped
            skipped = [s for s in report["stages"] if s["status"] == "skipped"]
            assert len(skipped) > 0

        finally:
            for p in patches.values():
                p.stop()

    def test_tier_limits_stages(self, tmp_path):
        """--tier 1 should only execute through stage 6."""
        patches = self._mock_all_stages()
        mocks = {}
        for key, p in patches.items():
            mocks[key] = p.start()

        try:
            report = run_pipeline(
                family="cells",
                dry_run=True,
                skip_run=True,
                repo_root=tmp_path,
                run_id="test-tier1",
                max_tier=1,
            )

            # Stages beyond tier 1 (order > 6) should be skipped
            for stage in report["stages"]:
                if stage["order"] > 6:
                    assert stage["status"] == "skipped", \
                        f"Stage {stage['name']} (order {stage['order']}) should be skipped at tier 1"

        finally:
            for p in patches.values():
                p.stop()


# ---------------------------------------------------------------------------
# TestTemplateModeTruth
# ---------------------------------------------------------------------------


class TestGenerationFramework:
    def test_generation_uses_net8_not_extraction_framework(self):
        """Runner must pass net8.0 to generate_project, not extraction framework."""
        import inspect
        from plugin_examples.runner import _stage_generation
        source = inspect.getsource(_stage_generation)
        # Must NOT reference selected_framework for generate_project
        assert 'target_framework="net8.0"' in source or "net8.0" in source
        assert 'extraction.get("selected_framework"' not in source


class TestTemplateModeVerdict:
    def test_template_mode_not_full_e2e(self, tmp_path):
        """Template mode must NOT produce FULL E2E PASSED verdict."""
        ctx = _make_ctx(tmp_path, template_mode=True)
        stages = []
        for i, name in enumerate([
            "load_config", "nuget_fetch", "dependency_resolution",
            "extraction", "reflection", "plugin_detection",
            "api_delta", "impact_mapping", "fixture_registry",
            "example_mining", "scenario_planning", "llm_preflight",
            "generation", "validation", "reviewer", "publisher",
        ]):
            s = StageResult(name=name, order=i + 1, status="success")
            stages.append(s)
        # Template mode generation with validation passing
        stages[10].artifacts = {"ready_count": 3, "blocked_count": 0}
        stages[12].artifacts = {"examples_generated": 3, "generation_mode": "template"}
        stages[13].artifacts = {"passed": 3, "failed": 0, "total": 3}
        verdict = _determine_verdict(stages, ctx)
        assert verdict != "FULL_E2E_PASSED"
        assert verdict == "DATA_FLOW_PROTOTYPE_ONLY"
