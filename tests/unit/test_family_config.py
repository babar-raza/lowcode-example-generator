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
WORDS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "words.yml"


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
        assert config.llm.provider_order == ["llm_professionalize", "ollama"]


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
        config = load_family_config(WORDS_CONFIG)
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


# --- Duplicate config cleanup tests ---


DISABLED_DIR = REPO_ROOT / "pipeline" / "configs" / "families" / "disabled"


class TestDuplicateConfigCleanup:
    """Verify stale disabled/ configs for words and pdf have been removed."""

    def test_disabled_words_config_does_not_exist(self):
        assert not (
            DISABLED_DIR / "words.yml"
        ).exists(), "disabled/words.yml must be deleted — it was superseded by the active words.yml"

    def test_disabled_pdf_config_does_not_exist(self):
        assert not (
            DISABLED_DIR / "pdf.yml"
        ).exists(), "disabled/pdf.yml must be deleted — it was superseded by the active pdf.yml"

    def test_active_words_config_loads_as_active(self):
        """Words was promoted from discovery_only to active for the controlled pilot."""
        config = load_family_config(WORDS_CONFIG)
        assert config.status == "active"

    def test_active_pdf_config_loads_as_active(self):
        pdf_config = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config)
        assert config.status == "active"


# --- Family-specific publishing target tests ---


class TestFamilyPublishingTarget:
    def test_cells_central_repo_allowed_defaults_false(self):
        """cells.yml must NOT set central_repo_allowed (defaults to False)."""
        config = load_family_config(CELLS_CONFIG)
        assert config.github.central_repo_allowed is False

    def test_words_central_repo_allowed_defaults_false(self):
        """words.yml must NOT set central_repo_allowed (defaults to False)."""
        config = load_family_config(WORDS_CONFIG)
        assert config.github.central_repo_allowed is False

    def test_central_repo_allowed_true_parsed_correctly(self):
        """When central_repo_allowed: true is set explicitly, loader parses it as True."""
        data = _load_raw(CELLS_CONFIG)
        data["github"]["central_repo_allowed"] = True
        path = _write_temp_config(data)
        config = load_family_config(path)
        assert config.github.central_repo_allowed is True

    def test_published_plugin_examples_repo_required(self):
        """Config without published_plugin_examples_repo must fail schema validation."""
        data = _load_raw(CELLS_CONFIG)
        del data["github"]["published_plugin_examples_repo"]
        with pytest.raises(Exception):
            validate_family_config(data)

    def test_github_repo_ref_has_owner_repo_branch(self):
        """published_plugin_examples_repo must expose owner, repo, branch fields."""
        config = load_family_config(CELLS_CONFIG)
        pub = config.github.published_plugin_examples_repo
        assert hasattr(pub, "owner") and pub.owner
        assert hasattr(pub, "repo") and pub.repo
        assert hasattr(pub, "branch") and pub.branch

    def test_cells_publish_target_is_family_specific(self):
        """cells.yml published_plugin_examples_repo must be family-specific (owner or repo contains 'cells')."""
        from plugin_examples.publisher.publisher import _is_central_repo

        config = load_family_config(CELLS_CONFIG)
        pub = config.github.published_plugin_examples_repo
        assert not _is_central_repo(
            pub.owner, pub.repo, "cells"
        ), f"Cells publish target {pub.owner}/{pub.repo} must be family-specific, not central"

    def test_words_publish_target_is_family_specific(self):
        """words.yml published_plugin_examples_repo must be family-specific (owner or repo contains 'words')."""
        from plugin_examples.publisher.publisher import _is_central_repo

        config = load_family_config(WORDS_CONFIG)
        pub = config.github.published_plugin_examples_repo
        assert not _is_central_repo(
            pub.owner, pub.repo, "words"
        ), f"Words publish target {pub.owner}/{pub.repo} must be family-specific, not central"

    def test_central_repo_not_used_for_cells_or_words(self):
        """Neither cells.yml nor words.yml may use aspose/aspose-plugins-examples-dotnet as publish target."""
        _CENTRAL = ("aspose", "aspose-plugins-examples-dotnet")
        for family, config_path in [("cells", CELLS_CONFIG), ("words", WORDS_CONFIG)]:
            config = load_family_config(config_path)
            pub = config.github.published_plugin_examples_repo
            assert (
                pub.owner,
                pub.repo,
            ) != _CENTRAL, f"{family} must not use central placeholder {_CENTRAL[0]}/{_CENTRAL[1]} as publish target"

    def test_pdf_config_is_active_for_controlled_pilot(self):
        """PDF must be active now that reflection dedup and publish target are resolved."""
        pdf_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config_path)
        assert config.status == "active", "PDF must be active after controlled-pilot enablement"

    def test_central_repo_allowed_defaults_false(self):
        """central_repo_allowed must default to False for all active families."""
        for config_path in [CELLS_CONFIG, WORDS_CONFIG]:
            config = load_family_config(config_path)
            assert (
                config.github.central_repo_allowed is False
            ), f"{config.family} central_repo_allowed must default to False"

    def test_pdf_publish_target_is_family_specific(self):
        """pdf.yml published_plugin_examples_repo must be family-specific (aspose-pdf-net), not central placeholder."""
        from plugin_examples.publisher.publisher import _is_central_repo

        pdf_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config_path)
        pub = config.github.published_plugin_examples_repo
        assert not _is_central_repo(
            pub.owner, pub.repo, "pdf"
        ), f"PDF publish target {pub.owner}/{pub.repo} must be family-specific, not central placeholder"

    def test_pdf_publish_target_owner_is_aspose_pdf_net(self):
        """pdf.yml published_plugin_examples_repo.owner must be aspose-pdf-net."""
        pdf_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config_path)
        pub = config.github.published_plugin_examples_repo
        assert pub.owner == "aspose-pdf-net", (
            f"Expected owner='aspose-pdf-net' but got '{pub.owner}'. "
            "pdf.yml published_plugin_examples_repo must follow the aspose-{{family}}-net pattern."
        )

    def test_pdf_publish_target_repo_follows_pattern(self):
        """pdf.yml published_plugin_examples_repo.repo must be Aspose.PDF.LowCode-for-.NET-Examples."""
        pdf_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config_path)
        pub = config.github.published_plugin_examples_repo
        assert (
            pub.repo == "Aspose.PDF.LowCode-for-.NET-Examples"
        ), f"Expected repo='Aspose.PDF.LowCode-for-.NET-Examples' but got '{pub.repo}'."

    def test_pdf_central_repo_not_used(self):
        """pdf.yml must not use aspose/aspose-plugins-examples-dotnet as publish target."""
        _CENTRAL = ("aspose", "aspose-plugins-examples-dotnet")
        pdf_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
        config = load_family_config(pdf_config_path)
        pub = config.github.published_plugin_examples_repo
        assert (
            pub.owner,
            pub.repo,
        ) != _CENTRAL, "pdf.yml must not use the central placeholder aspose/aspose-plugins-examples-dotnet"


class TestExtraPackagesConfig:
    """Tests for DependencyResolution.extra_packages field."""

    def test_extra_packages_defaults_to_empty(self):
        """extra_packages defaults to [] when not set."""
        cells_config = load_family_config(CELLS_CONFIG)
        assert cells_config.nuget.dependency_resolution.extra_packages == []

    def test_ocr_config_has_extra_packages(self):
        """ocr.yml declares Aspose.Drawing.Common as an extra_package."""
        ocr_config_path = REPO_ROOT / "pipeline" / "configs" / "families" / "ocr.yml"
        config = load_family_config(ocr_config_path)
        extras = config.nuget.dependency_resolution.extra_packages
        assert "Aspose.Drawing.Common" in extras

    def test_extra_packages_loaded_from_yaml(self, tmp_path):
        """extra_packages list is parsed correctly from YAML."""
        raw = _load_raw(CELLS_CONFIG)
        raw["nuget"]["dependency_resolution"] = {
            "enabled": True,
            "max_depth": 2,
            "extra_packages": ["Pkg.A", "Pkg.B"],
        }
        path = _write_temp_config(raw)
        config = load_family_config(path)
        assert config.nuget.dependency_resolution.extra_packages == ["Pkg.A", "Pkg.B"]

    def test_extra_packages_schema_valid(self, tmp_path):
        """Schema allows extra_packages as an array of strings."""
        raw = _load_raw(CELLS_CONFIG)
        raw["nuget"]["dependency_resolution"] = {
            "enabled": True,
            "max_depth": 2,
            "extra_packages": ["Some.Package"],
        }
        # Should not raise
        validate_family_config(raw)

    def test_extra_packages_not_required_in_schema(self, tmp_path):
        """Schema does not require extra_packages — it is optional."""
        raw = _load_raw(CELLS_CONFIG)
        raw["nuget"]["dependency_resolution"] = {"enabled": True, "max_depth": 2}
        # Should not raise
        validate_family_config(raw)


class TestPerTypeConstraints:
    """per_type_constraints is loaded from YAML into FamilyConfig."""

    REPO_ROOT = Path(__file__).resolve().parents[2]
    PDF_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "pdf.yml"
    WORDS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "words.yml"
    CELLS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "cells.yml"
    DIAGRAM_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "diagram.yml"

    def test_pdf_config_has_per_type_constraints(self):
        config = load_family_config(self.PDF_CONFIG)
        assert isinstance(config.per_type_constraints, dict)
        assert "Merger" in config.per_type_constraints

    def test_pdf_merger_required_includes_merge_options(self):
        """Merger must carry the MergeOptions LowCode API requirement (Aspose.Pdf.Text
        using directive was removed as over-strict fixture dependency — sprint56)."""
        config = load_family_config(self.PDF_CONFIG)
        merger = config.per_type_constraints["Merger"]
        required = merger.get("required", [])
        assert any(
            "MergeOptions" in r for r in required
        ), "Merger per_type_constraints must include REQUIRED: new MergeOptions("
        assert any(
            "Merger().Process" in r for r in required
        ), "Merger per_type_constraints must include REQUIRED: new Merger().Process(options)"

    def test_pdf_merger_forbidden_includes_pdffileeditor(self):
        config = load_family_config(self.PDF_CONFIG)
        merger = config.per_type_constraints["Merger"]
        forbidden = merger.get("forbidden", [])
        assert any("PdfFileEditor" in f for f in forbidden)

    def test_words_config_has_per_type_constraints(self):
        config = load_family_config(self.WORDS_CONFIG)
        assert isinstance(config.per_type_constraints, dict)
        assert "Converter" in config.per_type_constraints

    def test_words_converter_forbidden_document_save(self):
        config = load_family_config(self.WORDS_CONFIG)
        converter = config.per_type_constraints["Converter"]
        forbidden = converter.get("forbidden", [])
        assert any("Document.Save" in f for f in forbidden)

    def test_cells_config_has_per_type_constraints(self):
        config = load_family_config(self.CELLS_CONFIG)
        assert isinstance(config.per_type_constraints, dict)

    def test_diagram_config_has_per_type_constraints(self):
        config = load_family_config(self.DIAGRAM_CONFIG)
        assert isinstance(config.per_type_constraints, dict)
        assert "DiagramConverter" in config.per_type_constraints

    def test_config_without_per_type_constraints_defaults_empty(self, tmp_path):
        """Configs without per_type_constraints field load fine with empty dict."""
        raw = _load_raw(CELLS_CONFIG)
        raw.pop("per_type_constraints", None)
        path = _write_temp_config(raw)
        config = load_family_config(path)
        assert config.per_type_constraints == {}

    def test_pdf_toc_generator_in_per_type_constraints(self):
        """Sprint 16: TocGenerator must have per_type_constraints defined in pdf.yml."""
        config = load_family_config(self.PDF_CONFIG)
        assert (
            "TocGenerator" in config.per_type_constraints
        ), "TocGenerator must have per_type_constraints in pdf.yml (Sprint 16 next-wave)"
        toc = config.per_type_constraints["TocGenerator"]
        required = toc.get("required", [])
        assert any("TocOptions" in r for r in required), "TocGenerator constraints must require TocOptions"
        assert any("TocGenerator" in r for r in required), "TocGenerator constraints must require TocGenerator.Process"

    def test_pdf_toc_generator_forbidden_plugin_options(self):
        """TocGenerator constraints must forbid abstract PluginOptions."""
        config = load_family_config(self.PDF_CONFIG)
        toc = config.per_type_constraints["TocGenerator"]
        forbidden = toc.get("forbidden", [])
        assert any("PluginOptions" in f for f in forbidden)

    def test_pdf_image_extractor_in_per_type_constraints(self):
        """Sprint 16: ImageExtractor must have per_type_constraints defined in pdf.yml."""
        config = load_family_config(self.PDF_CONFIG)
        assert (
            "ImageExtractor" in config.per_type_constraints
        ), "ImageExtractor must have per_type_constraints in pdf.yml (Sprint 16 next-wave)"
        ie = config.per_type_constraints["ImageExtractor"]
        required = ie.get("required", [])
        assert any("ImageExtractorOptions" in r for r in required), "ImageExtractor must require ImageExtractorOptions"
        assert any("ImageExtractor" in r for r in required), "ImageExtractor constraints must require .Process call"

    def test_pdf_image_extractor_forbidden_add_output(self):
        """ImageExtractor constraints must forbid AddOutput (extractor pattern, not converter)."""
        config = load_family_config(self.PDF_CONFIG)
        ie = config.per_type_constraints["ImageExtractor"]
        forbidden = ie.get("forbidden", [])
        assert any("AddOutput" in f for f in forbidden), "ImageExtractor is an extractor — AddOutput must be forbidden"

    def test_pdf_allowed_types_includes_toc_and_image_extractor(self):
        """Sprint 16: TocGenerator and ImageExtractor must appear in allowed_types."""
        config = load_family_config(self.PDF_CONFIG)
        allowed = config.generation.allowed_types or []
        assert "TocGenerator" in allowed, "TocGenerator must be in pdf.yml allowed_types"
        assert "ImageExtractor" in allowed, "ImageExtractor must be in pdf.yml allowed_types"
