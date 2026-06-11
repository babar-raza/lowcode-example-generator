"""
Unit tests for Registry Bundle Completeness Validators (RBC-01..RBC-08)
Sprint: lowcode-plugin-canonical-package-wave11-20260605
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.plugin_examples.fixture_factory.registry_bundle_completeness_validators import (
    rbc_01_civ_entries_have_packages_or_queue,
    rbc_02_packages_have_manifest,
    rbc_03_packages_have_output_validation_pass,
    rbc_04_packages_have_log_proof,
    rbc_05_registry_count_matches_closeout,
    rbc_06_bundle_is_nonempty,
    rbc_07_bundle_sha_recorded,
    rbc_08_commit_sha_recorded,
    run_all_rbc_validators,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def make_package_dir(
    tmp: Path,
    family: str,
    slug: str,
    *,
    verdict: str = "PASS",
    include_logs: bool = True,
    include_manifest: bool = True,
) -> Path:
    pkg = tmp / family / slug
    pkg.mkdir(parents=True)
    # Program.cs
    (pkg / "Program.cs").write_text("// stub", encoding="utf-8")
    # .csproj
    (pkg / f"{family}-{slug}.csproj").write_text("<Project/>", encoding="utf-8")
    # output-validation.json
    (pkg / "output-validation.json").write_text(
        json.dumps({"package_key": f"{family}/{slug}", "verdict": verdict}), encoding="utf-8"
    )
    # output/
    out = pkg / "output"
    out.mkdir()
    (out / "result.txt").write_text("ok", encoding="utf-8")
    # source-provenance.json
    (pkg / "source-provenance.json").write_text("{}", encoding="utf-8")
    # package-manifest.json
    if include_manifest:
        (pkg / "package-manifest.json").write_text(
            json.dumps(
                {
                    "package_key": f"{family}/{slug}",
                    "family": family,
                    "plugin_slug": slug,
                    "canonical_url": f"https://example.com/{slug}/",
                    "identity_status": "CANONICAL_IDENTITY_VERIFIED",
                }
            ),
            encoding="utf-8",
        )
    # log files
    if include_logs:
        (pkg / "restore.log").write_text("restore ok", encoding="utf-8")
        (pkg / "build.log").write_text("build ok", encoding="utf-8")
        (pkg / "run.log").write_text("run ok", encoding="utf-8")
    return pkg


def complete_closeout() -> dict:
    return {
        "verdict": "SPRINT_COMPLETE",
        "registry_total": 67,
        "total_registry_entries": 67,
        "commit_sha": "abc1234",
        "evidence_bundle": {
            "objective": "COMPLETE",
            "entries": 100,
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "size_bytes": 50000,
        },
    }


# ─── RBC-01 ───────────────────────────────────────────────────────────────────


def test_rbc_01_all_civ_have_packages(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan-doc")
    result = rbc_01_civ_entries_have_packages_or_queue(
        civ_slugs=["ocr/scan-doc"],
        package_base_dirs=[tmp_path],
        queue_slugs=[],
    )
    assert result["result"] == "PASS"


def test_rbc_01_civ_in_queue(tmp_path):
    result = rbc_01_civ_entries_have_packages_or_queue(
        civ_slugs=["page/xps-converter"],
        package_base_dirs=[tmp_path],
        queue_slugs=["page/xps-converter"],
    )
    assert result["result"] == "PASS"


def test_rbc_01_civ_missing_and_not_in_queue(tmp_path):
    result = rbc_01_civ_entries_have_packages_or_queue(
        civ_slugs=["page/xps-converter"],
        package_base_dirs=[tmp_path],
        queue_slugs=[],
    )
    assert result["result"] == "ERROR"
    assert "page/xps-converter" in result["message"]


def test_rbc_01_empty_civ_list(tmp_path):
    result = rbc_01_civ_entries_have_packages_or_queue(
        civ_slugs=[],
        package_base_dirs=[tmp_path],
        queue_slugs=[],
    )
    assert result["result"] == "PASS"


# ─── RBC-02 ───────────────────────────────────────────────────────────────────


def test_rbc_02_all_have_manifest(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan")
    result = rbc_02_packages_have_manifest([pkg])
    assert result["result"] == "PASS"


def test_rbc_02_missing_manifest(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", include_manifest=False)
    result = rbc_02_packages_have_manifest([pkg])
    assert result["result"] == "ERROR"
    assert "missing package-manifest.json" in result["message"]


def test_rbc_02_manifest_missing_fields(tmp_path):
    pkg = tmp_path / "ocr" / "scan"
    pkg.mkdir(parents=True)
    (pkg / "package-manifest.json").write_text(json.dumps({"package_key": "ocr/scan"}), encoding="utf-8")
    result = rbc_02_packages_have_manifest([pkg])
    assert result["result"] == "ERROR"
    assert "missing fields" in result["message"]


def test_rbc_02_empty_package_list(tmp_path):
    result = rbc_02_packages_have_manifest([])
    assert result["result"] == "PASS"


# ─── RBC-03 ───────────────────────────────────────────────────────────────────


def test_rbc_03_all_pass(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", verdict="PASS")
    result = rbc_03_packages_have_output_validation_pass([pkg])
    assert result["result"] == "PASS"


def test_rbc_03_verdict_fail(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", verdict="FAIL")
    result = rbc_03_packages_have_output_validation_pass([pkg])
    assert result["result"] == "ERROR"
    assert "FAIL" in result["message"]


def test_rbc_03_missing_output_validation(tmp_path):
    pkg = tmp_path / "ocr" / "scan"
    pkg.mkdir(parents=True)
    result = rbc_03_packages_have_output_validation_pass([pkg])
    assert result["result"] == "ERROR"
    assert "missing output-validation.json" in result["message"]


def test_rbc_03_empty_list(tmp_path):
    result = rbc_03_packages_have_output_validation_pass([])
    assert result["result"] == "PASS"


# ─── RBC-04 ───────────────────────────────────────────────────────────────────


def test_rbc_04_all_logs_present(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", include_logs=True)
    result = rbc_04_packages_have_log_proof([pkg])
    assert result["result"] == "PASS"


def test_rbc_04_missing_restore_log(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", include_logs=False)
    (pkg / "build.log").write_text("ok")
    (pkg / "run.log").write_text("ok")
    result = rbc_04_packages_have_log_proof([pkg])
    assert result["result"] == "ERROR"
    assert "restore.log" in result["message"]


def test_rbc_04_missing_all_logs(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan", include_logs=False)
    result = rbc_04_packages_have_log_proof([pkg])
    assert result["result"] == "ERROR"


def test_rbc_04_empty_list(tmp_path):
    result = rbc_04_packages_have_log_proof([])
    assert result["result"] == "PASS"


# ─── RBC-05 ───────────────────────────────────────────────────────────────────


def test_rbc_05_count_matches(tmp_path):
    closeout = {"registry_total": 67}
    result = rbc_05_registry_count_matches_closeout(67, closeout)
    assert result["result"] == "PASS"


def test_rbc_05_count_mismatch(tmp_path):
    closeout = {"registry_total": 70}
    result = rbc_05_registry_count_matches_closeout(67, closeout)
    assert result["result"] == "ERROR"
    assert "70" in result["message"]


def test_rbc_05_uses_total_registry_entries_key(tmp_path):
    closeout = {"total_registry_entries": 67}
    result = rbc_05_registry_count_matches_closeout(67, closeout)
    assert result["result"] == "PASS"


def test_rbc_05_no_count_key_skips(tmp_path):
    result = rbc_05_registry_count_matches_closeout(67, {})
    assert result["result"] == "SKIP"


# ─── RBC-06 ───────────────────────────────────────────────────────────────────


def test_rbc_06_nonempty_bundle(tmp_path):
    closeout = {"evidence_bundle": {"entries": 100}}
    result = rbc_06_bundle_is_nonempty(closeout)
    assert result["result"] == "PASS"


def test_rbc_06_empty_bundle(tmp_path):
    closeout = {"evidence_bundle": {"entries": 0}}
    result = rbc_06_bundle_is_nonempty(closeout)
    assert result["result"] == "ERROR"


def test_rbc_06_no_bundle_dict_skips(tmp_path):
    result = rbc_06_bundle_is_nonempty({})
    assert result["result"] == "SKIP"


def test_rbc_06_no_entries_field_skips(tmp_path):
    result = rbc_06_bundle_is_nonempty({"evidence_bundle": {"sha256": "abc"}})
    assert result["result"] == "SKIP"


# ─── RBC-07 ───────────────────────────────────────────────────────────────────


def test_rbc_07_sha_recorded(tmp_path):
    closeout = {"evidence_bundle": {"sha256": "abc123def456"}}
    result = rbc_07_bundle_sha_recorded(closeout)
    assert result["result"] == "PASS"


def test_rbc_07_sha_pending(tmp_path):
    closeout = {"evidence_bundle": {"sha256": "PENDING"}}
    result = rbc_07_bundle_sha_recorded(closeout)
    assert result["result"] == "ERROR"


def test_rbc_07_sha_empty(tmp_path):
    closeout = {"evidence_bundle": {"sha256": ""}}
    result = rbc_07_bundle_sha_recorded(closeout)
    assert result["result"] == "ERROR"


def test_rbc_07_no_bundle_skips(tmp_path):
    result = rbc_07_bundle_sha_recorded({})
    assert result["result"] == "SKIP"


# ─── RBC-08 ───────────────────────────────────────────────────────────────────


def test_rbc_08_commit_sha_recorded(tmp_path):
    result = rbc_08_commit_sha_recorded({"commit_sha": "abc1234"})
    assert result["result"] == "PASS"


def test_rbc_08_commit_sha_pending(tmp_path):
    result = rbc_08_commit_sha_recorded({"commit_sha": "PENDING"})
    assert result["result"] == "ERROR"


def test_rbc_08_commit_sha_missing(tmp_path):
    result = rbc_08_commit_sha_recorded({})
    assert result["result"] == "ERROR"


def test_rbc_08_commit_sha_null_string(tmp_path):
    result = rbc_08_commit_sha_recorded({"commit_sha": "null"})
    assert result["result"] == "ERROR"


# ─── Aggregate runner ─────────────────────────────────────────────────────────


def test_aggregate_runner_all_pass(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan-image")
    closeout = complete_closeout()
    result = run_all_rbc_validators(
        civ_slugs=["ocr/scan-image"],
        package_base_dirs=[tmp_path],
        queue_slugs=[],
        package_dirs=[pkg],
        actual_registry_count=67,
        closeout=closeout,
    )
    assert result["verdict"] == "ALL_PASS"
    assert result["failed"] == 0


def test_aggregate_runner_fail_propagates(tmp_path):
    pkg = make_package_dir(tmp_path, "ocr", "scan-image", include_logs=False)
    closeout = complete_closeout()
    result = run_all_rbc_validators(
        civ_slugs=["ocr/scan-image"],
        package_base_dirs=[tmp_path],
        queue_slugs=[],
        package_dirs=[pkg],
        actual_registry_count=67,
        closeout=closeout,
    )
    assert result["verdict"] == "FAIL"
    assert result["failed"] >= 1
