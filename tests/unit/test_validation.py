"""Unit tests for verifier_bridge: dotnet_runner, output_validator, bridge."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.verifier_bridge.dotnet_runner import (
    DotnetResult,
    ValidationResult,
    run_dotnet_validation,
    write_validation_results,
)
import io
import zipfile as _zipfile

from plugin_examples.verifier_bridge.output_validator import (
    OutputValidation,
    validate_output,
    validate_output_file_semantic,
    write_output_validation,
)
from plugin_examples.verifier_bridge.bridge import (
    ReviewerResult,
    ReviewerUnavailableError,
    check_reviewer_availability,
    run_example_reviewer,
    write_reviewer_results,
)


# --- Tests: dotnet_runner ---


class TestDotnetRunner:
    def test_successful_validation(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Build succeeded"
        mock_result.stderr = ""

        with patch("plugin_examples.verifier_bridge.dotnet_runner.subprocess.run",
                    return_value=mock_result):
            result = run_dotnet_validation(project_dir, "test-scenario")

        assert result.passed
        assert result.restore.success
        assert result.build.success

    def test_build_failure(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        call_count = 0
        def mock_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            r = MagicMock()
            if call_count == 1:  # restore
                r.returncode = 0
                r.stdout = "Restore succeeded"
                r.stderr = ""
            else:  # build
                r.returncode = 1
                r.stdout = ""
                r.stderr = "Build failed: CS1234"
            return r

        with patch("plugin_examples.verifier_bridge.dotnet_runner.subprocess.run",
                    side_effect=mock_run):
            result = run_dotnet_validation(project_dir, "test-scenario")

        assert not result.passed
        assert result.failure_stage == "build"

    def test_skip_run(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""

        with patch("plugin_examples.verifier_bridge.dotnet_runner.subprocess.run",
                    return_value=mock_result):
            result = run_dotnet_validation(project_dir, "test", skip_run=True)

        assert result.passed
        assert result.run is None

    def test_write_validation_results(self, tmp_path):
        results = [
            ValidationResult(scenario_id="s1", passed=True,
                             restore=DotnetResult("restore", True),
                             build=DotnetResult("build", True)),
            ValidationResult(scenario_id="s2", passed=False, failure_stage="build",
                             restore=DotnetResult("restore", True),
                             build=DotnetResult("build", False)),
        ]
        path = write_validation_results(results, tmp_path / "workspace" / "verification")
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["total"] == 2
        assert data["passed"] == 1
        assert data["failed"] == 1


# --- Tests: output_validator ---


class TestOutputValidator:
    def test_valid_output_passes(self):
        result = validate_output("s1", "Hello World\nDone.", "")
        assert result.passed
        assert result.has_output

    def test_no_output_fails(self):
        result = validate_output("s1", "", "")
        assert not result.passed
        assert "No output" in result.issues[0]

    def test_exception_in_stderr_fails(self):
        result = validate_output("s1", "output", "System.Exception: Something failed")
        assert not result.passed
        assert result.has_error

    def test_unhandled_exception_fails(self):
        result = validate_output("s1", "Unhandled exception: NullRef", "")
        assert not result.passed
        assert result.has_error

    def test_expected_patterns_checked(self):
        result = validate_output("s1", "Hello", "", expected_patterns=["World"])
        assert not result.passed
        assert any("Missing" in i for i in result.issues)

    def test_write_output_validation(self, tmp_path):
        v = OutputValidation(scenario_id="s1", passed=True, has_output=True)
        path = write_output_validation(v, tmp_path / "workspace" / "runs" / "test")
        assert path.exists()


# --- Tests: semantic file validators ---


def _make_minimal_ooxml(tmp_path: Path, filename: str, internal_entry: str) -> Path:
    """Create a minimal OOXML ZIP file with the given internal XML entry."""
    out = tmp_path / filename
    buf = io.BytesIO()
    with _zipfile.ZipFile(buf, "w") as z:
        z.writestr(internal_entry, "<root/>")
    out.write_bytes(buf.getvalue())
    return out


def _make_bad_file(tmp_path: Path, filename: str, content: bytes = b"NOTAVALIDFORMAT") -> Path:
    out = tmp_path / filename
    out.write_bytes(content)
    return out


_OLE2_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 504


class TestOoxmlValidator:
    def test_docx_valid_passes(self, tmp_path):
        path = _make_minimal_ooxml(tmp_path, "output.docx", "word/document.xml")
        result = validate_output_file_semantic(path)
        zip_check = next(c for c in result["checks"] if c["check"] == "docx_zip_magic")
        xml_check = next(c for c in result["checks"] if c["check"] == "docx_internal_xml")
        assert zip_check["passed"]
        assert xml_check["passed"]

    def test_docx_wrong_bytes_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.docx")
        result = validate_output_file_semantic(path)
        zip_check = next(c for c in result["checks"] if c["check"] == "docx_zip_magic")
        assert not zip_check["passed"]

    def test_pptx_valid_passes(self, tmp_path):
        path = _make_minimal_ooxml(tmp_path, "output.pptx", "ppt/presentation.xml")
        result = validate_output_file_semantic(path)
        zip_check = next(c for c in result["checks"] if c["check"] == "pptx_zip_magic")
        xml_check = next(c for c in result["checks"] if c["check"] == "pptx_internal_xml")
        assert zip_check["passed"]
        assert xml_check["passed"]

    def test_pptx_wrong_bytes_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.pptx")
        result = validate_output_file_semantic(path)
        zip_check = next(c for c in result["checks"] if c["check"] == "pptx_zip_magic")
        assert not zip_check["passed"]

    def test_docx_missing_internal_xml_fails(self, tmp_path):
        """Valid ZIP but without word/document.xml."""
        out = tmp_path / "output.docx"
        buf = io.BytesIO()
        with _zipfile.ZipFile(buf, "w") as z:
            z.writestr("other/file.xml", "<root/>")
        out.write_bytes(buf.getvalue())
        result = validate_output_file_semantic(out)
        xml_check = next(c for c in result["checks"] if c["check"] == "docx_internal_xml")
        assert not xml_check["passed"]


class TestOle2Validator:
    def test_doc_valid_passes(self, tmp_path):
        path = tmp_path / "output.doc"
        path.write_bytes(_OLE2_HEADER)
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "doc_ole2_magic")
        assert ole2_check["passed"]

    def test_doc_wrong_bytes_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.doc")
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "doc_ole2_magic")
        assert not ole2_check["passed"]

    def test_xls_valid_passes(self, tmp_path):
        path = tmp_path / "output.xls"
        path.write_bytes(_OLE2_HEADER)
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "xls_ole2_magic")
        assert ole2_check["passed"]

    def test_xls_wrong_bytes_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.xls")
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "xls_ole2_magic")
        assert not ole2_check["passed"]


class TestEmlValidator:
    _VALID_EML = b"From: test@test.com\nTo: to@test.com\nSubject: Test\n\nBody text."

    def test_eml_valid_passes(self, tmp_path):
        path = tmp_path / "output.eml"
        path.write_bytes(self._VALID_EML)
        result = validate_output_file_semantic(path)
        hdr_check = next(c for c in result["checks"] if c["check"] == "eml_rfc2822_headers")
        assert hdr_check["passed"]

    def test_eml_no_headers_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.eml", b"This is just plain text without headers.")
        result = validate_output_file_semantic(path)
        hdr_check = next(c for c in result["checks"] if c["check"] == "eml_rfc2822_headers")
        assert not hdr_check["passed"]

    def test_eml_mime_version_header_passes(self, tmp_path):
        path = tmp_path / "output.eml"
        path.write_bytes(b"MIME-Version: 1.0\nContent-Type: text/plain\n\nBody.")
        result = validate_output_file_semantic(path)
        hdr_check = next(c for c in result["checks"] if c["check"] == "eml_rfc2822_headers")
        assert hdr_check["passed"]


class TestMsgValidator:
    def test_msg_valid_passes(self, tmp_path):
        path = tmp_path / "output.msg"
        path.write_bytes(_OLE2_HEADER)
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "msg_ole2_magic")
        assert ole2_check["passed"]

    def test_msg_wrong_bytes_fails(self, tmp_path):
        path = _make_bad_file(tmp_path, "output.msg")
        result = validate_output_file_semantic(path)
        ole2_check = next(c for c in result["checks"] if c["check"] == "msg_ole2_magic")
        assert not ole2_check["passed"]


# --- Tests: bridge ---


class TestBridge:
    def test_reviewer_unavailable_raises(self):
        with pytest.raises(ReviewerUnavailableError):
            run_example_reviewer(
                family="cells",
                workspace_dir=Path("/tmp"),
                reviewer_path=Path("/nonexistent/path"),
            )

    def test_check_availability_missing_path(self):
        assert not check_reviewer_availability(Path("/nonexistent/reviewer"))

    def test_write_reviewer_results(self, tmp_path):
        result = ReviewerResult(available=False, passed=False,
                                error="Not available")
        path = write_reviewer_results(result, tmp_path / "workspace" / "verification")
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["available"] is False

    def test_paths_use_workspace(self, tmp_path):
        result = ReviewerResult(available=True, passed=True)
        path = write_reviewer_results(result, tmp_path / "workspace" / "verification")
        assert "workspace" in str(path)
        assert "verification" in str(path)
