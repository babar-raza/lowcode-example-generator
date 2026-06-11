"""Tests for anti-overclaiming validator rules (Wave 6)."""

import json
import tempfile
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.anti_overclaiming_validators import (
    AocViolation,
    aoc_01_output_dir_exists,
    aoc_02_no_zero_byte_primary_output,
    aoc_03_output_validation_verdict_matches_run,
    aoc_04_no_fabricated_output,
    aoc_05_no_stale_error_snippet_on_pass,
    aoc_06_provenance_json_valid,
    aoc_07_no_double_brace_in_json,
    aoc_08_canonical_url_not_placeholder,
    aoc_09_package_manifest_consistent,
    aoc_10_restore_log_exists,
    aoc_11_build_log_exists,
    aoc_12_no_exception_in_pass_run,
    aoc_14_no_duplicate_output_files,
    aoc_15_readme_present,
    aoc_16_program_cs_present,
    run_anti_overclaiming_checks,
)


def _make_clean_package(tmp_path: Path, key: str = "test/pkg") -> Path:
    """Create a minimal clean package that should pass all AOC rules."""
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    output_dir = pkg_dir / "output"
    output_dir.mkdir()
    (output_dir / "output.pdf").write_bytes(b"%PDF-1.4 test output content " + b"x" * 200)
    (pkg_dir / "run.log").write_text("Build succeeded.\nPDF saved: output/output.pdf (230 bytes)\n")
    (pkg_dir / "restore.log").write_text("Restore succeeded.\n")
    (pkg_dir / "build.log").write_text("Build succeeded.\n1 Warning(s)\n0 Error(s)\n")
    (pkg_dir / "Program.cs").write_text('// test/pkg\nConsole.WriteLine("hi");\n')
    (pkg_dir / "README.md").write_text("# test/pkg\n")
    (pkg_dir / "output-validation.json").write_text(
        json.dumps(
            {"package_key": key, "verdict": "PASS", "output_files": [{"path": "output/output.pdf", "size": 230}]}
        )
    )
    (pkg_dir / "source-provenance.json").write_text(
        json.dumps(
            {
                "family": "test",
                "plugin_slug": "pkg",
                "nuget_package": "Aspose.Test",
                "nuget_version": "1.0.0",
                "canonical_url": "https://products.aspose.net/test/pkg/",
            }
        )
    )
    (pkg_dir / "package-manifest.json").write_text(
        json.dumps(
            {
                "package_key": key,
                "nuget_package": "Aspose.Test",
                "nuget_version": "1.0.0",
                "canonical_url": "https://products.aspose.net/test/pkg/",
            }
        )
    )
    return pkg_dir


class TestAoc01OutputDirExists:
    def test_pass_when_output_dir_present(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output").mkdir()
        assert aoc_01_output_dir_exists(pkg, "t/p") is None

    def test_violation_when_output_dir_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_01_output_dir_exists(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-01"


class TestAoc02NoZeroByteOutput:
    def test_pass_when_output_nonzero(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_02_no_zero_byte_primary_output(pkg, "t/p") == []

    def test_violation_when_primary_output_zero(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        out = pkg / "output"
        out.mkdir()
        (out / "result.pdf").write_bytes(b"")
        (pkg / "output-validation.json").write_text(
            json.dumps({"verdict": "PASS", "output_files": [{"path": "output/result.pdf", "size": 0}]})
        )
        violations = aoc_02_no_zero_byte_primary_output(pkg, "t/p")
        assert any(v.rule_id == "AOC-02" for v in violations)

    def test_no_violation_for_intermediate_files(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output-validation.json").write_text(
            json.dumps(
                {
                    "verdict": "PASS",
                    "output_files": [
                        {"path": "output/fixture.psd", "size": 0},
                        {"path": "output/output.jpg", "size": 5000},
                    ],
                }
            )
        )
        violations = aoc_02_no_zero_byte_primary_output(pkg, "t/p")
        assert violations == []


class TestAoc03VerdictMatchesOutput:
    def test_pass_when_verdict_and_output_consistent(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_03_output_validation_verdict_matches_run(pkg, "t/p") is None

    def test_violation_when_pass_claimed_but_no_output(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output-validation.json").write_text(
            json.dumps({"verdict": "PASS", "output_files": [{"path": "output/out.pdf", "size": 5}]})
        )
        v = aoc_03_output_validation_verdict_matches_run(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-03"

    def test_no_violation_when_fail_and_no_output(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "FAIL", "output_files": []}))
        v = aoc_03_output_validation_verdict_matches_run(pkg, "t/p")
        assert v is None


class TestAoc04NoFabricatedOutput:
    def test_pass_when_run_log_matches_output(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_04_no_fabricated_output(pkg, "t/p") is None

    def test_violation_when_output_exists_but_run_log_empty(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        out = pkg / "output"
        out.mkdir()
        (out / "result.pdf").write_bytes(b"%PDF " + b"x" * 200)
        (pkg / "run.log").write_text("")
        v = aoc_04_no_fabricated_output(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-04"


class TestAoc05NoStaleError:
    def test_pass_for_clean_build(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_05_no_stale_error_snippet_on_pass(pkg, "t/p") is None

    def test_violation_when_pass_but_build_failed(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "build.log").write_text("Program.cs(5,1): error CS0103: name not found\nBuild FAILED\n1 Error(s)")
        v = aoc_05_no_stale_error_snippet_on_pass(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-05"


class TestAoc06ProvenanceValid:
    def test_pass_when_provenance_complete(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_06_provenance_json_valid(pkg, "t/p") is None

    def test_violation_when_provenance_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_06_provenance_json_valid(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-06"

    def test_violation_when_provenance_invalid_json(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "source-provenance.json").write_text("{{ not valid json }}")
        v = aoc_06_provenance_json_valid(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-06"

    def test_violation_when_missing_required_fields(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "source-provenance.json").write_text(json.dumps({"family": "test"}))
        v = aoc_06_provenance_json_valid(pkg, "t/p")
        assert v is not None
        assert "plugin_slug" in v.description or "canonical_url" in v.description


class TestAoc07NoDoubleBrace:
    def test_pass_when_no_double_brace(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_07_no_double_brace_in_json(pkg, "t/p") == []

    def test_violation_when_double_brace_in_provenance(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "source-provenance.json").write_text('{{"family": "test", "plugin_slug": "pkg"}}')
        violations = aoc_07_no_double_brace_in_json(pkg, "t/p")
        assert any(v.rule_id == "AOC-07" for v in violations)


class TestAoc08CanonicalUrl:
    def test_pass_for_valid_url(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_08_canonical_url_not_placeholder(pkg, "t/p") is None

    def test_violation_when_url_empty(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "source-provenance.json").write_text(
            json.dumps({"family": "t", "plugin_slug": "p", "nuget_package": "A", "canonical_url": ""})
        )
        v = aoc_08_canonical_url_not_placeholder(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-08"


class TestAoc09ManifestConsistent:
    def test_pass_when_consistent(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_09_package_manifest_consistent(pkg, "t/p") == []

    def test_violation_when_version_mismatch(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "source-provenance.json").write_text(
            json.dumps(
                {
                    "nuget_package": "Aspose.Test",
                    "nuget_version": "1.0.0",
                    "family": "t",
                    "plugin_slug": "p",
                    "canonical_url": "https://example.com",
                }
            )
        )
        (pkg / "package-manifest.json").write_text(
            json.dumps({"nuget_package": "Aspose.Test", "nuget_version": "2.0.0"})
        )
        violations = aoc_09_package_manifest_consistent(pkg, "t/p")
        assert any(v.rule_id == "AOC-09" for v in violations)


class TestAoc10And11Logs:
    def test_pass_when_logs_exist(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_10_restore_log_exists(pkg, "t/p") is None
        assert aoc_11_build_log_exists(pkg, "t/p") is None

    def test_violation_when_restore_log_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_10_restore_log_exists(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-10"

    def test_violation_when_build_log_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_11_build_log_exists(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-11"


class TestAoc12NoExceptionOnPass:
    def test_pass_when_clean_run(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_12_no_exception_in_pass_run(pkg, "t/p") is None

    def test_violation_when_pass_but_exception(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "run.log").write_text("Unhandled exception. System.InvalidOperationException: test\n")
        v = aoc_12_no_exception_in_pass_run(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-12"


class TestAoc14NoDuplicates:
    def test_pass_when_no_duplicates(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_14_no_duplicate_output_files(pkg, "t/p") is None


class TestAoc15And16Structure:
    def test_pass_when_readme_and_program_present(self, tmp_path):
        pkg = _make_clean_package(tmp_path)
        assert aoc_15_readme_present(pkg, "t/p") is None
        assert aoc_16_program_cs_present(pkg, "t/p") is None

    def test_warning_when_readme_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_15_readme_present(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-15"
        assert v.severity == "WARNING"

    def test_error_when_program_cs_missing(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        v = aoc_16_program_cs_present(pkg, "t/p")
        assert v is not None
        assert v.rule_id == "AOC-16"
        assert v.severity == "ERROR"


class TestRunAllAocChecks:
    def test_clean_package_passes_all_16_rules(self, tmp_path):
        pkg = _make_clean_package(tmp_path, "t/p")
        result = run_anti_overclaiming_checks(pkg, "t/p")
        assert result.rules_checked == 16
        error_violations = [v for v in result.violations if v.severity == "ERROR"]
        assert error_violations == [], f"Unexpected ERROR violations: {error_violations}"

    def test_result_counts_rules(self, tmp_path):
        pkg = _make_clean_package(tmp_path, "t/p")
        result = run_anti_overclaiming_checks(pkg, "t/p")
        assert result.rules_checked == 16

    def test_missing_package_fails_multiple_rules(self, tmp_path):
        pkg = tmp_path / "empty"
        pkg.mkdir()
        result = run_anti_overclaiming_checks(pkg, "t/p")
        assert result.violation_count > 0
        assert not result.passed
