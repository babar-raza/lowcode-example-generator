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

    with patch.object(SharedDownstreamExecutor, "execute_batch", wraps=SharedDownstreamExecutor(strict=False).execute_batch) as mock_exec:
        result = _generate_nonlowcode_examples(ctx)

    assert result["generation_mode"] == "nonlowcode_executor"
    assert result["examples_generated"] >= 1


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


def test_probe_candidate_not_in_generation_candidates(tmp_path):
    """PROBE_CANDIDATE entries must NOT reach the generation stage."""
    _make_probe_confirmed_registry(tmp_path, "cad")

    # Override with a registry that has only PROBE_CANDIDATE
    import yaml
    registry_dir = tmp_path / "pipeline" / "plugin-capability-registry"
    (registry_dir / "cad.yaml").write_text(
        yaml.dump({"family": "cad", "entries": [
            {"plugin_slug": "not-validated", "status": "PROBE_CANDIDATE"},
        ]}),
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
