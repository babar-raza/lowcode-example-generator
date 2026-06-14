"""Integration test: non-LowCode end-to-end dry-run — Wave 25 Lane F.

Verifies that the full pipeline path for a non-LowCode family (barcode/svg/cad)
produces the correct artifact structure when run with dry_run=True.

Does NOT require GITHUB_TOKEN.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_probe_confirmed_registry(tmp_path: Path, family: str) -> None:
    """Write a capability registry with one PROBE_CONFIRMED entry."""
    import yaml

    registry_dir = tmp_path / "pipeline" / "plugin-capability-registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "plugin_slug": f"convert-{family}",
        "status": "PROBE_CONFIRMED",
        "type_name": f"Aspose.{family.capitalize()}.Plugins.{family.capitalize()}Converter",
        "method_name": "Process",
        "confidence_score": 0.9,
        "probe_evidence": {"probe_run_id": "test-run-001", "exit_code": 0},
        "last_validated": "2026-06-01T00:00:00Z",
    }
    (registry_dir / f"{family}.yaml").write_text(
        yaml.dump({"family": family, "entries": [entry]}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.legacy
def test_nonlowcode_fallback_candidates_populated(tmp_path):
    """After _stage_fallback_registry_lookup, ctx.fallback_candidates must be non-empty."""
    _make_probe_confirmed_registry(tmp_path, "barcode")

    from plugin_examples.runner import PipelineContext, _stage_fallback_registry_lookup

    config = MagicMock()
    config.plugin_detection.fallback_strategy = "capability_registry"
    config.plugin_detection.namespace_patterns = []

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "barcode"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.repo_root = tmp_path
    ctx.detection = None
    ctx.config = config
    ctx.fallback_candidates = None

    _stage_fallback_registry_lookup(ctx)

    assert ctx.fallback_candidates is not None
    assert len(ctx.fallback_candidates) >= 1
    assert ctx.fallback_candidates[0].namespace_source == "NON_LOWCODE_PLUGIN"
    assert ctx.fallback_candidates[0].discovery_method == "capability_registry_fallback"


@pytest.mark.legacy
def test_shared_downstream_executor_called_for_nonlowcode(tmp_path):
    """SharedDownstreamExecutor.execute_batch must be called when fallback_candidates present."""
    from plugin_examples.fixture_factory.shared_downstream_executor import PluginCandidate, SharedDownstreamExecutor
    from plugin_examples.runner import PipelineContext, _generate_nonlowcode_examples

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "barcode"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.generated_projects = []
    ctx.fallback_candidates = [
        PluginCandidate(
            slug="barcode-converter",
            family="barcode",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
        )
    ]

    with patch.object(
        SharedDownstreamExecutor, "execute_batch", wraps=SharedDownstreamExecutor(strict=False).execute_batch
    ) as mock_exec:
        result = _generate_nonlowcode_examples(ctx)

    assert result["generation_mode"] == "nonlowcode_executor"
    assert result["examples_generated"] >= 1


@pytest.mark.legacy
def test_nonlowcode_generation_writes_summary_json(tmp_path):
    """_generate_nonlowcode_examples must write nonlowcode-generation-summary.json."""
    from plugin_examples.fixture_factory.shared_downstream_executor import PluginCandidate
    from plugin_examples.runner import PipelineContext, _generate_nonlowcode_examples

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "svg"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.generated_projects = []
    ctx.fallback_candidates = [
        PluginCandidate(
            slug="svg-converter",
            family="svg",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
        )
    ]

    _generate_nonlowcode_examples(ctx)

    summary_path = tmp_path / "run" / "nonlowcode-generation-summary.json"
    assert summary_path.exists()
    data = json.loads(summary_path.read_text())
    assert "candidates" in data
    assert "passed" in data
    assert "failed" in data


@pytest.mark.legacy
def test_nonlowcode_pr_packet_assembled_in_results(tmp_path):
    """DownstreamResult pr_packet must have feat(plugins): prefix for NON_LOWCODE_PLUGIN."""
    from plugin_examples.fixture_factory.shared_downstream_executor import PluginCandidate
    from plugin_examples.runner import PipelineContext, _generate_nonlowcode_examples

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "cad"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.generated_projects = []
    ctx.fallback_candidates = [
        PluginCandidate(
            slug="cad-converter",
            family="cad",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
        )
    ]

    _generate_nonlowcode_examples(ctx)

    assert len(ctx.generated_projects) >= 1
    pr_packet = ctx.generated_projects[0]["pr_packet"]
    assert pr_packet["pr_title_prefix"] == "feat(plugins):"
    assert pr_packet["namespace_source"] == "NON_LOWCODE_PLUGIN"


@pytest.mark.legacy
def test_probe_candidate_not_in_generation_candidates(tmp_path):
    """PROBE_CANDIDATE entries must NOT reach the generation stage."""
    _make_probe_confirmed_registry(tmp_path, "cad")

    # Override with a registry that has only PROBE_CANDIDATE
    import yaml

    registry_dir = tmp_path / "pipeline" / "plugin-capability-registry"
    (registry_dir / "cad.yaml").write_text(
        yaml.dump(
            {
                "family": "cad",
                "entries": [
                    {"plugin_slug": "not-validated", "status": "PROBE_CANDIDATE"},
                ],
            }
        ),
        encoding="utf-8",
    )

    from plugin_examples.runner import PipelineContext, _stage_fallback_registry_lookup

    config = MagicMock()
    config.plugin_detection.fallback_strategy = "capability_registry"
    config.plugin_detection.namespace_patterns = []

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "cad"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.repo_root = tmp_path
    ctx.detection = None
    ctx.config = config
    ctx.fallback_candidates = None

    _stage_fallback_registry_lookup(ctx)

    # Must be empty — PROBE_CANDIDATE does not feed generation
    assert ctx.fallback_candidates == []


def test_nonlowcode_parity_pr_title_prefix():
    """build_nonlowcode_pr must use feat(plugins): title and lowcode/wave* branch."""
    from plugin_examples.publisher.pr_builder import build_nonlowcode_pr

    pr = build_nonlowcode_pr(
        family="barcode",
        wave="wave25",
        examples_count=4,
        package_version="26.5.0",
        examples_list=["barcode-reader", "barcode-writer"],
    )

    assert pr.title.startswith("feat(plugins):")
    assert "barcode" in pr.title.lower()
    assert pr.branch == "lowcode/wave25/barcode-plugin-examples"
    assert "4 packages" in pr.title or "4" in pr.title


# ---------------------------------------------------------------------------
# TC-H09: Stage chaining integration test (live pipeline path)
# ---------------------------------------------------------------------------


def test_nonlowcode_stage_chaining_sot_to_planning(tmp_path):
    """TC-H09: SOT proof + scenario planning chain correctly for non-LowCode.

    Verifies:
    1. _stage_plugin_detection writes nonlowcode SOT proof and passes gate
    2. _stage_scenario_planning returns REGISTRY_PLANNED with ready_count >= 1
    3. ctx.nonlowcode_proof_path is set and file exists
    4. ctx.planning has real Scenario objects from registry
    """
    import dataclasses
    from types import SimpleNamespace

    import yaml

    from plugin_examples.runner import (
        PipelineContext,
        _stage_plugin_detection,
        _stage_scenario_planning,
    )

    # Build minimal PipelineContext
    ctx = object.__new__(PipelineContext)
    for f in dataclasses.fields(PipelineContext):
        if f.default_factory is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default_factory())
        elif f.default is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default)
        else:
            object.__setattr__(ctx, f.name, None)

    object.__setattr__(ctx, "family", "barcode")
    object.__setattr__(ctx, "run_id", "test-chain-001")
    object.__setattr__(ctx, "dry_run", True)
    object.__setattr__(ctx, "skip_run", False)
    object.__setattr__(ctx, "template_mode", True)
    object.__setattr__(ctx, "require_llm", False)
    object.__setattr__(ctx, "require_validation", False)
    object.__setattr__(ctx, "require_reviewer", False)
    object.__setattr__(ctx, "repo_root", tmp_path / "repo")
    object.__setattr__(ctx, "run_dir", tmp_path)
    object.__setattr__(ctx, "evidence_dir", tmp_path / "evidence")

    (tmp_path / "repo").mkdir(exist_ok=True)
    (tmp_path / "evidence").mkdir(exist_ok=True)

    # Write a registry YAML with PROBE_CONFIRMED entry
    reg_dir = tmp_path / "repo" / "pipeline" / "plugin-capability-registry"
    reg_dir.mkdir(parents=True)
    entry = {
        "plugin_slug": "generate-barcode",
        "status": "PROBE_CONFIRMED",
        "type_name": "BarcodeGenerator",
        "namespace": "Aspose.BarCode.Generation",
        "method_name": "Save",
        "operation_kind": "BARCODE_GENERATION",
        "candidate_methods": ["Save"],
        "selected_api_mapping": {
            "type_name": "BarcodeGenerator",
            "namespace": "Aspose.BarCode.Generation",
            "constructor": "BarcodeGenerator(EncodeTypes, string)",
            "method_name": "Save",
            "output_format_enum": "BarCodeImageFormat",
        },
    }
    (reg_dir / "barcode.yaml").write_text(
        yaml.dump({"entries": [entry]}), encoding="utf-8",
    )

    # Set up config as discovery_only with fallback
    ctx.config = SimpleNamespace(
        family="barcode",
        display_name="Aspose.BarCode for .NET",
        enabled=True,
        status="discovery_only",
        plugin_detection=SimpleNamespace(
            namespace_patterns=["Aspose.BarCode.LowCode"],
            fallback_strategy="capability_registry",
        ),
        nuget=SimpleNamespace(package_id="Aspose.BarCode", version_policy="latest-stable"),
    )

    # Set up detection result (not eligible = non-LowCode)
    ctx.detection = SimpleNamespace(
        matched_namespaces=[],
        is_eligible=False,
        public_plugin_type_count=0,
        public_plugin_method_count=0,
    )
    ctx.download_manifest = {"version": "26.5.0", "sha256": "abc123"}
    ctx.extraction = {"selected_framework": "net8.0", "dll_path": "/fake/dll", "xml_path": None}
    ctx.catalog = {"namespaces": []}
    ctx.catalog_path = tmp_path / "catalog.json"
    ctx.deps = []

    # Stage 1: Plugin detection (SOT gate)
    with patch("plugin_examples.plugin_detector.detect_plugin_namespaces", return_value=ctx.detection), \
         patch("plugin_examples.plugin_detector.write_product_inventory"), \
         patch("plugin_examples.plugin_detector.write_source_of_truth_proof", return_value=tmp_path / "proof.json"), \
         patch("plugin_examples.plugin_detector.assert_source_of_truth_eligible") as mock_lowcode_assert:
        detection_result = _stage_plugin_detection(ctx)

    # LowCode gate NOT called; non-LowCode gate ran instead
    mock_lowcode_assert.assert_not_called()
    assert detection_result["eligible"] is False
    assert hasattr(ctx, "nonlowcode_proof_path")
    assert ctx.nonlowcode_proof_path.exists()

    # Stage 2: Scenario planning (REGISTRY_PLANNED)
    planning_result = _stage_scenario_planning(ctx)

    assert planning_result["status"] == "REGISTRY_PLANNED"
    assert planning_result["ready_count"] >= 1
    assert planning_result["planning_source"] == "capability_registry"
    assert ctx.planning is not None
    assert ctx.planning.ready_count >= 1

    # Verify scenario fields
    scenario = ctx.planning.ready_scenarios[0]
    assert scenario.scenario_id == "barcode-generate-barcode"
    assert scenario.target_type == "Aspose.BarCode.Generation.BarcodeGenerator"


def test_nonlowcode_stage_chaining_generation_to_validation(tmp_path):
    """TC-H09b: Generation + validation chain correctly for non-LowCode.

    Extends TC-H09 by verifying:
    1. _stage_generation produces project with project_dir and registry_template mode
    2. _stage_validation processes the generated project (with mocked dotnet)
    3. Full 4-stage chain: SOT → planning → generation → validation
    """
    import dataclasses
    from types import SimpleNamespace

    import yaml

    from plugin_examples.runner import (
        PipelineContext,
        _stage_generation,
        _stage_scenario_planning,
        _stage_validation,
    )
    from plugin_examples.verifier_bridge.dotnet_runner import (
        DotnetResult,
        ValidationResult,
    )

    # Build minimal PipelineContext
    ctx = object.__new__(PipelineContext)
    for f in dataclasses.fields(PipelineContext):
        if f.default_factory is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default_factory())
        elif f.default is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default)
        else:
            object.__setattr__(ctx, f.name, None)

    object.__setattr__(ctx, "family", "barcode")
    object.__setattr__(ctx, "run_id", "test-chain-gen-val-001")
    object.__setattr__(ctx, "dry_run", True)
    object.__setattr__(ctx, "skip_run", False)
    object.__setattr__(ctx, "template_mode", True)
    object.__setattr__(ctx, "require_llm", False)
    object.__setattr__(ctx, "require_validation", False)
    object.__setattr__(ctx, "require_reviewer", False)
    object.__setattr__(ctx, "repo_root", tmp_path / "repo")
    object.__setattr__(ctx, "run_dir", tmp_path)
    object.__setattr__(ctx, "evidence_dir", tmp_path / "evidence")
    object.__setattr__(ctx, "llm_available", False)

    (tmp_path / "repo").mkdir(exist_ok=True)
    (tmp_path / "evidence").mkdir(exist_ok=True)

    # Write registry YAML
    reg_dir = tmp_path / "repo" / "pipeline" / "plugin-capability-registry"
    reg_dir.mkdir(parents=True)
    entry = {
        "plugin_slug": "generate-barcode",
        "status": "PROBE_CONFIRMED",
        "type_name": "BarcodeGenerator",
        "namespace": "Aspose.BarCode.Generation",
        "method_name": "Save",
        "operation_kind": "BARCODE_GENERATION",
        "candidate_methods": ["Save"],
        "selected_api_mapping": {
            "type_name": "BarcodeGenerator",
            "namespace": "Aspose.BarCode.Generation",
            "constructor": "BarcodeGenerator(EncodeTypes, string)",
            "method_name": "Save",
            "output_format_enum": "BarCodeImageFormat",
        },
    }
    (reg_dir / "barcode.yaml").write_text(
        yaml.dump({"entries": [entry]}), encoding="utf-8",
    )

    # Config
    ctx.config = SimpleNamespace(
        family="barcode",
        display_name="Aspose.BarCode for .NET",
        enabled=True,
        status="discovery_only",
        plugin_detection=SimpleNamespace(
            namespace_patterns=["Aspose.BarCode.LowCode"],
            fallback_strategy="capability_registry",
        ),
        nuget=SimpleNamespace(package_id="Aspose.BarCode", version_policy="latest-stable"),
    )
    ctx.detection = SimpleNamespace(
        matched_namespaces=[],
        is_eligible=False,
        public_plugin_type_count=0,
        public_plugin_method_count=0,
    )
    ctx.download_manifest = {"version": "26.5.0", "sha256": "abc123"}
    ctx.catalog = {"namespaces": []}
    ctx.catalog_path = tmp_path / "catalog.json"

    # --- Stage 2: Scenario planning ---
    planning_result = _stage_scenario_planning(ctx)
    assert planning_result["status"] == "REGISTRY_PLANNED"
    assert ctx.planning.ready_count >= 1

    # --- Stage 3: Generation (registry_template) ---
    gen_result = _stage_generation(ctx)

    assert gen_result["generation_mode"] == "registry_template"
    assert gen_result["generation_quality_tier"] == "TEMPLATE_REGISTRY"
    assert gen_result["examples_generated"] >= 1
    assert len(ctx.generated_projects) >= 1
    # Verify project has project_dir (generated by generate_project)
    proj = ctx.generated_projects[0]
    assert "project_dir" in proj
    assert "scenario_id" in proj
    assert proj["scenario_id"] == "barcode-generate-barcode"

    # --- Stage 4: Validation (mocked dotnet) ---
    from plugin_examples.health.doctor import HealthCheck

    mock_hc = HealthCheck("dotnet_sdk", "PASS", "dotnet 9.0.200", False)
    mock_vr = ValidationResult(
        scenario_id=proj["scenario_id"],
        passed=True,
        build=DotnetResult(operation="build", success=True, stdout="Build succeeded."),
        run=DotnetResult(operation="run", success=True, stdout="Example: barcode-generate-barcode", exit_code=0),
    )

    with patch("plugin_examples.health.doctor.check_dotnet_sdk", return_value=mock_hc), \
         patch("plugin_examples.verifier_bridge.run_dotnet_validation", return_value=mock_vr), \
         patch("plugin_examples.verifier_bridge.dotnet_runner.write_validation_results"):
        val_result = _stage_validation(ctx)

    assert val_result["total"] >= 1
    assert val_result["passed"] >= 1
    assert val_result["sdk_available"] is True
    assert val_result["sdk_degraded"] == 0
    assert val_result["nonlowcode_limited"] == 0
