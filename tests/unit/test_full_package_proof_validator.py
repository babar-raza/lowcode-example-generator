"""
Tests for Full Package Proof Validator (FPP-01..FPP-12)
Sprint: lowcode-plugin-canonical-package-wave9-20260605
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil

from src.plugin_examples.fixture_factory.full_package_proof_validator import (
    run_full_package_proof_validator,
    ProofResult,
    ProofViolation,
)


@pytest.fixture
def full_pkg(tmp_path):
    """Create a fully-proven package directory."""
    pkg = tmp_path / "test-family" / "test-plugin"
    pkg.mkdir(parents=True)

    (pkg / "Program.cs").write_text("// test program")
    (pkg / "test-plugin.csproj").write_text("<Project></Project>")
    (pkg / "README.md").write_text("# Test Plugin for .NET")
    (pkg / "source-provenance.json").write_text(
        json.dumps(
            {
                "family": "test-family",
                "plugin_slug": "test-plugin",
                "canonical_plugin_slug": "test-plugin",
                "canonical_url": "https://products.aspose.net/test-family/test-plugin/",
                "display_plugin_name": "Test Plugin for .NET",
                "identity_status": "CANONICAL_IDENTITY_VERIFIED",
            }
        )
    )
    (pkg / "package-manifest.json").write_text(
        json.dumps(
            {
                "package_key": "test-family/test-plugin",
                "proof_type": "MIGRATED_FULL_PACKAGE",
            }
        )
    )
    (pkg / "restore.log").write_text("restore output")
    (pkg / "build.log").write_text("build output")
    (pkg / "run.log").write_text("run output")
    out = pkg / "output"
    out.mkdir()
    (out / "result.pdf").write_bytes(b"PDF content here")
    (pkg / "output-validation.json").write_text(
        json.dumps(
            {
                "package_key": "test-family/test-plugin",
                "verdict": "PASS",
                "restore_status": "SUCCESS",
                "build_status": "SUCCESS",
                "run_status": "SUCCESS",
            }
        )
    )
    return pkg


def test_fpp_full_package_passes(full_pkg):
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert result.passes
    assert result.proof_type == "FULL_PACKAGE_PROVEN"
    assert result.error_count == 0


def test_fpp_01_missing_program_cs(full_pkg):
    (full_pkg / "Program.cs").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-01" for v in result.violations)


def test_fpp_02_missing_csproj(full_pkg):
    for f in full_pkg.glob("*.csproj"):
        f.unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-02" for v in result.violations)


def test_fpp_03_missing_readme_is_warning(full_pkg):
    (full_pkg / "README.md").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert result.passes  # only warning
    assert any(v.rule == "FPP-03" and v.severity == "WARNING" for v in result.violations)


def test_fpp_04_missing_source_provenance(full_pkg):
    (full_pkg / "source-provenance.json").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-04" for v in result.violations)


def test_fpp_05_missing_package_manifest_is_warning(full_pkg):
    (full_pkg / "package-manifest.json").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert result.passes  # only warning
    assert any(v.rule == "FPP-05" and v.severity == "WARNING" for v in result.violations)


def test_fpp_06_missing_restore_log_is_warning(full_pkg):
    (full_pkg / "restore.log").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert result.passes  # only warning
    assert any(v.rule == "FPP-06" and v.severity == "WARNING" for v in result.violations)


def test_fpp_06_restore_log_in_logs_subdir(full_pkg):
    (full_pkg / "restore.log").unlink()
    logs = full_pkg / "logs"
    logs.mkdir()
    (logs / "restore.log").write_text("restore output")
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not any(v.rule == "FPP-06" for v in result.violations)


def test_fpp_09_missing_output_validation(full_pkg):
    (full_pkg / "output-validation.json").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-09" for v in result.violations)


def test_fpp_10_empty_output_dir(full_pkg):
    shutil.rmtree(full_pkg / "output")
    out = full_pkg / "output"
    out.mkdir()  # empty output dir
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-10" for v in result.violations)


def test_fpp_10_missing_output_dir(full_pkg):
    shutil.rmtree(full_pkg / "output")
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    assert any(v.rule == "FPP-10" for v in result.violations)


def test_fpp_11_pass_verdict_with_proof_errors(full_pkg):
    # Remove Program.cs to cause FPP-01 error, but ov still says PASS
    (full_pkg / "Program.cs").unlink()
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not result.passes
    rules = [v.rule for v in result.violations]
    assert "FPP-01" in rules
    assert "FPP-11" in rules


def test_fpp_11_no_false_positive_with_clean_package(full_pkg):
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert not any(v.rule == "FPP-11" for v in result.violations)


def test_fpp_12_metadata_only_with_full_files(full_pkg):
    # Set proof_type to METADATA_ONLY even though all files exist
    pm_path = full_pkg / "package-manifest.json"
    pm = json.loads(pm_path.read_text())
    pm["proof_type"] = "METADATA_ONLY"
    pm_path.write_text(json.dumps(pm))
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    assert any(v.rule == "FPP-12" and v.severity == "WARNING" for v in result.violations)


def test_proof_result_properties():
    r = ProofResult("a/b")
    assert r.passes
    assert r.error_count == 0
    assert r.warning_count == 0

    r.violations.append(ProofViolation("FPP-01", "ERROR", "msg", "path"))
    assert not r.passes
    assert r.error_count == 1

    r2 = ProofResult("c/d")
    r2.violations.append(ProofViolation("FPP-03", "WARNING", "warn", "path"))
    assert r2.passes
    assert r2.warning_count == 1


def test_proof_result_to_dict(full_pkg):
    result = run_full_package_proof_validator(full_pkg, "test-family/test-plugin")
    d = result.to_dict()
    assert d["package_key"] == "test-family/test-plugin"
    assert d["passes"] is True
    assert d["proof_type"] == "FULL_PACKAGE_PROVEN"


def test_metadata_only_package_fails_fpp():
    """A package with only metadata files must fail FPP-01 and FPP-02."""
    import os

    with tempfile.TemporaryDirectory() as tmp:
        pkg = Path(tmp) / "family" / "slug"
        pkg.mkdir(parents=True)
        (pkg / "source-provenance.json").write_text(json.dumps({"identity_status": "CANONICAL_IDENTITY_VERIFIED"}))
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "output").mkdir()
        (pkg / "output" / "out.txt").write_bytes(b"data")
        result = run_full_package_proof_validator(pkg, "family/slug")
        assert not result.passes
        rules = {v.rule for v in result.violations if v.severity == "ERROR"}
        assert "FPP-01" in rules
        assert "FPP-02" in rules
        assert "FPP-11" in rules
