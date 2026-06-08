"""Tests for probe_generator module — TC-IMPL-005."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.probe_generator.generator import (
    CandidateNotReflectedError,
    ProbeFiles,
    ProbeGenerator,
)
from plugin_examples.probe_generator.runner import ProbeResult, ProbeRunner
from plugin_examples.plugin_detector.heuristic_matcher import (
    CandidateMapping,
    MethodInfo,
    ReflectionCatalog,
    TypeInfo,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_catalog(
    type_name: str = "BarcodeGenerator",
    method_name: str = "Save",
    namespace: str = "Aspose.BarCode.Generation",
) -> ReflectionCatalog:
    return ReflectionCatalog(
        package_id="Aspose.BarCode",
        types=[
            TypeInfo(
                name=type_name,
                namespace=namespace,
                methods=[MethodInfo(name=method_name)],
                has_public_constructor=True,
            )
        ],
    )


def _make_candidate(
    type_name: str = "BarcodeGenerator",
    method_name: str = "Save",
    namespace: str = "Aspose.BarCode.Generation",
) -> CandidateMapping:
    return CandidateMapping(
        type_name=type_name,
        namespace=namespace,
        method_name=method_name,
        confidence_score=0.75,
        score_breakdown={},
        match_rationale="test",
    )


# ---------------------------------------------------------------------------
# ProbeGenerator tests
# ---------------------------------------------------------------------------


class TestProbeGeneratorValidation:
    def test_generator_raises_when_type_not_in_reflection(self, tmp_path):
        """CandidateNotReflectedError raised when type is absent from catalog (PR-01)."""
        catalog = _make_catalog(type_name="SomeOtherType")
        candidate = _make_candidate(type_name="NonExistentType")
        gen = ProbeGenerator()
        with pytest.raises(CandidateNotReflectedError, match="PR-01"):
            gen.validate_candidate(candidate, catalog)

    def test_generator_raises_when_method_not_in_reflection(self):
        """CandidateNotReflectedError raised when method is absent from type (PR-02)."""
        catalog = _make_catalog(type_name="BarcodeGenerator", method_name="Save")
        candidate = _make_candidate(type_name="BarcodeGenerator", method_name="NonExistentMethod")
        gen = ProbeGenerator()
        with pytest.raises(CandidateNotReflectedError, match="PR-02"):
            gen.validate_candidate(candidate, catalog)


class TestProbeGeneratorOutput:
    def test_generator_creates_cs_with_correct_namespace(self, tmp_path):
        """Generated Program.cs must contain the type's namespace."""
        catalog = _make_catalog(namespace="Aspose.BarCode.Generation")
        candidate = _make_candidate(namespace="Aspose.BarCode.Generation")
        gen = ProbeGenerator()
        files = gen.generate(candidate, catalog, "Aspose.BarCode", "25.1.0", tmp_path)
        assert "Aspose.BarCode.Generation" in files.cs_content

    def test_generator_creates_csproj_with_package_reference(self, tmp_path):
        """Generated .csproj must contain the NuGet package reference."""
        catalog = _make_catalog()
        candidate = _make_candidate()
        gen = ProbeGenerator()
        files = gen.generate(candidate, catalog, "Aspose.BarCode", "25.1.0", tmp_path)
        assert "Aspose.BarCode" in files.csproj_content
        assert "25.1.0" in files.csproj_content

    def test_generator_writes_files_to_output_dir(self, tmp_path):
        """ProbeFiles must contain valid paths that exist on disk."""
        catalog = _make_catalog()
        candidate = _make_candidate()
        gen = ProbeGenerator()
        files = gen.generate(candidate, catalog, "Aspose.BarCode", "25.1.0", tmp_path)
        assert files.cs_path.exists()
        assert files.csproj_path.exists()


# ---------------------------------------------------------------------------
# ProbeRunner tests (mocked subprocess)
# ---------------------------------------------------------------------------


def _mock_completed(exit_code: int, stdout: str = "", stderr: str = "") -> MagicMock:
    m = MagicMock(spec=subprocess.CompletedProcess)
    m.returncode = exit_code
    m.stdout = stdout
    m.stderr = stderr
    return m


class TestProbeRunnerTaxonomy:
    def test_probe_result_has_all_required_fields_including_taxonomy(self, tmp_path):
        """ProbeResult must expose all required fields (restore_ok, build_ok, run_ok,
        output_validated, output_size_bytes, log_path, exit_codes, failure_taxonomy)."""
        runner = ProbeRunner()
        # Simulate restore failure
        with patch("subprocess.run", return_value=_mock_completed(1, stderr="restore failed")):
            result = runner.run(tmp_path, tmp_path / "Probe.csproj")
        assert hasattr(result, "restore_ok")
        assert hasattr(result, "build_ok")
        assert hasattr(result, "run_ok")
        assert hasattr(result, "output_validated")
        assert hasattr(result, "output_size_bytes")
        assert hasattr(result, "log_path")
        assert hasattr(result, "exit_codes")
        assert hasattr(result, "failure_taxonomy")
        assert result.failure_taxonomy == "PROBE_FAILED_RESTORE"

    def test_runner_timeout_classified_as_probe_failed_timeout(self, tmp_path):
        """subprocess.TimeoutExpired during restore → PROBE_FAILED_TIMEOUT."""
        runner = ProbeRunner(timeout=1)
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="dotnet", timeout=1)):
            result = runner.run(tmp_path, tmp_path / "Probe.csproj")
        assert result.failure_taxonomy == "PROBE_FAILED_TIMEOUT"

    def test_runner_zero_output_with_license_keyword_classified_as_probe_failed_license(
        self, tmp_path
    ):
        """Zero-byte output + license keyword in run stderr → PROBE_FAILED_LICENSE."""
        # Simulate restore OK, build OK, run OK but output file is empty
        def fake_run(cmd, **kwargs):
            return _mock_completed(0, stdout="ok", stderr="trial license expired")

        runner = ProbeRunner()
        # The output file won't exist (zero bytes)
        with patch("subprocess.run", side_effect=fake_run):
            result = runner.run(tmp_path, tmp_path / "Probe.csproj")
        assert result.failure_taxonomy == "PROBE_FAILED_LICENSE"

    def test_runner_build_failure_classified_as_probe_failed_build(self, tmp_path):
        """dotnet build non-zero exit → PROBE_FAILED_BUILD."""
        call_count = {"n": 0}

        def fake_run(cmd, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _mock_completed(0, stdout="restore ok")
            return _mock_completed(1, stderr="build error CS1234")

        runner = ProbeRunner()
        with patch("subprocess.run", side_effect=fake_run):
            result = runner.run(tmp_path, tmp_path / "Probe.csproj")
        assert result.restore_ok is True
        assert result.build_ok is False
        assert result.failure_taxonomy == "PROBE_FAILED_BUILD"

    def test_runner_validates_output_file_existence(self, tmp_path):
        """ProbeResult.output_validated=True only when output file exists and has size > 0."""
        output_file = tmp_path / "probe-output.bin"
        output_file.write_bytes(b"FAKE_OUTPUT_DATA")

        def fake_run(cmd, **kwargs):
            return _mock_completed(0, stdout="done")

        runner = ProbeRunner()
        with patch("subprocess.run", side_effect=fake_run):
            result = runner.run(tmp_path, tmp_path / "Probe.csproj")
        # Output file exists with content → validated
        assert result.output_validated is True
        assert result.output_size_bytes > 0
        assert result.failure_taxonomy is None
