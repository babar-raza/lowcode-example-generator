"""Tests for non-LowCode fallback → generation wiring — Wave 25 Lane F.

Covers:
- _stage_fallback_registry_lookup() sets ctx.fallback_candidates with PROBE_CONFIRMED only
- PROBE_CANDIDATE entries are excluded from ctx.fallback_candidates
- _stage_generation() routes to _generate_nonlowcode_examples() when candidates present
- _stage_generation() skips with no_candidates when no LowCode scenarios and no fallback candidates
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ctx(tmp_path: Path, family: str = "barcode", fallback_strategy: str = "capability_registry"):
    """Create a minimal PipelineContext-like mock for testing."""
    from plugin_examples.runner import PipelineContext

    config = MagicMock()
    config.plugin_detection.fallback_strategy = fallback_strategy
    config.plugin_detection.namespace_patterns = []

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = family
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir(parents=True)
    ctx.repo_root = tmp_path
    ctx.detection = None
    ctx.config = config
    ctx.fallback_candidates = None
    ctx.generated_projects = []
    ctx.planning = None
    ctx.lifecycle_registry = None
    return ctx


def _write_registry(tmp_path: Path, family: str, entries: list[dict]) -> None:
    """Write a capability registry YAML for a family."""
    import yaml

    registry_dir = tmp_path / "pipeline" / "plugin-capability-registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    (registry_dir / f"{family}.yaml").write_text(
        yaml.dump({"family": family, "entries": entries}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Test: _stage_fallback_registry_lookup populates ctx.fallback_candidates
# ---------------------------------------------------------------------------


def test_fallback_lookup_sets_candidates_from_probe_confirmed(tmp_path):
    """PROBE_CONFIRMED entries must end up in ctx.fallback_candidates."""
    _write_registry(
        tmp_path,
        "barcode",
        [
            {"plugin_slug": "barcode-reader", "status": "PROBE_CONFIRMED"},
            {"plugin_slug": "barcode-writer", "status": "PROBE_CONFIRMED"},
        ],
    )
    ctx = _make_ctx(tmp_path)

    from plugin_examples.runner import _stage_fallback_registry_lookup

    result = _stage_fallback_registry_lookup(ctx)

    assert result["status"] == "OK"
    assert result["generation_ready"] == 2
    assert ctx.fallback_candidates is not None
    assert len(ctx.fallback_candidates) == 2
    slugs = {c.slug for c in ctx.fallback_candidates}
    assert "barcode-reader" in slugs
    assert "barcode-writer" in slugs


def test_fallback_lookup_sets_candidates_from_verified_publishable(tmp_path):
    """VERIFIED_PUBLISHABLE entries must end up in ctx.fallback_candidates."""
    _write_registry(
        tmp_path,
        "barcode",
        [
            {"plugin_slug": "barcode-publisher", "status": "VERIFIED_PUBLISHABLE"},
        ],
    )
    ctx = _make_ctx(tmp_path)

    from plugin_examples.runner import _stage_fallback_registry_lookup

    _stage_fallback_registry_lookup(ctx)

    assert ctx.fallback_candidates is not None
    assert len(ctx.fallback_candidates) == 1
    assert ctx.fallback_candidates[0].slug == "barcode-publisher"


def test_fallback_lookup_excludes_probe_candidate(tmp_path):
    """PROBE_CANDIDATE entries must NOT be in ctx.fallback_candidates (require probe first)."""
    _write_registry(
        tmp_path,
        "barcode",
        [
            {"plugin_slug": "unvalidated-plugin", "status": "PROBE_CANDIDATE"},
            {"plugin_slug": "validated-plugin", "status": "PROBE_CONFIRMED"},
        ],
    )
    ctx = _make_ctx(tmp_path)

    from plugin_examples.runner import _stage_fallback_registry_lookup

    result = _stage_fallback_registry_lookup(ctx)

    # Usable = 2 (PROBE_CANDIDATE + PROBE_CONFIRMED), generation_ready = 1 (only PROBE_CONFIRMED)
    assert result["candidate_count"] == 2
    assert result["generation_ready"] == 1
    assert ctx.fallback_candidates is not None
    assert len(ctx.fallback_candidates) == 1
    assert ctx.fallback_candidates[0].slug == "validated-plugin"


def test_fallback_lookup_empty_candidates_when_only_probe_candidate(tmp_path):
    """If all entries are PROBE_CANDIDATE, ctx.fallback_candidates must be empty list."""
    _write_registry(
        tmp_path,
        "barcode",
        [
            {"plugin_slug": "needs-probe", "status": "PROBE_CANDIDATE"},
        ],
    )
    ctx = _make_ctx(tmp_path)

    from plugin_examples.runner import _stage_fallback_registry_lookup

    _stage_fallback_registry_lookup(ctx)

    assert ctx.fallback_candidates == []


def test_fallback_lookup_skips_when_strategy_none(tmp_path):
    """When fallback_strategy is None, stage returns SKIPPED and does not set candidates."""
    ctx = _make_ctx(tmp_path, fallback_strategy=None)
    ctx.config.plugin_detection.fallback_strategy = None

    from plugin_examples.runner import _stage_fallback_registry_lookup

    result = _stage_fallback_registry_lookup(ctx)

    assert result["status"] == "SKIPPED"
    assert ctx.fallback_candidates is None


def test_fallback_lookup_namespace_source_is_non_lowcode(tmp_path):
    """ctx.fallback_candidates entries must have namespace_source=NON_LOWCODE_PLUGIN."""
    _write_registry(
        tmp_path,
        "cad",
        [
            {"plugin_slug": "convert-dwg", "status": "PROBE_CONFIRMED"},
        ],
    )
    ctx = _make_ctx(tmp_path, family="cad")

    from plugin_examples.runner import _stage_fallback_registry_lookup

    _stage_fallback_registry_lookup(ctx)

    assert ctx.fallback_candidates[0].namespace_source == "NON_LOWCODE_PLUGIN"
    assert ctx.fallback_candidates[0].discovery_method == "capability_registry_fallback"


def test_fallback_lookup_writes_json_artifact(tmp_path):
    """_stage_fallback_registry_lookup must write fallback_candidates.json."""
    _write_registry(
        tmp_path,
        "svg",
        [
            {"plugin_slug": "svg-converter", "status": "PROBE_CONFIRMED"},
        ],
    )
    ctx = _make_ctx(tmp_path, family="svg")

    from plugin_examples.runner import _stage_fallback_registry_lookup

    _stage_fallback_registry_lookup(ctx)

    artifact = ctx.run_dir / "fallback_candidates.json"
    assert artifact.exists()
    data = json.loads(artifact.read_text())
    assert data["family"] == "svg"
    assert "generation_ready_entries" in data
    assert data["generation_ready_entries"] == 1


# ---------------------------------------------------------------------------
# Test: _stage_generation routes to non-LowCode path
# ---------------------------------------------------------------------------


@pytest.mark.legacy
def test_generation_routes_to_nonlowcode_when_fallback_candidates_set(tmp_path):
    """When ctx.fallback_candidates is non-empty and no LowCode scenarios, use non-LowCode path."""
    from plugin_examples.fixture_factory.shared_downstream_executor import PluginCandidate
    from plugin_examples.runner import PipelineContext, _generate_nonlowcode_examples

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "barcode"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.generated_projects = []
    ctx.fallback_candidates = [
        PluginCandidate(
            slug="barcode-reader",
            family="barcode",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
        )
    ]

    result = _generate_nonlowcode_examples(ctx)

    assert result.get("generation_mode") == "nonlowcode_executor"
    assert result.get("examples_generated", 0) >= 1


@pytest.mark.legacy
def test_generation_skips_when_no_scenarios_and_no_fallback_candidates(tmp_path):
    """When no LowCode scenarios and no fallback candidates, skip with no_candidates reason."""
    from plugin_examples.runner import PipelineContext, _generate_nonlowcode_examples

    ctx = MagicMock(spec=PipelineContext)
    ctx.family = "barcode"
    ctx.run_dir = tmp_path / "run"
    ctx.run_dir.mkdir()
    ctx.generated_projects = []
    ctx.fallback_candidates = []

    result = _generate_nonlowcode_examples(ctx)

    assert result.get("examples_generated", 0) == 0
    assert result.get("reason") == "no generation-ready fallback candidates"
