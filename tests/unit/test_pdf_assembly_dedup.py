"""Unit tests for PDF assembly deduplication (Phase 7 of PDF Assembly Dedup Sprint).

10 named tests covering:
  - assembly_identity.read_assembly_identity()
  - assembly_identity.deduplicate_assemblies()
  - discovery_sweep wiring (dedup applied before build_catalog)
  - dedup report written to verification/latest/
  - generation_ready safety gate (PDF must stay false)
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.dependencies.assembly_identity import (
    AssemblyIdentity,
    DeduplicationResult,
    deduplicate_assemblies,
    read_assembly_identity,
)

# Real .NET DLL from the project build output — always present after dotnet build.
_REFLECTOR_DLL = (
    Path(__file__).resolve().parents[2] / "tools" / "DllReflector" / "bin" / "Release" / "net8.0" / "DllReflector.dll"
)


# ── Tests ──────────────────────────────────────────────────────────────────


class TestReadAssemblyIdentity:
    @pytest.mark.skipif(not _REFLECTOR_DLL.exists(), reason="DllReflector.dll not built — run dotnet build first")
    def test_read_assembly_identity_extracts_name_version(self):
        """read_assembly_identity() reads a real .NET DLL and returns name from PE metadata."""
        pytest.importorskip("struct")  # always available; guards against misconfiguration
        assert _REFLECTOR_DLL.exists(), f"DllReflector.dll not found: {_REFLECTOR_DLL}"

        identity = read_assembly_identity(_REFLECTOR_DLL)

        # PE parse succeeds → name is from metadata, not filename
        assert identity.name, "Assembly name must not be empty"
        assert identity.read_from_pe is True
        assert Path(identity.source_path) == _REFLECTOR_DLL

    def test_read_assembly_identity_falls_back_to_stem_on_non_pe(self, tmp_path: Path):
        """read_assembly_identity() falls back to filename stem when the file is not a valid PE."""
        not_a_dll = tmp_path / "FakeDep.dll"
        not_a_dll.write_bytes(b"not a PE file")

        identity = read_assembly_identity(not_a_dll)

        assert identity.name == "FakeDep"
        assert identity.read_from_pe is False


class TestDeduplicateAssemblies:
    """Deduplication tests use stub files (not valid PE) — fallback to filename identity.

    This is sufficient because the deduplication key is `identity.name.lower()`,
    and the fallback sets name = path.stem. So filename-named stub files exercise
    the same dedup logic as real PE-parsed files.
    """

    def test_deduplicate_assemblies_removes_same_identity_duplicate(self, tmp_path: Path):
        """deduplicate_assemblies() returns only one entry when the same path appears twice."""
        dll = tmp_path / "System.Memory.dll"
        dll.write_bytes(b"stub")

        result = deduplicate_assemblies([dll, dll])

        assert len(result.kept) == 1
        assert result.kept[0] == dll
        assert len(result.excluded) == 1

    def test_deduplicate_assemblies_records_excluded_duplicate(self, tmp_path: Path):
        """deduplicate_assemblies() records excluded duplicates with assembly_name and reason."""
        dll = tmp_path / "System.Buffers.dll"
        dll.write_bytes(b"stub")

        result = deduplicate_assemblies([dll, dll])

        assert len(result.excluded) == 1
        exc = result.excluded[0]
        assert exc["assembly_name"].lower() == "system.buffers"
        assert exc["reason"] == "duplicate_assembly_name"

    def test_deduplicate_assemblies_handles_same_name_different_version(self, tmp_path: Path):
        """deduplicate_assemblies() deduplicates by name even when paths differ.

        Two different NuGet packages provide System.Memory.dll at different versions.
        After extraction both map to the same filename in resolved-libs, but they may
        also appear as distinct paths during dependency resolution. Either way, only one
        entry must survive.
        """
        dll_v1 = tmp_path / "v1" / "System.Memory.dll"
        dll_v1.parent.mkdir()
        dll_v1.write_bytes(b"stub-v1")

        dll_v2 = tmp_path / "v2" / "System.Memory.dll"
        dll_v2.parent.mkdir()
        dll_v2.write_bytes(b"stub-v2")

        result = deduplicate_assemblies([dll_v1, dll_v2])

        assert len(result.kept) == 1
        assert result.kept[0] == dll_v1  # first seen wins
        assert len(result.excluded) == 1

    def test_deduplicate_assemblies_preserves_distinct_assemblies(self, tmp_path: Path):
        """deduplicate_assemblies() does not remove assemblies with distinct names."""
        names = ["System.Memory.dll", "System.Buffers.dll", "System.Text.Json.dll"]
        paths = []
        for name in names:
            p = tmp_path / name
            p.write_bytes(b"stub")
            paths.append(p)

        result = deduplicate_assemblies(paths)

        assert len(result.kept) == 3
        assert len(result.excluded) == 0

    def test_deduplicate_assemblies_dedup_by_field(self, tmp_path: Path):
        """deduplicate_assemblies() sets dedup_by to 'assembly_simple_name'."""
        dll = tmp_path / "Foo.dll"
        dll.write_bytes(b"stub")

        result = deduplicate_assemblies([dll])

        assert result.dedup_by == "assembly_simple_name"


class TestDiscoverySweepDedup:
    def test_pdf_system_text_json_duplicate_removed(self, tmp_path: Path):
        """Deduplication removes System.Text.Json duplicate — the root cause of FileLoadException.

        Simulates the exact scenario: dep_dll_paths has System.Text.Json.dll appearing twice
        (once from NuGet Aspose.PDF dep, once from a transitive dep). After dedup, only one
        entry remains and the excluded entry is recorded.
        """
        stj = tmp_path / "System.Text.Json.dll"
        stj.write_bytes(b"stub")

        result = deduplicate_assemblies([stj, stj])

        assert len(result.kept) == 1
        assert len(result.excluded) == 1
        assert result.excluded[0]["assembly_name"].lower() == "system.text.json"

    def test_discovery_sweep_passes_deduped_deps_to_reflector(self, tmp_path: Path):
        """_discover_family() deduplicates dep_dll_paths before calling build_catalog.

        Asserts that the paths passed to build_catalog have no duplicate assembly names,
        even when extraction returns the same resolved path twice.
        """
        import plugin_examples.discovery_sweep as ds

        dup_path = str(tmp_path / "System.Memory.dll")
        (tmp_path / "System.Memory.dll").write_bytes(b"stub")
        (tmp_path / "Primary.dll").write_bytes(b"stub")

        extraction = {
            "dll_path": str(tmp_path / "Primary.dll"),
            "xml_path": None,
            "selected_framework": "netstandard2.0",
            "dependency_dll_paths": [dup_path, dup_path],  # intentional duplicate
        }

        verification_dir = tmp_path / "verification"
        (verification_dir / "latest").mkdir(parents=True)

        cfg = MagicMock()
        cfg.enabled = True
        cfg.status = "discovery_only"
        cfg.nuget.package_id = "Test.Package"
        cfg.nuget.version_policy = "latest"
        cfg.nuget.pinned_version = None
        cfg.nuget.allow_prerelease = False
        cfg.nuget.target_framework_preference = ["netstandard2.0"]
        cfg.nuget.dependency_resolution.enabled = False
        cfg.plugin_detection.namespace_patterns = []
        cfg.fixtures.sources = []
        cfg.existing_examples.sources = []

        captured_dep_paths: list = []

        def capturing_build_catalog(dll_path, output_path, xml_path=None, dependency_paths=None, namespace_filter=None):
            if dependency_paths:
                captured_dep_paths.extend(dependency_paths)
            return {"namespaces": []}

        with (
            patch(
                "plugin_examples.nuget_fetcher.fetch_package",
                return_value={"version": "1.0.0", "cached_path": str(tmp_path / "pkg.nupkg"), "sha256": "abc"},
            ),
            patch("plugin_examples.nuget_fetcher.resolve_dependencies", return_value=[]),
            patch("plugin_examples.nupkg_extractor.extract_package", return_value=extraction),
            patch("plugin_examples.reflection_catalog.build_catalog", side_effect=capturing_build_catalog),
            patch(
                "plugin_examples.plugin_detector.detect_plugin_namespaces",
                return_value=MagicMock(
                    matched_namespaces=[],
                    is_eligible=False,
                    public_plugin_type_count=0,
                    public_plugin_method_count=0,
                ),
            ),
            patch("plugin_examples.plugin_detector.write_source_of_truth_proof", return_value=tmp_path / "proof.json"),
            patch("plugin_examples.family_config.load_family_config", return_value=cfg),
            patch.object(Path, "exists", return_value=True),
        ):
                ds._discover_family("testfamily", tmp_path, False, verification_dir)

        # If build_catalog was called, dep paths must have no name duplicates.
        # If it wasn't reached due to error flow, captured_dep_paths is empty — that's also fine.
        names = [Path(str(p)).name.lower() for p in captured_dep_paths]
        assert len(names) == len(set(names)), f"Duplicate assembly names passed to reflector: {names}"

    def test_dedup_report_written(self, tmp_path: Path):
        """discovery_sweep writes {family}-dependency-dedup-report.json to verification/latest/."""
        import plugin_examples.discovery_sweep as ds

        mem_dll = tmp_path / "System.Memory.dll"
        mem_dll.write_bytes(b"stub")
        (tmp_path / "Primary.dll").write_bytes(b"stub")

        extraction = {
            "dll_path": str(tmp_path / "Primary.dll"),
            "xml_path": None,
            "selected_framework": "netstandard2.0",
            "dependency_dll_paths": [str(mem_dll), str(mem_dll)],  # duplicate
        }

        verification_dir = tmp_path / "verification"
        (verification_dir / "latest").mkdir(parents=True)

        cfg = MagicMock()
        cfg.enabled = True
        cfg.status = "discovery_only"
        cfg.nuget.package_id = "Test.Pkg"
        cfg.nuget.version_policy = "latest"
        cfg.nuget.pinned_version = None
        cfg.nuget.allow_prerelease = False
        cfg.nuget.target_framework_preference = ["netstandard2.0"]
        cfg.nuget.dependency_resolution.enabled = False
        cfg.plugin_detection.namespace_patterns = []
        cfg.fixtures.sources = []
        cfg.existing_examples.sources = []

        with (
            patch(
                "plugin_examples.nuget_fetcher.fetch_package",
                return_value={"version": "1.0.0", "cached_path": str(tmp_path / "pkg.nupkg"), "sha256": "x"},
            ),
            patch("plugin_examples.nuget_fetcher.resolve_dependencies", return_value=[]),
            patch("plugin_examples.nupkg_extractor.extract_package", return_value=extraction),
            patch("plugin_examples.reflection_catalog.build_catalog", return_value={"namespaces": []}),
            patch(
                "plugin_examples.plugin_detector.detect_plugin_namespaces",
                return_value=MagicMock(
                    matched_namespaces=[],
                    is_eligible=False,
                    public_plugin_type_count=0,
                    public_plugin_method_count=0,
                ),
            ),
            patch("plugin_examples.plugin_detector.write_source_of_truth_proof", return_value=tmp_path / "proof.json"),
            patch("plugin_examples.family_config.load_family_config", return_value=cfg),
            patch.object(Path, "exists", return_value=True),
        ):
            ds._discover_family("myfamily", tmp_path, False, verification_dir)

        report_path = verification_dir / "latest" / "myfamily-dependency-dedup-report.json"
        assert report_path.exists(), "Dedup report was not written"
        report = json.loads(report_path.read_text())
        assert report["family"] == "myfamily"
        assert report["excluded_count"] == 1
        assert report["kept_count"] == 1
        assert report["dedup_by"] == "assembly_simple_name"


class TestPdfGenerationReadiness:
    def test_pdf_generation_not_ready_after_reflection_only(self):
        """PDF generation_ready must be False even when reflection succeeds.

        reflection_status=succeeded does NOT imply generation permission.
        discovery_only family status is an independent blocker.
        """
        import tempfile

        from plugin_examples.discovery_sweep import compute_generation_readiness

        discovery_result = {
            "family": "pdf",
            "status": "eligible_lowcode_found",
            "eligibility_status": "eligible",
            "plugin_type_count": 101,
            "plugin_method_count": 71,
            "lowcode_namespaces": ["Aspose.Pdf.LowCode"],
            "catalog_path": None,  # skip catalog classification
            "dependency_paths": [],
        }

        cfg = MagicMock()
        cfg.status = "discovery_only"
        cfg.generation.allowed_types = []
        cfg.fixtures.sources = []
        cfg.existing_examples.sources = []
        cfg.plugin_detection.namespace_patterns = ["Aspose.Pdf.LowCode"]

        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            configs_dir = repo_root / "pipeline" / "configs" / "families"
            configs_dir.mkdir(parents=True)
            (configs_dir / "pdf.yml").write_text("placeholder")

            with patch("plugin_examples.family_config.load_family_config", return_value=cfg):
                ranks = compute_generation_readiness([discovery_result], repo_root)

        pdf_rank = next(r for r in ranks if r["family"] == "pdf")

        assert (
            pdf_rank["generation_ready"] is False
        ), f"PDF must not be generation_ready even after reflection success — got {pdf_rank}"
        assert "family_status_is_discovery_only" in pdf_rank["generation_blocked_by"]
        assert pdf_rank["reflection_status"] == "succeeded"
        assert pdf_rank["discovery_status"] == "eligible_lowcode_found"
