"""Tests for non-LowCode fallback pipeline healing (Phase 2).

Validates that:
- discovery_only families with fallback_strategy can proceed through _stage_load_config
- discovery_only families WITHOUT fallback_strategy are still blocked
- source-of-truth gate is skipped when fallback_strategy is set and detection is not eligible
- source-of-truth gate still runs for LowCode families (no fallback_strategy)
- scenario planning is skipped in fallback mode (non-LowCode with fallback_strategy)
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import plugin_examples.family_config  # noqa: F401 — ensure module loaded for patch()
from plugin_examples.runner import (
    PipelineContext,
    _stage_load_config,
    _stage_plugin_detection,
    _stage_scenario_planning,
    _stage_validation,
)


def _make_ctx(tmp_path: Path, family: str = "barcode") -> PipelineContext:
    """Build a minimal PipelineContext."""
    ctx = object.__new__(PipelineContext)
    for f in dataclasses.fields(PipelineContext):
        if f.default_factory is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default_factory())
        elif f.default is not dataclasses.MISSING:
            object.__setattr__(ctx, f.name, f.default)
        else:
            object.__setattr__(ctx, f.name, None)

    object.__setattr__(ctx, "family", family)
    object.__setattr__(ctx, "run_id", "test-fallback-001")
    object.__setattr__(ctx, "dry_run", True)
    object.__setattr__(ctx, "skip_run", False)
    object.__setattr__(ctx, "template_mode", False)
    object.__setattr__(ctx, "require_llm", False)
    object.__setattr__(ctx, "require_validation", False)
    object.__setattr__(ctx, "require_reviewer", False)
    object.__setattr__(ctx, "repo_root", tmp_path / "repo")
    object.__setattr__(ctx, "run_dir", tmp_path)
    object.__setattr__(ctx, "evidence_dir", tmp_path / "evidence")

    (tmp_path / "repo").mkdir(exist_ok=True)
    (tmp_path / "evidence").mkdir(exist_ok=True)

    return ctx


def _make_config(family: str, status: str, fallback_strategy: str | None) -> SimpleNamespace:
    """Build a family config with specified status and fallback."""
    return SimpleNamespace(
        family=family,
        display_name=f"Aspose.{family.title()} for .NET",
        enabled=True,
        status=status,
        plugin_detection=SimpleNamespace(
            namespace_patterns=[f"Aspose.{family.title()}.LowCode"],
            fallback_strategy=fallback_strategy,
        ),
        nuget=SimpleNamespace(
            package_id=f"Aspose.{family.title()}",
            version_policy="latest-stable",
        ),
        github=SimpleNamespace(
            official_examples_repo=SimpleNamespace(owner="aspose", repo="test", branch="main"),
            published_plugin_examples_repo=SimpleNamespace(owner="aspose", repo="test", branch="main"),
        ),
        fixtures=SimpleNamespace(sources=[]),
        existing_examples=SimpleNamespace(sources=[]),
        generation=SimpleNamespace(
            min_examples_per_family=1,
            max_examples_per_monthly_run=5,
            allow_new_fixtures=True,
            allow_generated_input_files=True,
            allowed_types=[],
            preferred_methods_per_type=None,
        ),
        validation=SimpleNamespace(
            require_restore=True,
            require_build=True,
            require_run=True,
            require_output_validation=False,
            require_example_reviewer=False,
        ),
        template_hints=SimpleNamespace(default_fixture_extension=".xlsx"),
        llm=SimpleNamespace(provider_order=["llm_professionalize"]),
    )


class TestDiscoveryOnlyFallbackGuard:
    """TC-H02: discovery_only families with fallback_strategy should not be blocked."""

    def test_discovery_only_with_fallback_does_not_raise(self, tmp_path: Path) -> None:
        config = _make_config("barcode", "discovery_only", "capability_registry")
        ctx = _make_ctx(tmp_path, "barcode")

        config_dir = tmp_path / "repo" / "pipeline" / "configs" / "families"
        config_dir.mkdir(parents=True)
        (config_dir / "barcode.yml").write_text("family: barcode\n")

        with patch("plugin_examples.family_config.load_family_config", return_value=config):
            result = _stage_load_config(ctx)

        assert result["family"] == "barcode"
        assert ctx.config.status == "discovery_only"

    def test_discovery_only_without_fallback_raises(self, tmp_path: Path) -> None:
        config = _make_config("testfam", "discovery_only", None)
        ctx = _make_ctx(tmp_path, "testfam")

        config_dir = tmp_path / "repo" / "pipeline" / "configs" / "families"
        config_dir.mkdir(parents=True)
        (config_dir / "testfam.yml").write_text("family: testfam\n")

        with patch("plugin_examples.family_config.load_family_config", return_value=config), pytest.raises(RuntimeError, match="discovery_only"):
            _stage_load_config(ctx)

    def test_active_status_still_works(self, tmp_path: Path) -> None:
        config = _make_config("cells", "active", None)
        ctx = _make_ctx(tmp_path, "cells")

        config_dir = tmp_path / "repo" / "pipeline" / "configs" / "families"
        config_dir.mkdir(parents=True)
        (config_dir / "cells.yml").write_text("family: cells\n")

        with patch("plugin_examples.family_config.load_family_config", return_value=config):
            result = _stage_load_config(ctx)

        assert result["family"] == "cells"


class TestSourceOfTruthGateConditional:
    """TC-H01: source-of-truth gate runs for ALL families (LowCode and non-LowCode)."""

    def test_nonlowcode_gate_runs_when_fallback_and_not_eligible(self, tmp_path: Path) -> None:
        ctx = _make_ctx(tmp_path, "barcode")
        ctx.config = _make_config("barcode", "discovery_only", "capability_registry")
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

        # Create a registry YAML with a PROBE_CONFIRMED entry so the non-LowCode SOT gate passes
        reg_dir = tmp_path / "repo" / "pipeline" / "plugin-capability-registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "barcode.yaml").write_text(
            "entries:\n  - plugin_slug: generate-barcode\n    status: PROBE_CONFIRMED\n    type_name: BarcodeGenerator\n    namespace: Aspose.BarCode.Generation\n    method_name: Save\n"
        )

        with patch("plugin_examples.plugin_detector.detect_plugin_namespaces", return_value=ctx.detection), \
             patch("plugin_examples.plugin_detector.write_product_inventory"), \
             patch("plugin_examples.plugin_detector.write_source_of_truth_proof", return_value=tmp_path / "proof.json"), \
             patch("plugin_examples.plugin_detector.assert_source_of_truth_eligible") as mock_lowcode_assert:

            result = _stage_plugin_detection(ctx)

        # LowCode gate NOT called (non-LowCode path); non-LowCode gate writes its own proof
        mock_lowcode_assert.assert_not_called()
        assert result["eligible"] is False
        # Non-LowCode SOT proof should have been written
        assert hasattr(ctx, "nonlowcode_proof_path")
        assert ctx.nonlowcode_proof_path.exists()

    def test_gate_runs_when_no_fallback(self, tmp_path: Path) -> None:
        ctx = _make_ctx(tmp_path, "cells")
        ctx.config = _make_config("cells", "active", None)
        ctx.detection = SimpleNamespace(
            matched_namespaces=[SimpleNamespace(namespace="Aspose.Cells.LowCode")],
            is_eligible=True,
            public_plugin_type_count=5,
            public_plugin_method_count=20,
        )
        ctx.download_manifest = {"version": "26.5.0", "sha256": "abc123"}
        ctx.extraction = {"selected_framework": "net8.0", "dll_path": "/fake/dll", "xml_path": None}
        ctx.catalog = {"namespaces": []}
        ctx.catalog_path = tmp_path / "catalog.json"
        ctx.deps = []

        with patch("plugin_examples.plugin_detector.detect_plugin_namespaces", return_value=ctx.detection), \
             patch("plugin_examples.plugin_detector.write_product_inventory"), \
             patch("plugin_examples.plugin_detector.write_source_of_truth_proof", return_value=tmp_path / "proof.json"), \
             patch("plugin_examples.plugin_detector.assert_source_of_truth_eligible") as mock_assert:

            result = _stage_plugin_detection(ctx)

        mock_assert.assert_called_once()
        assert result["eligible"] is True


class TestScenarioPlanningRegistryPlanned:
    """TC-H03: scenario planning uses registry entries for non-LowCode families."""

    def test_scenario_planning_uses_registry_in_fallback_mode(self, tmp_path: Path) -> None:
        ctx = _make_ctx(tmp_path, "barcode")
        ctx.config = _make_config("barcode", "discovery_only", "capability_registry")
        ctx.detection = SimpleNamespace(
            matched_namespaces=[],
            is_eligible=False,
        )

        # Create a registry YAML with PROBE_CONFIRMED entry
        reg_dir = tmp_path / "repo" / "pipeline" / "plugin-capability-registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "barcode.yaml").write_text(
            "entries:\n"
            "  - plugin_slug: generate-barcode\n"
            "    status: PROBE_CONFIRMED\n"
            "    type_name: BarcodeGenerator\n"
            "    namespace: Aspose.BarCode.Generation\n"
            "    method_name: Save\n"
            "    operation_kind: BARCODE_GENERATION\n"
        )

        result = _stage_scenario_planning(ctx)

        assert result["status"] == "REGISTRY_PLANNED"
        assert result["ready_count"] >= 1
        assert result["planning_source"] == "capability_registry"
        assert ctx.planning is not None
        assert ctx.planning.ready_count >= 1

    def test_scenario_planning_not_skipped_for_lowcode(self, tmp_path: Path) -> None:
        """LowCode families (no fallback) should NOT skip scenario planning."""
        ctx = _make_ctx(tmp_path, "cells")
        ctx.config = _make_config("cells", "active", None)
        ctx.detection = SimpleNamespace(
            matched_namespaces=[SimpleNamespace(namespace="Aspose.Cells.LowCode")],
            is_eligible=True,
        )
        # Scenario planning for LowCode will try to import and run plan_scenarios,
        # which needs a full catalog — we just verify it does NOT return SKIPPED_FALLBACK_MODE
        # by checking that it tries to import (and fails in test context)
        with pytest.raises(Exception):
            # Will fail deeper in the function (missing catalog etc.), but NOT with SKIPPED_FALLBACK_MODE
            _stage_scenario_planning(ctx)


class TestValidationLimitedNonLowcode:
    """Validation stage labels non-LowCode projects without project_dir as LIMITED_VALIDATION."""

    def test_nonlowcode_projects_limited_validation(self, tmp_path: Path) -> None:
        ctx = _make_ctx(tmp_path, "barcode")
        ctx.config = _make_config("barcode", "discovery_only", "capability_registry")
        ctx.generated_projects = [
            {
                "slug": "generate-barcode",
                "family": "barcode",
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "discovery_method": "capability_registry_fallback",
                "artifact_contract": {},
                "pr_packet": {},
                "publication_state": "PENDING",
                "evidence": [],
                "errors": [],
            }
        ]
        ctx.llm_available = False
        ctx.template_mode = True
        ctx.healing_intelligence = None
        ctx.lifecycle_registry = None

        result = _stage_validation(ctx)

        assert result["nonlowcode_limited"] == 1
        assert result["total"] == 1  # degraded ValidationResult appended
        assert result["failed"] == 1  # marked as failed (no_project_dir)

    def test_lowcode_projects_not_limited(self, tmp_path: Path) -> None:
        """LowCode projects with project_dir should be validated normally."""
        ctx = _make_ctx(tmp_path, "cells")
        ctx.config = _make_config("cells", "active", None)

        proj_dir = tmp_path / "proj"
        proj_dir.mkdir()
        (proj_dir / "Program.cs").write_text("class P { static void Main() {} }")
        (proj_dir / "test.csproj").write_text("<Project/>")

        ctx.generated_projects = [
            {
                "project_dir": str(proj_dir),
                "scenario_id": "cells-test-001",
                "program_path": str(proj_dir / "Program.cs"),
            }
        ]
        ctx.llm_available = False
        ctx.template_mode = True
        ctx.healing_intelligence = None
        ctx.lifecycle_registry = None

        with patch("plugin_examples.verifier_bridge.run_dotnet_validation") as mock_val, \
             patch("plugin_examples.verifier_bridge.dotnet_runner.write_validation_results"):
            mock_vr = SimpleNamespace(
                passed=True, failure_stage=None,
                build=SimpleNamespace(success=True, stdout="", stderr=""),
                run=SimpleNamespace(success=True, stdout="", stderr="", exit_code=0),
            )
            mock_val.return_value = mock_vr
            result = _stage_validation(ctx)

        assert result["nonlowcode_limited"] == 0
        assert result["total"] == 1
        mock_val.assert_called_once()
