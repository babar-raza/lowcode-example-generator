"""Unit tests for the example factory."""

import json
import tempfile
from pathlib import Path

import pytest

from src.plugin_examples.example_factory.generator import ExamplePackageGenerator
from src.plugin_examples.example_factory.templates import FamilyTemplateRegistry
from src.plugin_examples.plugin_code_registry.models import PluginEntry


@pytest.fixture
def template_registry():
    return FamilyTemplateRegistry()


@pytest.fixture
def entry():
    return PluginEntry(
        family="barcode",
        plugin_slug="test-barcode",
        registry_status="READY_FOR_TRANSFORMATION",
        canonical_url="https://products.aspose.net/barcode/1d-barcode-writer/",
        implementation_model="STATIC_CONVERTER_CLASS",
        classes_used=["BarcodeGenerator"],
        code_hashes=["abc123"],
        github_links=["https://github.com/example.cs"],
    )


def test_template_registry_has_all_expected_families(template_registry):
    families = template_registry.available_families()
    required = ["barcode", "imaging", "zip", "html", "tasks", "svg", "tex", "ocr", "psd", "cad"]
    for f in required:
        assert f in families, f"Missing template for family: {f}"


def test_template_registry_fixture_free_families(template_registry):
    ff = template_registry.fixture_free_families()
    assert "barcode" in ff
    assert "svg" in ff
    assert "html" in ff
    assert "tex" in ff


def test_template_map_has_required_fields(template_registry):
    tm = template_registry.template_map()
    for family, info in tm.items():
        assert "nuget_package" in info, f"{family} missing nuget_package"
        assert "implementation_model" in info, f"{family} missing implementation_model"
        assert "fixture_strategy" in info, f"{family} missing fixture_strategy"


def test_generator_scaffold_creates_required_files(entry, tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    program_cs = '// test\nusing System;\nConsole.WriteLine("test");\n'
    pkg_dir = gen.generate_scaffold(entry, program_cs)

    assert (pkg_dir / "Program.cs").exists()
    assert (pkg_dir / "barcode-test-barcode.csproj").exists()
    assert (pkg_dir / "README.md").exists()
    assert (pkg_dir / "source-provenance.json").exists()
    assert (pkg_dir / "output").is_dir()


def test_generator_provenance_has_canonical_url(entry, tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    program_cs = 'Console.WriteLine("hi");\n'
    pkg_dir = gen.generate_scaffold(entry, program_cs)

    provenance = json.loads((pkg_dir / "source-provenance.json").read_text())
    assert provenance["canonical_url"] == entry.canonical_url
    assert provenance["family"] == "barcode"
    assert provenance["plugin_slug"] == "test-barcode"


def test_generator_readme_has_run_instructions(entry, tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    pkg_dir = gen.generate_scaffold(entry, 'Console.WriteLine("hi");\n')
    readme = (pkg_dir / "README.md").read_text()
    assert "dotnet run" in readme
    assert "dotnet restore" in readme


def test_generator_csproj_has_correct_package(entry, tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    pkg_dir = gen.generate_scaffold(entry, 'Console.WriteLine("hi");\n')
    csproj = (pkg_dir / "barcode-test-barcode.csproj").read_text()
    assert "Aspose.BarCode" in csproj
    assert "net8.0" in csproj


def test_generator_raises_for_unknown_family(tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    unknown_entry = PluginEntry(
        family="unknownfamily",
        plugin_slug="test",
        registry_status="READY_FOR_TRANSFORMATION",
    )
    with pytest.raises(ValueError, match="No template for family"):
        gen.generate_scaffold(unknown_entry, "")


def test_generator_package_dir_structure(entry, tmp_path):
    gen = ExamplePackageGenerator(tmp_path)
    expected_dir = tmp_path / "barcode" / "test-barcode"
    pkg_dir = gen.generate_scaffold(entry, 'Console.WriteLine("hi");\n')
    assert pkg_dir == expected_dir
