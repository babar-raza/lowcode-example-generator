"""Tests for stage-registry.yml optional YAML pilot — Wave 25 Lane I.

Verifies:
- Valid stage-registry.yml loads without error
- Invalid YAML falls back to hardcoded list without crashing
- Missing file falls back to hardcoded list without crashing
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


def _load_stage_registry(yaml_path: Path) -> list[dict] | None:
    """Load stage registry from YAML. Returns None if file missing or invalid."""
    if not yaml_path.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "stages" in data:
            return data["stages"]
        return None
    except Exception:  # noqa: BLE001
        return None


def test_valid_stage_registry_loads(tmp_path):
    """A valid stage-registry.yml must load as a list of stage dicts."""
    stage_yml = tmp_path / "stage-registry.yml"
    stage_yml.write_text(
        "stages:\n  - name: load_config\n    order: 1\n    required: true\n",
        encoding="utf-8",
    )
    stages = _load_stage_registry(stage_yml)
    assert stages is not None
    assert len(stages) == 1
    assert stages[0]["name"] == "load_config"


def test_invalid_yaml_returns_none(tmp_path):
    """Invalid YAML must return None (trigger fallback to hardcoded list)."""
    stage_yml = tmp_path / "stage-registry.yml"
    stage_yml.write_text("stages: [unclosed bracket\n", encoding="utf-8")
    stages = _load_stage_registry(stage_yml)
    assert stages is None


def test_missing_file_returns_none(tmp_path):
    """Missing stage-registry.yml must return None (trigger fallback)."""
    stage_yml = tmp_path / "stage-registry.yml"
    assert not stage_yml.exists()
    stages = _load_stage_registry(stage_yml)
    assert stages is None


def test_production_stage_registry_is_valid():
    """The committed pipeline/configs/stage-registry.yml must load without error."""
    stage_yml = Path("pipeline/configs/stage-registry.yml")
    if not stage_yml.exists():
        pytest.skip("stage-registry.yml not yet committed")
    stages = _load_stage_registry(stage_yml)
    assert stages is not None
    assert len(stages) > 0
    for s in stages:
        assert "name" in s
        assert "order" in s


def test_fallback_does_not_crash_on_invalid_yaml(tmp_path):
    """Loading an invalid stage-registry.yml must never crash the caller."""
    stage_yml = tmp_path / "stage-registry.yml"
    stage_yml.write_text(": : : invalid YAML :::", encoding="utf-8")

    # Caller pattern: load or fall back
    stages = _load_stage_registry(stage_yml)
    hardcoded_fallback = ["load_config", "nuget_resolve", "generation"]  # minimal stand-in
    effective_stages = stages if stages else hardcoded_fallback
    assert effective_stages == hardcoded_fallback
