"""Unit tests for nupkg_extractor: framework_selector and extractor."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

from plugin_examples.nupkg_extractor.extractor import (
    ExtractionError,
    extract_package,
)
from plugin_examples.nupkg_extractor.framework_selector import (
    FrameworkSelection,
    select_framework,
)


# --- Helpers ---


def _make_nupkg(
    tmp_path: Path,
    package_id: str,
    frameworks: dict[str, list[str]],
    name: str | None = None,
) -> Path:
    """Create a fake .nupkg with lib/{tfm}/{files}.

    Args:
        frameworks: mapping of TFM → list of filenames to include.
    """
    nupkg_path = tmp_path / (name or f"{package_id}.1.0.0.nupkg")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for tfm, files in frameworks.items():
            for fname in files:
                zf.writestr(f"lib/{tfm}/{fname}", b"fake dll content")
        # Add a minimal .nuspec
        zf.writestr(
            f"{package_id}.nuspec",
            f'<package><metadata><id>{package_id}</id></metadata></package>',
        )
    nupkg_path.write_bytes(buf.getvalue())
    return nupkg_path


# --- Tests: framework_selector ---


class TestFrameworkSelector:
    def test_selects_first_preference(self):
        result = select_framework(
            ["net8.0", "netstandard2.0", "net48"],
            ["netstandard2.0", "netstandard2.1", "net8.0", "net6.0", "net48"],
        )
        assert result.selected_framework == "netstandard2.0"

    def test_netstandard20_over_net80(self):
        result = select_framework(
            ["net8.0", "netstandard2.0"],
            ["netstandard2.0", "net8.0"],
        )
        assert result.selected_framework == "netstandard2.0"

    def test_falls_through_to_second_preference(self):
        result = select_framework(
            ["net8.0", "net6.0"],
            ["netstandard2.0", "net8.0", "net6.0"],
        )
        assert result.selected_framework == "net8.0"

    def test_net48_requires_windows(self):
        result = select_framework(
            ["net48"],
            ["netstandard2.0", "net48"],
        )
        assert result.selected_framework == "net48"
        assert result.requires_windows_runner is True

    def test_net45_requires_windows(self):
        result = select_framework(
            ["net45"],
            ["net45"],
        )
        assert result.requires_windows_runner is True

    def test_netstandard_does_not_require_windows(self):
        result = select_framework(
            ["netstandard2.0"],
            ["netstandard2.0"],
        )
        assert result.requires_windows_runner is False

    def test_net80_does_not_require_windows(self):
        result = select_framework(
            ["net8.0"],
            ["net8.0"],
        )
        assert result.requires_windows_runner is False

    def test_no_match_raises(self):
        with pytest.raises(ValueError, match="No supported framework found"):
            select_framework(["net9.0"], ["netstandard2.0", "net8.0"])

    def test_empty_available_raises(self):
        with pytest.raises(ValueError, match="No frameworks available"):
            select_framework([], ["netstandard2.0"])

    def test_case_insensitive(self):
        result = select_framework(
            ["NetStandard2.0"],
            ["netstandard2.0"],
        )
        assert result.selected_framework == "NetStandard2.0"

    def test_selection_reason_recorded(self):
        result = select_framework(
            ["net8.0", "netstandard2.0"],
            ["netstandard2.0", "net8.0"],
        )
        assert "preference #1" in result.selection_reason


# --- Tests: extract_package ---


class TestExtractPackage:
    def test_dll_path_recorded(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll", "TestPkg.xml"],
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        assert result["dll_path"] is not None
        assert Path(result["dll_path"]).name == "TestPkg.dll"

    def test_xml_path_recorded(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll", "TestPkg.xml"],
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        assert result["xml_path"] is not None
        assert Path(result["xml_path"]).name == "TestPkg.xml"

    def test_warnings_on_missing_xml(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll"],  # No XML
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        assert result["xml_path"] is None
        assert result["xml_warning"] is not None

        warnings_path = run_dir / "extracted" / "test" / "warnings.json"
        assert warnings_path.exists()
        with open(warnings_path) as f:
            warnings = json.load(f)
        assert len(warnings) == 1
        assert warnings[0]["type"] == "missing_xml_documentation"

    def test_missing_dll_raises(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["SomeOther.dll"],  # Wrong DLL name
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        with pytest.raises(ExtractionError, match="DLL not found"):
            extract_package(
                nupkg,
                package_id="TestPkg",
                family="test",
                target_framework_preference=["netstandard2.0"],
                run_dir=run_dir,
            )

    def test_extraction_manifest_fields(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll", "TestPkg.xml"],
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        required_fields = [
            "package_id",
            "family",
            "selected_framework",
            "framework_selection_reason",
            "requires_windows_runner",
            "dll_path",
            "xml_path",
            "xml_warning",
            "dependency_dll_paths",
            "extracted_primary_path",
            "extracted_dependency_paths",
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Verify manifest file written
        manifest_path = run_dir / "extracted" / "test" / "extraction-manifest.json"
        assert manifest_path.exists()
        with open(manifest_path) as f:
            written = json.load(f)
        for field in required_fields:
            assert field in written

    def test_requires_windows_runner_in_manifest(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "net48": ["TestPkg.dll"],
        })
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["net48"],
            run_dir=run_dir,
        )

        assert result["requires_windows_runner"] is True


# --- Tests: dependency extraction ---


class TestDependencyExtraction:
    def test_dependency_dlls_extracted(self, tmp_path):
        primary = _make_nupkg(tmp_path, "Primary", {
            "netstandard2.0": ["Primary.dll"],
        })
        dep = _make_nupkg(
            tmp_path,
            "Dep.One",
            {"netstandard2.0": ["Dep.One.dll"]},
            name="Dep.One.2.0.0.nupkg",
        )

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            primary,
            package_id="Primary",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
            dependency_nupkgs=[dep],
        )

        assert len(result["dependency_dll_paths"]) == 1
        dep_dll = Path(result["dependency_dll_paths"][0])
        assert dep_dll.name == "Dep.One.dll"

    def test_dependency_dlls_in_resolved_libs(self, tmp_path):
        primary = _make_nupkg(tmp_path, "Primary", {
            "netstandard2.0": ["Primary.dll"],
        })
        dep = _make_nupkg(
            tmp_path,
            "Dep.One",
            {"netstandard2.0": ["Dep.One.dll"]},
            name="Dep.One.2.0.0.nupkg",
        )

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        extract_package(
            primary,
            package_id="Primary",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
            dependency_nupkgs=[dep],
        )

        resolved_libs = run_dir / "extracted" / "test" / "resolved-libs"
        assert resolved_libs.exists()
        assert (resolved_libs / "Dep.One.dll").exists()

    def test_multiple_dependencies(self, tmp_path):
        primary = _make_nupkg(tmp_path, "Primary", {
            "netstandard2.0": ["Primary.dll"],
        })
        dep1 = _make_nupkg(
            tmp_path, "DepA", {"netstandard2.0": ["DepA.dll"]},
            name="DepA.1.0.0.nupkg",
        )
        dep2 = _make_nupkg(
            tmp_path, "DepB", {"netstandard2.0": ["DepB.dll"]},
            name="DepB.3.0.0.nupkg",
        )

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        result = extract_package(
            primary,
            package_id="Primary",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
            dependency_nupkgs=[dep1, dep2],
        )

        assert len(result["dependency_dll_paths"]) == 2


# --- Tests: path correctness ---


class TestPathCorrectness:
    def test_all_paths_under_run_dir(self, tmp_path):
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll"],
        })
        run_dir = tmp_path / "workspace" / "runs" / "test-run"
        run_dir.mkdir(parents=True)

        result = extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        assert "workspace" in result["dll_path"]
        assert "workspace" in result["extracted_primary_path"]

    def test_no_old_root_paths_created(self, tmp_path):
        """Verify no old root-level runs/ or extracted/ dirs created."""
        nupkg = _make_nupkg(tmp_path, "TestPkg", {
            "netstandard2.0": ["TestPkg.dll"],
        })
        run_dir = tmp_path / "workspace" / "runs" / "test-run"
        run_dir.mkdir(parents=True)

        extract_package(
            nupkg,
            package_id="TestPkg",
            family="test",
            target_framework_preference=["netstandard2.0"],
            run_dir=run_dir,
        )

        # No root-level runs/ or extracted/ should exist
        assert not (tmp_path / "runs").exists()
        assert not (tmp_path / "extracted").exists()
