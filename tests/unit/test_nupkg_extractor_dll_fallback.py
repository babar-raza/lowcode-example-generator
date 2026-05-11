"""Unit tests for nupkg extractor DLL name fallback.

Covers the .NET suffix fallback introduced for Aspose.Slides.NET:
  - Package ID 'Aspose.Slides.NET' ships 'Aspose.Slides.dll' (not 'Aspose.Slides.NET.dll')
  - Extractor must fall back to the shorter assembly name when the exact match is absent
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from plugin_examples.nupkg_extractor.extractor import ExtractionError, extract_package


def _make_fake_nupkg(
    tmp_path: Path,
    package_id: str,
    dll_stem: str,
    framework: str = "netstandard2.0",
) -> Path:
    """Create a minimal .nupkg with a single DLL under lib/{framework}/."""
    nupkg = tmp_path / f"{package_id}.nupkg"
    dll_bytes = b"\x4d\x5a" + b"\x00" * 100  # minimal MZ header stub (not valid PE)
    with zipfile.ZipFile(nupkg, "w") as zf:
        zf.writestr(f"lib/{framework}/{dll_stem}.dll", dll_bytes)
        # Minimal .nuspec to satisfy any nuspec checks
        zf.writestr(
            f"{package_id}.nuspec",
            f'<?xml version="1.0"?><package><metadata>'
            f"<id>{package_id}</id><version>1.0.0</version>"
            f"<description>test</description>"
            f"</metadata></package>",
        )
    return nupkg


class TestDllNameFallback:
    """Tests for the .NET suffix DLL name fallback in extract_package."""

    def test_exact_dll_name_found_directly(self, tmp_path: Path):
        """When package_id.dll exists, it is found without needing the fallback."""
        nupkg = _make_fake_nupkg(
            tmp_path,
            package_id="Aspose.Cells",
            dll_stem="Aspose.Cells",
        )
        result = extract_package(
            nupkg,
            package_id="Aspose.Cells",
            family="cells",
            target_framework_preference=["netstandard2.0"],
            run_dir=tmp_path / "run",
        )
        assert Path(result["dll_path"]).name == "Aspose.Cells.dll"

    def test_net_suffix_fallback_used_when_exact_not_found(self, tmp_path: Path):
        """When Aspose.Slides.NET.dll is absent but Aspose.Slides.dll exists, fallback succeeds."""
        nupkg = _make_fake_nupkg(
            tmp_path,
            package_id="Aspose.Slides.NET",
            dll_stem="Aspose.Slides",  # actual DLL name (without .NET)
        )
        result = extract_package(
            nupkg,
            package_id="Aspose.Slides.NET",
            family="slides",
            target_framework_preference=["netstandard2.0"],
            run_dir=tmp_path / "run",
        )
        assert Path(result["dll_path"]).name == "Aspose.Slides.dll"

    def test_net_suffix_fallback_not_triggered_without_net_suffix(self, tmp_path: Path):
        """When package_id does not end in .NET and exact DLL is absent, raises ExtractionError."""
        nupkg = _make_fake_nupkg(
            tmp_path,
            package_id="Aspose.Cells",
            dll_stem="WrongName",  # intentionally wrong
        )
        with pytest.raises(ExtractionError, match="DLL not found"):
            extract_package(
                nupkg,
                package_id="Aspose.Cells",
                family="cells",
                target_framework_preference=["netstandard2.0"],
                run_dir=tmp_path / "run2",
            )

    def test_net_suffix_fallback_raises_if_neither_name_found(self, tmp_path: Path):
        """If neither Aspose.Slides.NET.dll nor Aspose.Slides.dll exists, raises ExtractionError."""
        nupkg = _make_fake_nupkg(
            tmp_path,
            package_id="Aspose.Slides.NET",
            dll_stem="SomethingElse",  # neither name matches
        )
        with pytest.raises(ExtractionError, match="DLL not found"):
            extract_package(
                nupkg,
                package_id="Aspose.Slides.NET",
                family="slides",
                target_framework_preference=["netstandard2.0"],
                run_dir=tmp_path / "run3",
            )
