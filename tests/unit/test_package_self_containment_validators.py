"""Unit tests for package self-containment validators PSC-01..08 — TC-PSC-001."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin_examples.fixture_factory.package_self_containment_validators import (
    PscViolation,
    psc_01_csproj_exists,
    psc_02_target_framework,
    psc_03_package_reference,
    psc_04_no_absolute_paths,
    psc_05_no_interactive_calls,
    psc_06_manifest_exists,
    psc_07_expected_output_exists,
    psc_08_readme_exists,
    validate_package,
)


def _make_valid_package(tmp_path: Path) -> Path:
    """Create a minimal valid package."""
    pkg = tmp_path / "my-example"
    pkg.mkdir()
    (pkg / "Example.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk">\n'
        '  <PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup>\n'
        '  <ItemGroup><PackageReference Include="Aspose.Cells" Version="24.1.0" /></ItemGroup>\n'
        '</Project>',
        encoding="utf-8",
    )
    (pkg / "Program.cs").write_text(
        'using Aspose.Cells;\nclass Program { static void Main() { } }',
        encoding="utf-8",
    )
    (pkg / "example.manifest.json").write_text('{"scenario_id": "test"}', encoding="utf-8")
    (pkg / "expected-output.json").write_text('{}', encoding="utf-8")
    (pkg / "README.md").write_text("# Example", encoding="utf-8")
    return pkg


class TestPsc01CsprojExists:
    def test_passes_when_present(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_01_csproj_exists(pkg) is None

    def test_fails_when_missing(self, tmp_path):
        pkg = tmp_path / "empty"
        pkg.mkdir()
        v = psc_01_csproj_exists(pkg)
        assert v is not None
        assert v.rule_id == "PSC-01"


class TestPsc02TargetFramework:
    def test_passes_net80(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_02_target_framework(pkg) is None

    def test_fails_net60(self, tmp_path):
        pkg = tmp_path / "old"
        pkg.mkdir()
        (pkg / "Example.csproj").write_text(
            '<Project><PropertyGroup><TargetFramework>net6.0</TargetFramework></PropertyGroup></Project>',
            encoding="utf-8",
        )
        v = psc_02_target_framework(pkg)
        assert v is not None
        assert "net6.0" in v.detail


class TestPsc03PackageReference:
    def test_passes_with_reference(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_03_package_reference(pkg) is None

    def test_fails_without_reference(self, tmp_path):
        pkg = tmp_path / "norefs"
        pkg.mkdir()
        (pkg / "Example.csproj").write_text(
            '<Project><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>',
            encoding="utf-8",
        )
        v = psc_03_package_reference(pkg)
        assert v is not None
        assert v.rule_id == "PSC-03"


class TestPsc04NoAbsolutePaths:
    def test_passes_with_relative_paths(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_04_no_absolute_paths(pkg) is None

    def test_fails_with_windows_path(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        (pkg / "Program.cs").write_text('var f = @"C:\\Users\\test\\file.txt";', encoding="utf-8")
        v = psc_04_no_absolute_paths(pkg)
        assert v is not None
        assert v.rule_id == "PSC-04"


class TestPsc05NoInteractiveCalls:
    def test_passes_without_readkey(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_05_no_interactive_calls(pkg) is None

    def test_fails_with_readkey(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        (pkg / "Program.cs").write_text('Console.ReadKey();', encoding="utf-8")
        v = psc_05_no_interactive_calls(pkg)
        assert v is not None
        assert "ReadKey" in v.detail


class TestPsc06ManifestExists:
    def test_passes(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_06_manifest_exists(pkg) is None

    def test_fails(self, tmp_path):
        pkg = tmp_path / "nomanifest"
        pkg.mkdir()
        v = psc_06_manifest_exists(pkg)
        assert v is not None


class TestPsc07ExpectedOutput:
    def test_passes_with_expected(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_07_expected_output_exists(pkg) is None

    def test_fails_without_either(self, tmp_path):
        pkg = tmp_path / "nooutput"
        pkg.mkdir()
        v = psc_07_expected_output_exists(pkg)
        assert v is not None


class TestPsc08ReadmeExists:
    def test_passes(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        assert psc_08_readme_exists(pkg) is None

    def test_fails(self, tmp_path):
        pkg = tmp_path / "noreadme"
        pkg.mkdir()
        v = psc_08_readme_exists(pkg)
        assert v is not None


class TestValidatePackage:
    def test_valid_package_has_no_violations(self, tmp_path):
        pkg = _make_valid_package(tmp_path)
        violations = validate_package(pkg)
        assert len(violations) == 0

    def test_empty_dir_has_all_violations(self, tmp_path):
        pkg = tmp_path / "empty"
        pkg.mkdir()
        violations = validate_package(pkg)
        assert len(violations) >= 4  # At minimum: csproj, manifest, output, readme
