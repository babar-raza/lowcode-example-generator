"""Unit tests for the family_config module."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path

import pytest
import yaml

from plugin_examples.family_config import (
    DisabledFamilyError,
    FamilyConfig,
    TemplateHints,
    load_family_config,
)
from plugin_examples.family_config.validator import validate_family_config

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parents[2]
CELLS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "cells.yml"
WORDS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "disabled" / "words.yml"


def _load_raw(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _write_temp_config(data: dict, *, subdir: str = "") -> Path:
    """Write a config dict to a temp YAML file and return its path."""
    tmpdir = tempfile.mkdtemp()
    if subdir:
        target = Path(tmpdir) / subdir
        target.mkdir(parents=True, exist_ok=True)
    else:
        target = Path(tmpdir)
    path = target / "test-config.yml"
    with open(path, "w") as f:
        yaml.dump(data, f)
    return path


# --- Happy path tests ---


class TestCellsConfigLoads:
    def test_loads_successfully(self):
        config = load_family_config(CELLS_CONFIG)
        assert isinstance(config, FamilyConfig)

    def test_family_is_cells(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.family == "cells"

    def test_enabled_is_true(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.enabled is True

    def test_status_is_active(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.status == "active"

    def test_nuget_package_id(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.nuget.package_id == "Aspose.Cells"

    def test_namespace_patterns_present(self):
        config = load_family_config(CELLS_CONFIG)
        assert len(config.plugin_detection.namespace_patterns) >= 1

    def test_provider_order(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.llm.provider_order == ["gpt_oss", "openai", "llm_professionalize", "ollama"]


# --- Schema validation failure tests ---


class TestSchemaValidationFailures:
    def test_missing_namespace_patterns_fails(self):
        data = _load_raw(CELLS_CONFIG)
        del data["plugin_detection"]["namespace_patterns"]
        with pytest.raises(Exception):
            validate_family_config(data)

    def test_missing_package_id_fails(self):
        data = _load_raw(CELLS_CONFIG)
        del data["nuget"]["package_id"]
        with pytest.raises(Exception):
            validate_family_config(data)

    def test_invalid_version_policy_fails(self):
        data = _load_raw(CELLS_CONFIG)
        data["nuget"]["version_policy"] = "invalid"
        with pytest.raises(Exception):
            validate_family_config(data)

    def test_missing_enabled_fails(self):
        data = _load_raw(CELLS_CONFIG)
        del data["enabled"]
        with pytest.raises(Exception):
            validate_family_config(data)

    def test_missing_status_fails(self):
        data = _load_raw(CELLS_CONFIG)
        del data["status"]
        with pytest.raises(Exception):
            validate_family_config(data)


# --- Disabled config tests ---


class TestDisabledConfigs:
    def test_disabled_path_raises(self):
        """A config under a disabled/ directory is rejected."""
        data = _load_raw(CELLS_CONFIG)
        path = _write_temp_config(data, subdir="disabled")
        with pytest.raises(DisabledFamilyError):
            load_family_config(path)

    def test_enabled_false_raises(self):
        data = _load_raw(CELLS_CONFIG)
        data["enabled"] = False
        path = _write_temp_config(data)
        with pytest.raises(DisabledFamilyError):
            load_family_config(path)

    def test_status_disabled_raises(self):
        data = _load_raw(CELLS_CONFIG)
        data["status"] = "disabled"
        path = _write_temp_config(data)
        with pytest.raises(DisabledFamilyError):
            load_family_config(path)

    def test_disabled_path_rejected_even_if_enabled_true(self):
        """A config under a disabled/ directory is rejected even if enabled=true."""
        data = _load_raw(CELLS_CONFIG)
        data["enabled"] = True
        data["status"] = "active"
        path = _write_temp_config(data, subdir="disabled")
        with pytest.raises(DisabledFamilyError):
            load_family_config(path)


# --- Template hints tests ---


class TestTemplateHints:
    def test_cells_has_template_hints(self):
        config = load_family_config(CELLS_CONFIG)
        assert hasattr(config, "template_hints")
        assert isinstance(config.template_hints, TemplateHints)

    def test_cells_hints_values(self):
        config = load_family_config(CELLS_CONFIG)
        h = config.template_hints
        assert h.default_input_extension == ".xlsx"
        assert h.default_input_filename == "input.xlsx"
        assert h.default_output_extension == ".xlsx"
        assert h.default_fixture_extension == ".xlsx"
        assert "Aspose.Cells" in h.additional_usings
        assert len(h.input_creation_lines) > 0

    def test_words_has_template_hints(self):
        # Words config is in disabled/ dir, so load raw + validate + build directly
        data = _load_raw(WORDS_CONFIG)
        validate_family_config(data)
        from plugin_examples.family_config.loader import _build_model
        config = _build_model(data)
        h = config.template_hints
        assert h.default_input_extension == ".docx"
        assert h.default_input_filename == "input.docx"
        assert "Aspose.Words" in h.additional_usings

    def test_defaults_when_absent(self):
        """Config without template_hints uses defaults."""
        data = _load_raw(CELLS_CONFIG)
        data.pop("template_hints", None)
        path = _write_temp_config(data)
        config = load_family_config(path)
        assert config.template_hints.default_input_extension == ".xlsx"
        assert config.template_hints.default_output_extension == ".out"
        assert config.template_hints.additional_usings == []

    def test_additional_usings_preserved(self):
        config = load_family_config(CELLS_CONFIG)
        assert config.template_hints.additional_usings == ["Aspose.Cells"]

    def test_input_creation_lines_preserved(self):
        config = load_family_config(CELLS_CONFIG)
        lines = config.template_hints.input_creation_lines
        assert any("Workbook" in line for line in lines)
        assert any("Save" in line for line in lines)
