"""
Wave 17 Validator Tests

Tests for:
- TCV-01..TCV-03: Taskcard Count Validators
- PEV-01..PEV-03: Pending Evidence Validators
- BAV-01..BAV-03: Bundle vs Attestation Validators
- PRC-01..PRC-02: PR Packet Count Validators
- PPL-01..PPL-03: Package Proof Log Validators
- FGS-01..FGS-02: Final Git Status Validators

Includes regression tests for Wave 16 defect patterns (W16-DEF-01..07).
"""

import io
import json
import os
import tempfile
import zipfile
import hashlib
import pytest

from src.plugin_examples.fixture_factory.taskcard_count_validator import (
    tcv_01_total_matches_array_length,
    tcv_02_complete_plus_pending_equals_total,
    tcv_03_pending_zero_at_sprint_close,
    run_all_tcv,
)
from src.plugin_examples.fixture_factory.pending_evidence_validator import (
    pev_01_no_pending_in_complete_evidence,
    pev_02_no_deferred_in_complete_evidence,
    pev_03_no_empty_evidence_on_complete,
    run_all_pev,
)
from src.plugin_examples.fixture_factory.bundle_attestation_validator import (
    bav_01_bundle_sha_matches_attestation,
    bav_02_bundle_entry_count_matches_attestation,
    bav_03_bundle_size_matches_attestation,
    run_all_bav,
)
from src.plugin_examples.fixture_factory.pr_packet_count_validator import (
    prc_01_bundle_pr_packet_count_gte_pclc_total,
    prc_02_each_pclc_package_has_pr_packet_in_bundle,
    run_all_prc,
)
from src.plugin_examples.fixture_factory.package_proof_log_validator import (
    ppl_01_restore_log_present,
    ppl_02_build_log_present,
    ppl_03_run_log_present,
    run_all_ppl,
)
from src.plugin_examples.fixture_factory.final_git_status_validator import (
    fgs_01_final_git_status_present_in_bundle,
    fgs_02_no_pfx_in_final_git_status,
    run_all_fgs,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_taskcard(id_: str, status: str, evidence: str) -> dict:
    return {"id": id_, "status": status, "evidence": evidence}


def _make_bundle(entries: dict[str, bytes]) -> bytes:
    """Create an in-memory ZIP with given entries {path: content}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _write_bundle(tmp_path: str, entries: dict[str, bytes]) -> str:
    """Write a ZIP bundle to disk and return path."""
    path = os.path.join(tmp_path, "test-bundle.zip")
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return path


# ===========================================================================
# TCV Tests
# ===========================================================================

class TestTCV01:
    def test_pass_when_total_matches(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "done"), _make_taskcard("T2", "COMPLETE", "done")]
        closeout = {"taskcards": {"total": 2, "complete": 2, "pending": 0}}
        r = tcv_01_total_matches_array_length(closeout, tcs)
        assert r.status == "PASS"

    def test_fail_when_total_overcounts(self):
        """Regression: W16-DEF-01 — pre-bundle-closeout claims 42, actual 41."""
        tcs = [_make_taskcard(f"T{i}", "COMPLETE", "done") for i in range(41)]
        closeout = {"taskcards": {"total": 42, "complete": 42, "pending": 0}}
        r = tcv_01_total_matches_array_length(closeout, tcs)
        assert r.status == "FAIL"
        assert "42" in r.message
        assert "41" in r.message

    def test_fail_when_total_missing(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "done")]
        closeout = {"taskcards": {"complete": 1, "pending": 0}}
        r = tcv_01_total_matches_array_length(closeout, tcs)
        assert r.status == "FAIL"
        assert "missing" in r.message


class TestTCV02:
    def test_pass_when_balanced(self):
        closeout = {"taskcards": {"total": 10, "complete": 8, "pending": 2}}
        r = tcv_02_complete_plus_pending_equals_total(closeout)
        assert r.status == "PASS"

    def test_fail_when_unbalanced(self):
        closeout = {"taskcards": {"total": 10, "complete": 9, "pending": 2}}
        r = tcv_02_complete_plus_pending_equals_total(closeout)
        assert r.status == "FAIL"

    def test_fail_when_field_missing(self):
        closeout = {"taskcards": {"total": 10, "complete": 10}}
        r = tcv_02_complete_plus_pending_equals_total(closeout)
        assert r.status == "FAIL"


class TestTCV03:
    def test_pass_when_pending_zero(self):
        closeout = {"taskcards": {"total": 5, "complete": 5, "pending": 0}}
        r = tcv_03_pending_zero_at_sprint_close(closeout)
        assert r.status == "PASS"

    def test_fail_when_pending_nonzero(self):
        closeout = {"taskcards": {"total": 5, "complete": 4, "pending": 1}}
        r = tcv_03_pending_zero_at_sprint_close(closeout)
        assert r.status == "FAIL"

    def test_fail_when_pending_missing(self):
        closeout = {"taskcards": {"total": 5, "complete": 5}}
        r = tcv_03_pending_zero_at_sprint_close(closeout)
        assert r.status == "FAIL"


# ===========================================================================
# PEV Tests
# ===========================================================================

class TestPEV01:
    def test_pass_when_no_pending_in_complete(self):
        tcs = [
            _make_taskcard("T1", "COMPLETE", "done — commit abc123"),
            _make_taskcard("T2", "COMPLETE", "output-validation.json PASS"),
        ]
        r = pev_01_no_pending_in_complete_evidence(tcs)
        assert r.status == "PASS"

    def test_fail_when_pending_in_complete_evidence(self):
        """Regression: W16-DEF-02 — W16-LF-06 evidence = 'PENDING — chore commit...'"""
        tcs = [
            _make_taskcard("W16-LF-06", "COMPLETE", "PENDING — chore commit to be created after bundle freeze"),
        ]
        r = pev_01_no_pending_in_complete_evidence(tcs)
        assert r.status == "FAIL"
        assert "W16-LF-06" in str(r.details)

    def test_pass_when_pending_status_not_complete(self):
        """PENDING in evidence is only checked for COMPLETE taskcards."""
        tcs = [_make_taskcard("T1", "PENDING", "PENDING — not started")]
        r = pev_01_no_pending_in_complete_evidence(tcs)
        assert r.status == "PASS"

    def test_multiple_violations(self):
        tcs = [
            _make_taskcard("T1", "COMPLETE", "PENDING x"),
            _make_taskcard("T2", "COMPLETE", "PENDING y"),
            _make_taskcard("T3", "COMPLETE", "done"),
        ]
        r = pev_01_no_pending_in_complete_evidence(tcs)
        assert r.status == "FAIL"
        assert len(r.details["violations"]) == 2


class TestPEV02:
    def test_pass_when_no_deferred_in_complete(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "done fully")]
        r = pev_02_no_deferred_in_complete_evidence(tcs)
        assert r.status == "PASS"

    def test_fail_when_deferred_in_complete_evidence(self):
        """Regression: W16-DEF-02 — W16-L0-07 evidence = 'DEFERRED TO AFTER BUNDLE FREEZE'"""
        tcs = [
            _make_taskcard("W16-L0-07", "COMPLETE", "DEFERRED TO AFTER BUNDLE FREEZE — written in chore commit"),
        ]
        r = pev_02_no_deferred_in_complete_evidence(tcs)
        assert r.status == "FAIL"
        assert "W16-L0-07" in str(r.details)


class TestPEV03:
    def test_pass_when_all_complete_have_evidence(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "evidence present")]
        r = pev_03_no_empty_evidence_on_complete(tcs)
        assert r.status == "PASS"

    def test_fail_when_empty_evidence_on_complete(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "")]
        r = pev_03_no_empty_evidence_on_complete(tcs)
        assert r.status == "FAIL"

    def test_pass_when_pending_has_empty_evidence(self):
        tcs = [_make_taskcard("T1", "PENDING", "")]
        r = pev_03_no_empty_evidence_on_complete(tcs)
        assert r.status == "PASS"


# ===========================================================================
# BAV Tests
# ===========================================================================

class TestBAV:
    @pytest.fixture
    def bundle_file(self, tmp_path):
        path = str(tmp_path)
        entries = {
            "sprint/taskcards/taskcards.json": b'{"total":1}',
            "sprint/preflight/git-status.txt": b"M file.py",
        }
        bundle_path = _write_bundle(path, entries)
        sha = hashlib.sha256(open(bundle_path, "rb").read()).hexdigest()
        size = os.path.getsize(bundle_path)
        entry_count = 2
        attestation = {"sha256": sha, "size_bytes": size, "entry_count": entry_count}
        return bundle_path, attestation

    def test_bav_01_pass(self, bundle_file):
        path, att = bundle_file
        r = bav_01_bundle_sha_matches_attestation(path, att)
        assert r.status == "PASS"

    def test_bav_01_fail_wrong_sha(self, bundle_file):
        path, att = bundle_file
        att_wrong = dict(att, sha256="0" * 64)
        r = bav_01_bundle_sha_matches_attestation(path, att_wrong)
        assert r.status == "FAIL"
        assert "does not match" in r.message

    def test_bav_02_pass(self, bundle_file):
        path, att = bundle_file
        r = bav_02_bundle_entry_count_matches_attestation(path, att)
        assert r.status == "PASS"

    def test_bav_02_fail_wrong_count(self, bundle_file):
        path, att = bundle_file
        att_wrong = dict(att, entry_count=99)
        r = bav_02_bundle_entry_count_matches_attestation(path, att_wrong)
        assert r.status == "FAIL"

    def test_bav_03_pass(self, bundle_file):
        path, att = bundle_file
        r = bav_03_bundle_size_matches_attestation(path, att)
        assert r.status == "PASS"

    def test_bav_03_fail_wrong_size(self, bundle_file):
        path, att = bundle_file
        att_wrong = dict(att, size_bytes=999999)
        r = bav_03_bundle_size_matches_attestation(path, att_wrong)
        assert r.status == "FAIL"

    def test_bav_01_missing_file(self, tmp_path):
        r = bav_01_bundle_sha_matches_attestation(
            str(tmp_path / "nonexistent.zip"), {"sha256": "abc"}
        )
        assert r.status == "FAIL"


# ===========================================================================
# PRC Tests
# ===========================================================================

class TestPRC:
    @pytest.fixture
    def bundle_with_6_packets(self, tmp_path):
        entries = {
            "sprint/publication/pr-packets/html/convert-html-to-markdown/pr-packet.json": b"{}",
            "sprint/publication/pr-packets/html/merge-html/pr-packet.json": b"{}",
            "sprint/publication/pr-packets/gis/convert-gis-data/pr-packet.json": b"{}",
            "sprint/publication/pr-packets/tasks/read-project-data/pr-packet.json": b"{}",
            "sprint/publication/pr-packets/html/convert-html-to-xps/pr-packet.json": b"{}",
            "sprint/publication/pr-packets/psd/convert-psd-to-png/pr-packet.json": b"{}",
        }
        return _write_bundle(str(tmp_path), entries)

    def test_prc_01_pass_when_enough_packets(self, bundle_with_6_packets):
        r = prc_01_bundle_pr_packet_count_gte_pclc_total(bundle_with_6_packets, 6)
        assert r.status == "PASS"

    def test_prc_01_fail_w16_defect(self, bundle_with_6_packets):
        """Regression: W16-DEF-03 — bundle has 6 packets but pclc_total=20."""
        r = prc_01_bundle_pr_packet_count_gte_pclc_total(bundle_with_6_packets, 20)
        assert r.status == "FAIL"
        assert "6" in r.message
        assert "20" in r.message

    def test_prc_02_pass_when_all_present(self, bundle_with_6_packets):
        packages = [
            {"family": "html", "slug": "convert-html-to-markdown"},
            {"family": "html", "slug": "merge-html"},
            {"family": "gis", "slug": "convert-gis-data"},
        ]
        r = prc_02_each_pclc_package_has_pr_packet_in_bundle(bundle_with_6_packets, packages)
        assert r.status == "PASS"

    def test_prc_02_fail_when_package_missing(self, bundle_with_6_packets):
        packages = [
            {"family": "svg", "slug": "vectorizer"},  # not in bundle
            {"family": "html", "slug": "convert-html-to-markdown"},
        ]
        r = prc_02_each_pclc_package_has_pr_packet_in_bundle(bundle_with_6_packets, packages)
        assert r.status == "FAIL"
        assert "svg/vectorizer" in str(r.details)


# ===========================================================================
# PPL Tests
# ===========================================================================

class TestPPL:
    @pytest.fixture
    def bundle_with_logs(self, tmp_path):
        entries = {
            "sprint/wave17-dryrun/examples/threed/convert-3d-model/restore.log": b"Restored.",
            "sprint/wave17-dryrun/examples/threed/convert-3d-model/build.log": b"Build succeeded.",
            "sprint/wave17-dryrun/examples/threed/convert-3d-model/run.log": b"3D model saved.",
        }
        return _write_bundle(str(tmp_path), entries)

    @pytest.fixture
    def bundle_without_logs(self, tmp_path):
        entries = {
            "sprint/wave16-dryrun/examples/html/convert-html-to-markdown/Program.cs": b"using Aspose.HTML;",
            "sprint/wave16-dryrun/examples/html/convert-html-to-markdown/output-validation.json": b'{"status":"PASS"}',
        }
        return _write_bundle(str(tmp_path), entries)

    def test_ppl_01_pass(self, bundle_with_logs):
        pkgs = [{"family": "threed", "slug": "convert-3d-model"}]
        r = ppl_01_restore_log_present(bundle_with_logs, pkgs)
        assert r.status == "PASS"

    def test_ppl_01_fail_w16_defect(self, bundle_without_logs):
        """Regression: W16-DEF-04 — no restore.log for proven packages."""
        pkgs = [{"family": "html", "slug": "convert-html-to-markdown"}]
        r = ppl_01_restore_log_present(bundle_without_logs, pkgs)
        assert r.status == "FAIL"
        assert "html/convert-html-to-markdown" in str(r.details)

    def test_ppl_02_pass(self, bundle_with_logs):
        pkgs = [{"family": "threed", "slug": "convert-3d-model"}]
        r = ppl_02_build_log_present(bundle_with_logs, pkgs)
        assert r.status == "PASS"

    def test_ppl_02_fail(self, bundle_without_logs):
        pkgs = [{"family": "html", "slug": "convert-html-to-markdown"}]
        r = ppl_02_build_log_present(bundle_without_logs, pkgs)
        assert r.status == "FAIL"

    def test_ppl_03_pass(self, bundle_with_logs):
        pkgs = [{"family": "threed", "slug": "convert-3d-model"}]
        r = ppl_03_run_log_present(bundle_with_logs, pkgs)
        assert r.status == "PASS"

    def test_ppl_03_fail(self, bundle_without_logs):
        pkgs = [{"family": "html", "slug": "convert-html-to-markdown"}]
        r = ppl_03_run_log_present(bundle_without_logs, pkgs)
        assert r.status == "FAIL"


# ===========================================================================
# FGS Tests
# ===========================================================================

class TestFGS:
    @pytest.fixture
    def bundle_with_final_status(self, tmp_path):
        entries = {
            "sprint/preflight/git-status.txt": b"M src/foo.py",
            "sprint/final/git-status-final.txt": b"M reports/foo.json",
        }
        return _write_bundle(str(tmp_path), entries)

    @pytest.fixture
    def bundle_preflight_only(self, tmp_path):
        """Regression: W16-DEF-05 — only preflight git-status, no final."""
        entries = {
            "sprint/preflight/git-status.txt": b"M src/foo.py\n?? test-cert.pfx",
        }
        return _write_bundle(str(tmp_path), entries)

    @pytest.fixture
    def bundle_with_pfx_in_final(self, tmp_path):
        entries = {
            "sprint/preflight/git-status.txt": b"M src/foo.py",
            "sprint/final/git-status-final.txt": b"M reports/foo.json\n?? test-cert.pfx",
        }
        return _write_bundle(str(tmp_path), entries)

    def test_fgs_01_pass(self, bundle_with_final_status):
        r = fgs_01_final_git_status_present_in_bundle(bundle_with_final_status)
        assert r.status == "PASS"

    def test_fgs_01_fail_w16_defect(self, bundle_preflight_only):
        """Regression: W16-DEF-05 — no final git-status in bundle."""
        r = fgs_01_final_git_status_present_in_bundle(bundle_preflight_only)
        assert r.status == "FAIL"
        assert "only preflight" in r.message.lower() or "no final" in r.message.lower()

    def test_fgs_02_pass_no_pfx(self, bundle_with_final_status):
        r = fgs_02_no_pfx_in_final_git_status(bundle_with_final_status)
        assert r.status == "PASS"

    def test_fgs_02_fail_pfx_in_final(self, bundle_with_pfx_in_final):
        r = fgs_02_no_pfx_in_final_git_status(bundle_with_pfx_in_final)
        assert r.status == "FAIL"
        assert ".pfx" in str(r.details)

    def test_fgs_02_fail_when_no_final_status(self, bundle_preflight_only):
        r = fgs_02_no_pfx_in_final_git_status(bundle_preflight_only)
        assert r.status == "FAIL"


# ===========================================================================
# Run_all integration tests
# ===========================================================================

class TestRunAll:
    def test_run_all_tcv_pass(self):
        tcs = [_make_taskcard(f"T{i}", "COMPLETE", "done") for i in range(5)]
        closeout = {"taskcards": {"total": 5, "complete": 5, "pending": 0}}
        results = run_all_tcv(closeout, tcs)
        assert len(results) == 3
        assert all(r.status == "PASS" for r in results)

    def test_run_all_pev_pass(self):
        tcs = [_make_taskcard("T1", "COMPLETE", "commit abc123")]
        results = run_all_pev(tcs)
        assert len(results) == 3
        assert all(r.status == "PASS" for r in results)

    def test_run_all_pev_catches_w16_defects(self):
        """Regression: W16-DEF-02 — multiple PENDING/DEFERRED violations."""
        tcs = [
            _make_taskcard("W16-LF-06", "COMPLETE", "PENDING — chore commit to be created after bundle freeze"),
            _make_taskcard("W16-L0-07", "COMPLETE", "DEFERRED TO AFTER BUNDLE FREEZE"),
            _make_taskcard("W16-L0-06", "COMPLETE", "DEFERRED TO AFTER TASKCARDS COMPLETE"),
        ]
        results = run_all_pev(tcs)
        fails = [r for r in results if r.status == "FAIL"]
        assert len(fails) >= 2  # PEV-01 and PEV-02 should fail
