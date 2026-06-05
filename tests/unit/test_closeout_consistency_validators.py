"""
Tests for Closeout Consistency Validators (CCV-01..CCV-18)
Sprint: lowcode-plugin-canonical-package-wave10-20260605
"""
import json
import pytest
from pathlib import Path

from src.plugin_examples.fixture_factory.closeout_consistency_validators import (
    run_closeout_consistency_validators,
    check_ccv_01_evidence_bundle_not_pending,
    check_ccv_02_lane_ledger_lanes_complete,
    check_ccv_03_taskcards_complete,
    check_ccv_04_test_log_exists,
    check_ccv_05_git_status_recorded,
    check_ccv_06_commit_proof_recorded,
    check_ccv_07_canonical_url_for_verified,
    check_ccv_08_display_name_for_verified,
    check_ccv_09_publication_clean_has_canonical_url,
    check_ccv_10_pass_package_has_program_cs,
    check_ccv_11_pass_package_has_csproj,
    check_ccv_12_pass_package_has_logs,
    check_ccv_13_no_legacy_alias_as_publication_candidate,
    check_ccv_14_matrix_has_canonical_url_column,
    check_ccv_15_publication_ready_has_package_proof,
    check_ccv_16_registry_count_matches_claimed,
    check_ccv_17_no_errors_with_complete_verdict,
    check_ccv_18_bundle_entry_count_positive,
    CcvResult,
    CcvViolation,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def complete_closeout(**overrides):
    base = {
        "verdict": "SPRINT_COMPLETE",
        "evidence_bundle": {"objective": "COMPLETE — bundle written", "entries": 42},
        "commit_sha": "abc1234",
        "pytest_passed": 100,
    }
    base.update(overrides)
    return base


def pending_closeout(**overrides):
    base = {
        "verdict": "PENDING",
        "evidence_bundle": {"objective": "PENDING"},
    }
    base.update(overrides)
    return base


def verified_entry(slug="my-plugin", family="myFamily", url="https://products.aspose.net/myFamily/my-plugin/", name="My Plugin for .NET"):
    return {
        "plugin_slug": slug,
        "family": family,
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "canonical_url": url,
        "display_plugin_name": name,
    }


# ---------------------------------------------------------------------------
# CCV-01
# ---------------------------------------------------------------------------

def test_ccv_01_passes_when_bundle_complete():
    result = CcvResult()
    check_ccv_01_evidence_bundle_not_pending(complete_closeout(), result)
    assert not any(v.rule == "CCV-01" for v in result.violations)


def test_ccv_01_error_when_verdict_complete_bundle_pending():
    result = CcvResult()
    closeout = {"verdict": "SPRINT_COMPLETE", "evidence_bundle": {"objective": "PENDING"}}
    check_ccv_01_evidence_bundle_not_pending(closeout, result)
    assert any(v.rule == "CCV-01" and v.severity == "ERROR" for v in result.violations)


def test_ccv_01_no_false_positive_when_verdict_pending():
    result = CcvResult()
    check_ccv_01_evidence_bundle_not_pending(pending_closeout(), result)
    assert not any(v.rule == "CCV-01" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-02
# ---------------------------------------------------------------------------

def complete_lane_ledger():
    return {"lanes": [
        {"lane": "A", "status": "COMPLETE"},
        {"lane": "B", "status": "COMPLETE"},
    ]}


def test_ccv_02_passes_when_all_lanes_complete():
    result = CcvResult()
    check_ccv_02_lane_ledger_lanes_complete(complete_closeout(), complete_lane_ledger(), result)
    assert not any(v.rule == "CCV-02" for v in result.violations)


def test_ccv_02_error_when_lane_pending():
    result = CcvResult()
    ledger = {"lanes": [{"lane": "A", "status": "PENDING"}]}
    check_ccv_02_lane_ledger_lanes_complete(complete_closeout(), ledger, result)
    assert any(v.rule == "CCV-02" and v.severity == "ERROR" for v in result.violations)


def test_ccv_02_error_when_no_ledger_provided():
    result = CcvResult()
    check_ccv_02_lane_ledger_lanes_complete(complete_closeout(), None, result)
    assert any(v.rule == "CCV-02" for v in result.violations)


def test_ccv_02_no_check_when_sprint_not_complete():
    result = CcvResult()
    ledger = {"lanes": [{"lane": "A", "status": "PENDING"}]}
    check_ccv_02_lane_ledger_lanes_complete(pending_closeout(), ledger, result)
    assert not any(v.rule == "CCV-02" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-03
# ---------------------------------------------------------------------------

def test_ccv_03_passes_when_taskcards_complete():
    result = CcvResult()
    cards = [{"id": "TC-01", "status": "COMPLETE"}]
    check_ccv_03_taskcards_complete(complete_closeout(), cards, result)
    assert not any(v.rule == "CCV-03" for v in result.violations)


def test_ccv_03_error_when_taskcard_pending():
    result = CcvResult()
    cards = [{"id": "TC-01", "status": "PENDING"}]
    check_ccv_03_taskcards_complete(complete_closeout(), cards, result)
    assert any(v.rule == "CCV-03" and v.severity == "ERROR" for v in result.violations)


def test_ccv_03_error_when_no_taskcards_provided():
    result = CcvResult()
    check_ccv_03_taskcards_complete(complete_closeout(), None, result)
    assert any(v.rule == "CCV-03" for v in result.violations)


def test_ccv_03_no_check_when_sprint_pending():
    result = CcvResult()
    cards = [{"id": "TC-01", "status": "PENDING"}]
    check_ccv_03_taskcards_complete(pending_closeout(), cards, result)
    assert not any(v.rule == "CCV-03" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-04
# ---------------------------------------------------------------------------

def test_ccv_04_no_violation_when_no_test_count_claimed():
    result = CcvResult()
    check_ccv_04_test_log_exists({}, None, result)
    assert not any(v.rule == "CCV-04" for v in result.violations)


def test_ccv_04_passes_when_log_file_exists(tmp_path):
    (tmp_path / "pytest-stdout.txt").write_text("17 passed")
    result = CcvResult()
    check_ccv_04_test_log_exists({"pytest_passed": 17}, tmp_path, result)
    assert not any(v.rule == "CCV-04" for v in result.violations)


def test_ccv_04_error_when_log_missing(tmp_path):
    result = CcvResult()
    check_ccv_04_test_log_exists({"pytest_passed": 17}, tmp_path, result)
    assert any(v.rule == "CCV-04" and v.severity == "ERROR" for v in result.violations)


def test_ccv_04_error_when_no_report_dir():
    result = CcvResult()
    check_ccv_04_test_log_exists({"pytest_passed": 100}, None, result)
    assert any(v.rule == "CCV-04" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-05
# ---------------------------------------------------------------------------

def test_ccv_05_no_violation_when_git_status_present(tmp_path):
    (tmp_path / "git-status.txt").write_text("nothing to commit")
    result = CcvResult()
    check_ccv_05_git_status_recorded(complete_closeout(), tmp_path, result)
    assert not any(v.rule == "CCV-05" for v in result.violations)


def test_ccv_05_warning_when_git_status_missing(tmp_path):
    result = CcvResult()
    check_ccv_05_git_status_recorded(complete_closeout(), tmp_path, result)
    assert any(v.rule == "CCV-05" and v.severity == "WARNING" for v in result.violations)


def test_ccv_05_no_check_when_not_complete(tmp_path):
    result = CcvResult()
    check_ccv_05_git_status_recorded(pending_closeout(), tmp_path, result)
    assert not any(v.rule == "CCV-05" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-06
# ---------------------------------------------------------------------------

def test_ccv_06_passes_with_commit_sha():
    result = CcvResult()
    check_ccv_06_commit_proof_recorded(complete_closeout(commit_sha="abc1234"), result)
    assert not any(v.rule == "CCV-06" for v in result.violations)


def test_ccv_06_warning_when_no_commit():
    result = CcvResult()
    closeout = {"verdict": "SPRINT_COMPLETE", "evidence_bundle": {"objective": "COMPLETE"}}
    check_ccv_06_commit_proof_recorded(closeout, result)
    assert any(v.rule == "CCV-06" and v.severity == "WARNING" for v in result.violations)


def test_ccv_06_no_check_when_pending():
    result = CcvResult()
    check_ccv_06_commit_proof_recorded(pending_closeout(), result)
    assert not any(v.rule == "CCV-06" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-07
# ---------------------------------------------------------------------------

def test_ccv_07_passes_when_url_present():
    result = CcvResult()
    check_ccv_07_canonical_url_for_verified([verified_entry()], result)
    assert not any(v.rule == "CCV-07" for v in result.violations)


def test_ccv_07_error_when_url_missing():
    result = CcvResult()
    entry = verified_entry()
    del entry["canonical_url"]
    check_ccv_07_canonical_url_for_verified([entry], result)
    assert any(v.rule == "CCV-07" and v.severity == "ERROR" for v in result.violations)


def test_ccv_07_skips_non_verified_entries():
    result = CcvResult()
    entry = {"plugin_slug": "foo", "identity_status": "SLUG_ALIAS_REQUIRED"}
    check_ccv_07_canonical_url_for_verified([entry], result)
    assert not any(v.rule == "CCV-07" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-08
# ---------------------------------------------------------------------------

def test_ccv_08_passes_when_display_name_present():
    result = CcvResult()
    check_ccv_08_display_name_for_verified([verified_entry()], result)
    assert not any(v.rule == "CCV-08" for v in result.violations)


def test_ccv_08_warning_when_display_name_missing():
    result = CcvResult()
    entry = verified_entry()
    del entry["display_plugin_name"]
    check_ccv_08_display_name_for_verified([entry], result)
    assert any(v.rule == "CCV-08" and v.severity == "WARNING" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-09
# ---------------------------------------------------------------------------

def test_ccv_09_passes_when_url_present():
    result = CcvResult()
    row = {"package_key": "family/plugin", "publication_status": "PUBLICATION_READY", "canonical_url": "https://example.com"}
    check_ccv_09_publication_clean_has_canonical_url([row], result)
    assert not any(v.rule == "CCV-09" for v in result.violations)


def test_ccv_09_error_when_url_missing():
    result = CcvResult()
    row = {"package_key": "family/plugin", "publication_status": "PUBLICATION_READY"}
    check_ccv_09_publication_clean_has_canonical_url([row], result)
    assert any(v.rule == "CCV-09" and v.severity == "ERROR" for v in result.violations)


def test_ccv_09_skips_non_publication_rows():
    result = CcvResult()
    row = {"package_key": "family/plugin", "publication_status": "BLOCKED"}
    check_ccv_09_publication_clean_has_canonical_url([row], result)
    assert not any(v.rule == "CCV-09" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-10 / CCV-11 / CCV-12
# ---------------------------------------------------------------------------

def test_ccv_10_passes_when_program_cs_exists(tmp_path):
    (tmp_path / "Program.cs").write_text("// test")
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_10_pass_package_has_program_cs(ov, tmp_path, result)
    assert not any(v.rule == "CCV-10" for v in result.violations)


def test_ccv_10_error_when_program_cs_missing(tmp_path):
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_10_pass_package_has_program_cs(ov, tmp_path, result)
    assert any(v.rule == "CCV-10" and v.severity == "ERROR" for v in result.violations)


def test_ccv_10_no_check_when_verdict_fail(tmp_path):
    result = CcvResult()
    ov = {"verdict": "FAIL"}
    check_ccv_10_pass_package_has_program_cs(ov, tmp_path, result)
    assert not any(v.rule == "CCV-10" for v in result.violations)


def test_ccv_11_error_when_csproj_missing(tmp_path):
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_11_pass_package_has_csproj(ov, tmp_path, result)
    assert any(v.rule == "CCV-11" and v.severity == "ERROR" for v in result.violations)


def test_ccv_11_passes_when_csproj_exists(tmp_path):
    (tmp_path / "plugin.csproj").write_text("<Project/>")
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_11_pass_package_has_csproj(ov, tmp_path, result)
    assert not any(v.rule == "CCV-11" for v in result.violations)


def test_ccv_12_warning_when_no_logs(tmp_path):
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_12_pass_package_has_logs(ov, tmp_path, result)
    assert any(v.rule == "CCV-12" and v.severity == "WARNING" for v in result.violations)


def test_ccv_12_passes_when_log_exists(tmp_path):
    (tmp_path / "build.log").write_text("build ok")
    result = CcvResult()
    ov = {"verdict": "PASS", "package_key": "family/plugin"}
    check_ccv_12_pass_package_has_logs(ov, tmp_path, result)
    assert not any(v.rule == "CCV-12" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-13
# ---------------------------------------------------------------------------

def test_ccv_13_error_when_legacy_alias_in_clean_matrix():
    result = CcvResult()
    registry = [{"plugin_slug": "canonical-slug", "family": "imaging", "legacy_aliases": ["compress-image"]}]
    matrix = [{"package_key": "imaging/compress-image", "publication_status": "PUBLICATION_READY"}]
    check_ccv_13_no_legacy_alias_as_publication_candidate(matrix, registry, result)
    assert any(v.rule == "CCV-13" and v.severity == "ERROR" for v in result.violations)


def test_ccv_13_passes_when_canonical_slug_in_matrix():
    result = CcvResult()
    registry = [{"plugin_slug": "image-compressor", "family": "imaging", "legacy_aliases": ["compress-image"]}]
    matrix = [{"package_key": "imaging/image-compressor", "publication_status": "PUBLICATION_READY"}]
    check_ccv_13_no_legacy_alias_as_publication_candidate(matrix, registry, result)
    assert not any(v.rule == "CCV-13" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-14
# ---------------------------------------------------------------------------

def test_ccv_14_error_when_no_canonical_url_column():
    result = CcvResult()
    rows = [{"package_key": "a/b", "publication_status": "PUBLICATION_READY"}]
    check_ccv_14_matrix_has_canonical_url_column(rows, result)
    assert any(v.rule == "CCV-14" and v.severity == "ERROR" for v in result.violations)


def test_ccv_14_passes_when_all_rows_have_url():
    result = CcvResult()
    rows = [{"package_key": "a/b", "canonical_url": "https://example.com"}]
    check_ccv_14_matrix_has_canonical_url_column(rows, result)
    assert not any(v.rule == "CCV-14" for v in result.violations)


def test_ccv_14_warning_when_partial_urls():
    result = CcvResult()
    rows = [
        {"package_key": "a/b", "canonical_url": "https://example.com"},
        {"package_key": "c/d"},  # missing url
    ]
    check_ccv_14_matrix_has_canonical_url_column(rows, result)
    assert any(v.rule == "CCV-14" and v.severity == "WARNING" for v in result.violations)


def test_ccv_14_no_violation_for_empty_matrix():
    result = CcvResult()
    check_ccv_14_matrix_has_canonical_url_column([], result)
    assert not any(v.rule == "CCV-14" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-15
# ---------------------------------------------------------------------------

def test_ccv_15_passes_when_program_cs_found(tmp_path):
    pkg_dir = tmp_path / "imaging" / "image-compressor"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "Program.cs").write_text("// test")
    result = CcvResult()
    row = {"package_key": "imaging/image-compressor", "publication_status": "PUBLICATION_READY",
           "canonical_url": "https://example.com"}
    check_ccv_15_publication_ready_has_package_proof([row], [tmp_path], result)
    assert not any(v.rule == "CCV-15" for v in result.violations)


def test_ccv_15_error_when_program_cs_missing(tmp_path):
    pkg_dir = tmp_path / "imaging" / "image-compressor"
    pkg_dir.mkdir(parents=True)
    # No Program.cs — only metadata
    (pkg_dir / "source-provenance.json").write_text("{}")
    result = CcvResult()
    row = {"package_key": "imaging/image-compressor", "publication_status": "PUBLICATION_READY"}
    check_ccv_15_publication_ready_has_package_proof([row], [tmp_path], result)
    assert any(v.rule == "CCV-15" and v.severity == "ERROR" for v in result.violations)


def test_ccv_15_skips_non_publication_rows(tmp_path):
    result = CcvResult()
    row = {"package_key": "imaging/image-compressor", "publication_status": "BLOCKED"}
    check_ccv_15_publication_ready_has_package_proof([row], [tmp_path], result)
    assert not any(v.rule == "CCV-15" for v in result.violations)


def test_ccv_15_skips_when_no_pkg_base_dirs():
    result = CcvResult()
    row = {"package_key": "imaging/image-compressor", "publication_status": "PUBLICATION_READY"}
    check_ccv_15_publication_ready_has_package_proof([row], None, result)
    assert not any(v.rule == "CCV-15" for v in result.violations)


def test_ccv_15_checks_multiple_base_dirs(tmp_path):
    base1 = tmp_path / "wave8"
    base2 = tmp_path / "wave9"
    pkg_dir = base2 / "imaging" / "image-compressor"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "Program.cs").write_text("// test")
    result = CcvResult()
    row = {"package_key": "imaging/image-compressor", "publication_status": "PUBLICATION_READY"}
    check_ccv_15_publication_ready_has_package_proof([row], [base1, base2], result)
    assert not any(v.rule == "CCV-15" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-16
# ---------------------------------------------------------------------------

def test_ccv_16_passes_when_counts_match():
    result = CcvResult()
    closeout = complete_closeout(registry_total=70)
    check_ccv_16_registry_count_matches_claimed(closeout, 70, result)
    assert not any(v.rule == "CCV-16" for v in result.violations)


def test_ccv_16_error_when_counts_mismatch():
    result = CcvResult()
    closeout = complete_closeout(registry_total=72)
    check_ccv_16_registry_count_matches_claimed(closeout, 70, result)
    assert any(v.rule == "CCV-16" and v.severity == "ERROR" for v in result.violations)


def test_ccv_16_skips_when_no_claimed_count():
    result = CcvResult()
    check_ccv_16_registry_count_matches_claimed(complete_closeout(), 70, result)
    assert not any(v.rule == "CCV-16" for v in result.violations)


def test_ccv_16_skips_when_no_actual_count():
    result = CcvResult()
    closeout = complete_closeout(registry_total=70)
    check_ccv_16_registry_count_matches_claimed(closeout, None, result)
    assert not any(v.rule == "CCV-16" for v in result.violations)


def test_ccv_16_uses_total_registry_entries_key():
    result = CcvResult()
    closeout = complete_closeout(total_registry_entries=70)
    check_ccv_16_registry_count_matches_claimed(closeout, 70, result)
    assert not any(v.rule == "CCV-16" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-17
# ---------------------------------------------------------------------------

def test_ccv_17_no_violation_when_no_errors():
    result = CcvResult()
    check_ccv_17_no_errors_with_complete_verdict(complete_closeout(), result)
    assert not any(v.rule == "CCV-17" for v in result.violations)


def test_ccv_17_error_when_complete_verdict_with_existing_errors():
    result = CcvResult()
    # Inject a prior ERROR violation
    result.violations.append(CcvViolation("CCV-02", "ERROR", "lanes pending", ""))
    check_ccv_17_no_errors_with_complete_verdict(complete_closeout(), result)
    assert any(v.rule == "CCV-17" and v.severity == "ERROR" for v in result.violations)


def test_ccv_17_no_check_when_verdict_pending():
    result = CcvResult()
    result.violations.append(CcvViolation("CCV-02", "ERROR", "lanes pending", ""))
    check_ccv_17_no_errors_with_complete_verdict(pending_closeout(), result)
    assert not any(v.rule == "CCV-17" for v in result.violations)


def test_ccv_17_no_violation_when_only_warnings():
    result = CcvResult()
    result.violations.append(CcvViolation("CCV-08", "WARNING", "display name missing", ""))
    check_ccv_17_no_errors_with_complete_verdict(complete_closeout(), result)
    assert not any(v.rule == "CCV-17" for v in result.violations)


# ---------------------------------------------------------------------------
# CCV-18
# ---------------------------------------------------------------------------

def test_ccv_18_passes_when_entries_positive():
    result = CcvResult()
    closeout = complete_closeout(evidence_bundle={"objective": "COMPLETE", "entries": 42})
    check_ccv_18_bundle_entry_count_positive(closeout, result)
    assert not any(v.rule == "CCV-18" for v in result.violations)


def test_ccv_18_error_when_entries_zero():
    result = CcvResult()
    closeout = complete_closeout(evidence_bundle={"objective": "COMPLETE", "entries": 0})
    check_ccv_18_bundle_entry_count_positive(closeout, result)
    assert any(v.rule == "CCV-18" and v.severity == "ERROR" for v in result.violations)


def test_ccv_18_error_when_entries_missing():
    result = CcvResult()
    closeout = complete_closeout(evidence_bundle={"objective": "COMPLETE"})
    check_ccv_18_bundle_entry_count_positive(closeout, result)
    assert any(v.rule == "CCV-18" and v.severity == "ERROR" for v in result.violations)


def test_ccv_18_no_check_when_verdict_pending():
    result = CcvResult()
    closeout = pending_closeout(evidence_bundle={"objective": "PENDING", "entries": 0})
    check_ccv_18_bundle_entry_count_positive(closeout, result)
    assert not any(v.rule == "CCV-18" for v in result.violations)


def test_ccv_18_no_violation_when_bundle_not_dict():
    result = CcvResult()
    # If bundle is a plain string, CCV-18 should not crash or produce a violation
    closeout = complete_closeout(evidence_bundle="COMPLETE — bundle written")
    check_ccv_18_bundle_entry_count_positive(closeout, result)
    assert not any(v.rule == "CCV-18" for v in result.violations)


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

def test_aggregate_runner_clean_state(tmp_path):
    (tmp_path / "pytest-stdout.txt").write_text("100 passed")
    (tmp_path / "git-status.txt").write_text("nothing to commit")
    closeout = complete_closeout()
    lanes = {"lanes": [{"lane": "A", "status": "COMPLETE"}]}
    cards = [{"id": "TC-01", "status": "COMPLETE"}]
    result = run_closeout_consistency_validators(
        closeout=closeout,
        lane_ledger=lanes,
        taskcards=cards,
        report_dir=tmp_path,
    )
    assert result.passes
    assert result.error_count == 0


def test_aggregate_runner_detects_pending_lanes():
    closeout = complete_closeout()
    lanes = {"lanes": [{"lane": "A", "status": "PENDING"}]}
    cards = [{"id": "TC-01", "status": "COMPLETE"}]
    result = run_closeout_consistency_validators(
        closeout=closeout,
        lane_ledger=lanes,
        taskcards=cards,
    )
    assert not result.passes
    assert any(v.rule == "CCV-02" for v in result.violations)


def test_ccv_result_to_dict():
    result = CcvResult()
    result.violations.append(CcvViolation("CCV-01", "ERROR", "test msg", "ctx"))
    d = result.to_dict()
    assert d["passes"] is False
    assert d["error_count"] == 1
    assert d["violations"][0]["rule"] == "CCV-01"
