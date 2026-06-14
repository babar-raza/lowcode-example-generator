"""Integration tests for fallback_registry_lookup stage in runner.py — TC-IMPL-012."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# Import the stage function directly — no need to run the full pipeline
from plugin_examples.runner import PipelineContext, _stage_fallback_registry_lookup


def _make_ctx(
    *,
    family: str = "barcode",
    fallback_strategy: str | None = "capability_registry",
    detection_is_eligible: bool = False,
    run_dir: Path | None = None,
    repo_root: Path | None = None,
) -> PipelineContext:
    """Build a minimal PipelineContext for fallback stage testing."""
    if run_dir is None:
        run_dir = Path(tempfile.mkdtemp())
    if repo_root is None:
        repo_root = Path(tempfile.mkdtemp())

    plugin_detection = SimpleNamespace(fallback_strategy=fallback_strategy)
    config = SimpleNamespace(plugin_detection=plugin_detection)
    detection = SimpleNamespace(is_eligible=detection_is_eligible)

    import dataclasses
    from dataclasses import fields

    # Build a PipelineContext with just the fields we need
    ctx = object.__new__(PipelineContext)
    # Set defaults for all fields
    for f in fields(PipelineContext):
        try:
            object.__setattr__(ctx, f.name, f.default)
        except Exception:
            try:
                object.__setattr__(ctx, f.name, f.default_factory())
            except Exception:
                object.__setattr__(ctx, f.name, None)

    object.__setattr__(ctx, "family", family)
    object.__setattr__(ctx, "run_dir", run_dir)
    object.__setattr__(ctx, "repo_root", repo_root)
    object.__setattr__(ctx, "config", config)
    object.__setattr__(ctx, "detection", detection)
    return ctx


class TestFallbackStageSkipsForLowCodeFamilies:
    def test_lowcode_families_skip_fallback_stage_when_strategy_none(self):
        """When fallback_strategy=None, stage returns SKIPPED immediately."""
        ctx = _make_ctx(fallback_strategy=None)
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "SKIPPED"
        assert "fallback_strategy is None" in result["reason"]

    def test_fallback_strategy_null_preserves_existing_detection_path(self):
        """fallback_strategy=None must not mutate ctx.detection or any ctx attribute."""
        ctx = _make_ctx(fallback_strategy=None, detection_is_eligible=True)
        original_detection = ctx.detection
        _stage_fallback_registry_lookup(ctx)
        assert ctx.detection is original_detection


class TestFallbackStageSkipsWhenLowCodeDetected:
    def test_fallback_strategy_set_but_lowcode_namespace_found_skips(self):
        """If detection.is_eligible=True (LowCode namespace found), stage must SKIP."""
        ctx = _make_ctx(fallback_strategy="capability_registry", detection_is_eligible=True)
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "SKIPPED"
        assert "LowCode namespace found" in result["reason"]


class TestFallbackStageSkipsWhenNoRegistryFile:
    def test_fallback_stage_skips_gracefully_when_no_registry_file(self):
        """Missing registry YAML must cause a clean SKIPPED (not an exception)."""
        ctx = _make_ctx(fallback_strategy="capability_registry", detection_is_eligible=False)
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "SKIPPED"
        assert "no registry file" in result["reason"]


class TestFallbackStageLoadsRegistryEntries:
    def _make_registry(self, tmp_path, entries_yaml: str) -> tuple[Path, Path]:
        registry_dir = tmp_path / "pipeline" / "plugin-capability-registry"
        registry_dir.mkdir(parents=True, exist_ok=True)
        (registry_dir / "barcode.yaml").write_text(f"entries:\n{entries_yaml}", encoding="utf-8")
        run_dir = tmp_path / "run"
        run_dir.mkdir(exist_ok=True)
        return tmp_path, run_dir

    def test_fallback_strategy_capability_registry_loads_probe_candidate(self, tmp_path):
        """PROBE_CANDIDATE entries are loaded as usable fallback candidates."""
        repo_root, run_dir = self._make_registry(
            tmp_path,
            "  - {family: barcode, package_id: Aspose.BarCode, type_name: BarcodeGenerator,"
            " method_name: Save, status: PROBE_CANDIDATE, confidence_score: 0.75}\n",
        )
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=run_dir,
            repo_root=repo_root,
        )
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "OK"
        assert result["candidate_count"] == 1
        data = json.loads((run_dir / "fallback_candidates.json").read_text())
        assert data["usable_entries"] == 1
        assert data["status_counts"]["PROBE_CANDIDATE"] == 1

    def test_fallback_strategy_capability_registry_loads_probe_confirmed(self, tmp_path):
        """PROBE_CONFIRMED entries are loaded as usable fallback candidates."""
        repo_root, run_dir = self._make_registry(
            tmp_path,
            "  - {family: barcode, package_id: Aspose.BarCode, type_name: BarcodeGenerator,"
            " method_name: Save, status: PROBE_CONFIRMED, confidence_score: 0.95}\n",
        )
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=run_dir,
            repo_root=repo_root,
        )
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "OK"
        assert result["candidate_count"] == 1
        data = json.loads((run_dir / "fallback_candidates.json").read_text())
        assert data["usable_entries"] == 1
        assert data["status_counts"]["PROBE_CONFIRMED"] == 1

    def test_fallback_stage_excludes_probe_failed(self, tmp_path):
        """PROBE_FAILED entries must NOT be loaded as usable candidates."""
        repo_root, run_dir = self._make_registry(
            tmp_path,
            "  - {family: barcode, package_id: Aspose.BarCode, type_name: BarcodeGenerator,"
            " method_name: Save, status: PROBE_FAILED, failure_taxonomy: PROBE_FAILED_LICENSE}\n",
        )
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=run_dir,
            repo_root=repo_root,
        )
        result = _stage_fallback_registry_lookup(ctx)
        assert result["status"] == "OK"
        assert result["candidate_count"] == 0
        data = json.loads((run_dir / "fallback_candidates.json").read_text())
        assert data["usable_entries"] == 0
        assert data["excluded_entries"] == 1

    def test_fallback_stage_excludes_blocked_package_unavailable(self, tmp_path):
        """BLOCKED_PACKAGE_UNAVAILABLE entries must NOT be loaded."""
        repo_root, run_dir = self._make_registry(
            tmp_path,
            "  - {family: barcode, package_id: Aspose.BarCode,"
            " type_name: null, method_name: null, status: BLOCKED_PACKAGE_UNAVAILABLE}\n",
        )
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=run_dir,
            repo_root=repo_root,
        )
        result = _stage_fallback_registry_lookup(ctx)
        assert result["candidate_count"] == 0
        data = json.loads((run_dir / "fallback_candidates.json").read_text())
        assert data["excluded_entries"] == 1

    def test_fallback_artifact_has_status_counts_and_exclusion_reason(self, tmp_path):
        """fallback_candidates.json must have status_counts and exclusion_reason fields."""
        repo_root, run_dir = self._make_registry(
            tmp_path,
            "  - {status: PROBE_CONFIRMED, type_name: A, method_name: S}\n"
            "  - {status: PROBE_FAILED, type_name: B, method_name: S, failure_taxonomy: PROBE_FAILED_BUILD}\n",
        )
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=run_dir,
            repo_root=repo_root,
        )
        _stage_fallback_registry_lookup(ctx)
        data = json.loads((run_dir / "fallback_candidates.json").read_text())
        assert "status_counts" in data
        assert "exclusion_reason" in data
        assert data["total_registry_entries"] == 2
        assert data["usable_entries"] == 1
        assert data["excluded_entries"] == 1


class TestFallbackStageDoesNotMutateFormatAuthority:
    def test_fallback_stage_does_not_mutate_format_authority(self, tmp_path):
        """format-authority/ directory must not be touched by fallback stage."""
        fa_dir = tmp_path / "pipeline" / "format-authority"
        fa_dir.mkdir(parents=True)
        manifest = fa_dir / "manifest.json"
        manifest.write_text('{"entries": []}', encoding="utf-8")

        # No registry file so stage will SKIP — but format-authority still untouched
        ctx = _make_ctx(
            family="barcode",
            fallback_strategy="capability_registry",
            detection_is_eligible=False,
            run_dir=tmp_path / "run",
            repo_root=tmp_path,
        )

        before_mtime = manifest.stat().st_mtime
        _stage_fallback_registry_lookup(ctx)
        after_mtime = manifest.stat().st_mtime

        assert before_mtime == after_mtime, "format-authority/manifest.json was mutated"
