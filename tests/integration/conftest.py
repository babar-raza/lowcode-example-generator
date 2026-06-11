"""Shared fixtures for integration tests."""

from __future__ import annotations

import dataclasses
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from plugin_examples.runner import PipelineContext


@pytest.fixture
def tmp_run_dir(tmp_path: Path) -> Path:
    """Create an isolated run directory with evidence subdirectory."""
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    return tmp_path


@pytest.fixture
def mock_pipeline_context(tmp_run_dir: Path) -> PipelineContext:
    """Build a minimal PipelineContext using the object.__new__ pattern."""
    ctx = object.__new__(PipelineContext)
    for f in dataclasses.fields(PipelineContext):
        try:
            object.__setattr__(ctx, f.name, f.default)
        except Exception:
            try:
                object.__setattr__(ctx, f.name, f.default_factory())
            except Exception:
                object.__setattr__(ctx, f.name, None)

    object.__setattr__(ctx, "family", "cells")
    object.__setattr__(ctx, "run_id", "test-run-001")
    object.__setattr__(ctx, "dry_run", True)
    object.__setattr__(ctx, "skip_run", False)
    object.__setattr__(ctx, "template_mode", False)
    object.__setattr__(ctx, "require_llm", False)
    object.__setattr__(ctx, "require_validation", False)
    object.__setattr__(ctx, "require_reviewer", False)
    object.__setattr__(ctx, "repo_root", tmp_run_dir / "repo")
    object.__setattr__(ctx, "run_dir", tmp_run_dir)
    object.__setattr__(ctx, "evidence_dir", tmp_run_dir / "evidence")

    # Create directories
    (tmp_run_dir / "repo").mkdir(exist_ok=True)
    (tmp_run_dir / "evidence").mkdir(exist_ok=True)

    return ctx


@pytest.fixture
def mock_family_config() -> SimpleNamespace:
    """Return a minimal cells-like family config."""
    return SimpleNamespace(
        family="cells",
        display_name="Cells",
        enabled=True,
        status="active",
        plugin_detection=SimpleNamespace(
            namespace_patterns=["Aspose.Cells.LowCode"],
            fallback_strategy=None,
        ),
        nuget=SimpleNamespace(
            package_id="Aspose.Cells",
            version_policy="latest-stable",
        ),
        github=SimpleNamespace(
            official_examples_repo=SimpleNamespace(
                owner="aspose-cells",
                repo="Aspose.Cells-for-.NET",
                branch="master",
            ),
            published_plugin_examples_repo=SimpleNamespace(
                owner="aspose-cells",
                repo="Aspose.Cells-for-.NET",
                branch="master",
            ),
        ),
        generation=SimpleNamespace(
            min_examples_per_family=1,
            max_examples_per_monthly_run=10,
        ),
        validation=SimpleNamespace(
            require_restore=True,
            require_build=True,
            require_run=True,
            require_output_validation=False,
            require_example_reviewer=False,
        ),
    )
