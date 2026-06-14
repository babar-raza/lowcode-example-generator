"""
Tests for EAV (Evidence Authority Validators) — Wave 16
Regression tests against Wave 15 defect patterns.
"""

import hashlib
import io
import json
import os
import tempfile
import zipfile

import pytest

from src.plugin_examples.fixture_factory.evidence_authority_validators import (
    REQUIRED_ATTESTATION_FIELDS,
    eav_01_iv_not_final_pass_with_pending_taskcards,
    eav_02_ar_not_final_pass_with_pending_taskcards,
    eav_03_external_sidecar_exists_and_valid,
    eav_04_external_attestation_exists_and_complete,
    eav_05_prebundle_closeout_not_claiming_final_authority,
    eav_06_bundle_entry_count_matches_attestation,
    run_all_eav,
)

# ============================================================
# Fixtures
# ============================================================


def make_taskcards(complete_ids=None, pending_ids=None):
    taskcards = []
    for tid in complete_ids or []:
        taskcards.append({"id": tid, "status": "COMPLETE", "evidence": "done"})
    for tid in pending_ids or []:
        taskcards.append({"id": tid, "status": "PENDING", "evidence": ""})
    return {"taskcards": taskcards}


def make_iv(verdict="IV_PASS", is_final=True):
    return {"verdict": verdict, "is_final": is_final}


def make_ar(verdict="ADVERSARIAL_REVIEW_PASS", review_type="FINAL"):
    return {"verdict": verdict, "review_type": review_type}


def make_bundle_with_files(files: dict[str, str]) -> bytes:
    """Create an in-memory ZIP with the given filename->content mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def write_bundle(tmp_dir, files: dict[str, str]) -> str:
    bundle_path = os.path.join(tmp_dir, "bundle.zip")
    data = make_bundle_with_files(files)
    with open(bundle_path, "wb") as f:
        f.write(data)
    return bundle_path


def write_sidecar(tmp_dir, bundle_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(bundle_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    digest = sha256.hexdigest()
    sidecar_path = os.path.join(tmp_dir, "bundle.sha256")
    with open(sidecar_path, "w") as f:
        f.write(f"{digest}  bundle.zip\n")
    return sidecar_path


def write_attestation(tmp_dir, bundle_path: str, sidecar_path: str, entry_count: int = 1, protocol: str = "v2") -> str:
    sha256 = hashlib.sha256()
    with open(bundle_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    digest = sha256.hexdigest()
    size = os.path.getsize(bundle_path)
    attestation = {
        "path": bundle_path,
        "sha256": digest,
        "size_bytes": size,
        "entry_count": entry_count,
        "feat_commit": "abc1234",
        "sidecar_path": sidecar_path,
        "protocol_version": protocol,
    }
    att_path = os.path.join(tmp_dir, "attestation.json")
    with open(att_path, "w") as f:
        json.dump(attestation, f)
    return att_path


# ============================================================
# EAV-01
# ============================================================


class TestEAV01:
    def test_pass_iv_pass_no_pending(self):
        result = eav_01_iv_not_final_pass_with_pending_taskcards(
            make_iv("IV_PASS"), make_taskcards(complete_ids=["TC-01", "TC-02"])
        )
        assert result.passed
        assert result.rule_id == "EAV-01"

    def test_fail_wave15_pattern_iv_pass_with_pending(self):
        """Regression: Wave 15 had IV_PASS with 6 PENDING taskcards in bundle."""
        iv = make_iv("IV_PASS")
        tc = make_taskcards(
            complete_ids=["W15-L0-01", "W15-LI-01", "W15-LI-02", "W15-LI-03"],
            pending_ids=["W15-LI-04", "W15-LI-05", "W15-LI-06", "W15-LI-07", "W15-LI-08", "W15-LI-09"],
        )
        result = eav_01_iv_not_final_pass_with_pending_taskcards(iv, tc)
        assert not result.passed
        assert "W15-LI-04" in result.detail["pending_taskcards"]
        assert len(result.detail["pending_taskcards"]) == 6

    def test_pass_iv_partial_with_pending(self):
        """IV marked as non-final (PARTIAL) should not trigger EAV-01."""
        iv = make_iv("IV_PASS", is_final=False)
        tc = make_taskcards(pending_ids=["TC-01"])
        result = eav_01_iv_not_final_pass_with_pending_taskcards(iv, tc)
        assert result.passed

    def test_pass_iv_fail_not_applicable(self):
        result = eav_01_iv_not_final_pass_with_pending_taskcards(
            make_iv("IV_FAIL"), make_taskcards(pending_ids=["TC-01"])
        )
        assert result.passed  # EAV-01 only fires when IV_PASS


# ============================================================
# EAV-02
# ============================================================


class TestEAV02:
    def test_pass_ar_pass_no_pending(self):
        result = eav_02_ar_not_final_pass_with_pending_taskcards(make_ar(), make_taskcards(complete_ids=["TC-01"]))
        assert result.passed

    def test_fail_ar_final_pass_with_pending(self):
        """Regression: Wave 15 adversarial review FINAL PASS with pending closeout taskcards."""
        ar = make_ar("ADVERSARIAL_REVIEW_PASS", "FINAL")
        tc = make_taskcards(pending_ids=["W15-LI-05", "W15-LI-06", "W15-LI-07"])
        result = eav_02_ar_not_final_pass_with_pending_taskcards(ar, tc)
        assert not result.passed
        assert len(result.detail["pending_taskcards"]) == 3

    def test_pass_ar_not_final(self):
        ar = make_ar("ADVERSARIAL_REVIEW_PASS", "INTERIM")
        tc = make_taskcards(pending_ids=["TC-01"])
        result = eav_02_ar_not_final_pass_with_pending_taskcards(ar, tc)
        assert result.passed


# ============================================================
# EAV-03
# ============================================================


class TestEAV03:
    def test_pass_sidecar_matches_bundle(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"file.txt": "hello"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        result = eav_03_external_sidecar_exists_and_valid(sidecar_path, bundle_path)
        assert result.passed

    def test_fail_sidecar_missing(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"file.txt": "hello"})
        result = eav_03_external_sidecar_exists_and_valid(str(tmp_path / "nonexistent.sha256"), bundle_path)
        assert not result.passed

    def test_fail_sidecar_sha_mismatch(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"file.txt": "hello"})
        sidecar_path = str(tmp_path / "bundle.sha256")
        with open(sidecar_path, "w") as f:
            # Write a known-wrong SHA (Wave 14 constants as regression)
            f.write("9a34a24e0000000000000000000000000000000000000000000000000000000  bundle.zip\n")
        result = eav_03_external_sidecar_exists_and_valid(sidecar_path, bundle_path)
        assert not result.passed
        assert "mismatch" in result.message.lower()

    def test_fail_bundle_missing(self, tmp_path):
        sidecar_path = str(tmp_path / "bundle.sha256")
        with open(sidecar_path, "w") as f:
            f.write("abc123  bundle.zip\n")
        result = eav_03_external_sidecar_exists_and_valid(sidecar_path, str(tmp_path / "nonexistent.zip"))
        assert not result.passed


# ============================================================
# EAV-04
# ============================================================


class TestEAV04:
    def test_pass_complete_attestation(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"f.txt": "x"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=1)
        result = eav_04_external_attestation_exists_and_complete(att_path)
        assert result.passed

    def test_fail_attestation_missing(self, tmp_path):
        result = eav_04_external_attestation_exists_and_complete(str(tmp_path / "nonexistent.json"))
        assert not result.passed

    def test_fail_missing_fields(self, tmp_path):
        att_path = str(tmp_path / "att.json")
        with open(att_path, "w") as f:
            json.dump({"sha256": "abc", "protocol_version": "v2"}, f)
        result = eav_04_external_attestation_exists_and_complete(att_path)
        assert not result.passed
        assert "missing" in result.message.lower()

    def test_fail_wrong_protocol_version(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"f.txt": "x"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=1, protocol="v1.1")
        result = eav_04_external_attestation_exists_and_complete(att_path)
        assert not result.passed
        assert "v1.1" in result.message


# ============================================================
# EAV-05
# ============================================================


class TestEAV05:
    def test_pass_no_closeout_in_bundle(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"evidence.txt": "data"})
        result = eav_05_prebundle_closeout_not_claiming_final_authority(bundle_path)
        assert result.passed

    def test_pass_prebundle_closeout_labeled_correctly(self, tmp_path):
        pre_closeout = json.dumps({"closeout_type": "PRE_BUNDLE_CLOSEOUT", "verdict": "SPRINT_IN_PROGRESS"})
        bundle_path = write_bundle(str(tmp_path), {"sprint/final/sprint-closeout.json": pre_closeout})
        result = eav_05_prebundle_closeout_not_claiming_final_authority(bundle_path)
        assert result.passed

    def test_fail_wave14_pattern_zip_contains_own_sha(self, tmp_path):
        """Regression: Wave 14 had closeout with final SHA inside the bundle."""
        # Wave 14 constants from regression fixtures
        closeout_with_sha = json.dumps(
            {
                "closeout_type": "FINAL",
                "verdict": "SPRINT_COMPLETE",
                "evidence_bundle": {
                    "sha256": "0cfddd35f4a013eff83e2d28266e90fe6c35f7e1a37ff82af7c78fe026fc4de4",
                    "size_bytes": 747902,
                },
            }
        )
        bundle_path = write_bundle(str(tmp_path), {"sprint/final/sprint-closeout.json": closeout_with_sha})
        result = eav_05_prebundle_closeout_not_claiming_final_authority(bundle_path)
        assert not result.passed
        assert "final sha authority" in result.message.lower()

    def test_fail_bundle_missing(self, tmp_path):
        result = eav_05_prebundle_closeout_not_claiming_final_authority(str(tmp_path / "nonexistent.zip"))
        assert not result.passed


# ============================================================
# EAV-06
# ============================================================


class TestEAV06:
    def test_pass_count_matches(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"a.txt": "1", "b.txt": "2"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=2)
        result = eav_06_bundle_entry_count_matches_attestation(bundle_path, att_path)
        assert result.passed

    def test_fail_count_mismatch(self, tmp_path):
        bundle_path = write_bundle(str(tmp_path), {"a.txt": "1", "b.txt": "2"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=50)
        result = eav_06_bundle_entry_count_matches_attestation(bundle_path, att_path)
        assert not result.passed
        assert "mismatch" in result.message.lower()

    def test_fail_wave15_bundle_count_drift(self, tmp_path):
        """Regression: Wave 15 bundle had 50 entries; attestation must match exactly."""
        # Simulate a bundle with 3 files but attestation claiming 50
        bundle_path = write_bundle(str(tmp_path), {f"f{i}.txt": "x" for i in range(3)})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=50)
        result = eav_06_bundle_entry_count_matches_attestation(bundle_path, att_path)
        assert not result.passed
        assert result.detail["bundle_entries"] == 3
        assert result.detail["attestation_entries"] == 50


# ============================================================
# run_all_eav integration
# ============================================================


class TestRunAllEAV:
    def test_all_pass_correct_scenario(self, tmp_path):
        # Build bundle with pre-bundle closeout (no final SHA)
        pre_closeout = json.dumps({"closeout_type": "PRE_BUNDLE_CLOSEOUT", "verdict": "SPRINT_IN_PROGRESS"})
        bundle_path = write_bundle(
            str(tmp_path),
            {
                "sprint/evidence.txt": "data",
                "sprint/final/pre-bundle-closeout.json": pre_closeout,
            },
        )
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=2)

        tc = make_taskcards(complete_ids=["TC-01", "TC-02"])
        iv = make_iv("IV_PASS")
        ar = make_ar()

        results = run_all_eav(iv, ar, tc, bundle_path, sidecar_path, att_path)
        assert all(r.passed for r in results), [r for r in results if not r.passed]
        assert len(results) == 6

    def test_wave15_defect_pattern_fails(self, tmp_path):
        """Simulate the exact Wave 15 defect: IV_PASS with pending taskcards in bundle."""
        bundle_path = write_bundle(str(tmp_path), {"evidence.txt": "data"})
        sidecar_path = write_sidecar(str(tmp_path), bundle_path)
        att_path = write_attestation(str(tmp_path), bundle_path, sidecar_path, entry_count=1)

        # Wave 15 exact defect state
        tc = make_taskcards(
            complete_ids=[f"W15-L{i}-01" for i in range(9)],
            pending_ids=["W15-LI-04", "W15-LI-05", "W15-LI-06", "W15-LI-07", "W15-LI-08", "W15-LI-09"],
        )
        iv = make_iv("IV_PASS", is_final=True)  # Final IV with pending taskcards
        ar = make_ar("ADVERSARIAL_REVIEW_PASS", "FINAL")  # Final AR with pending taskcards

        results = run_all_eav(iv, ar, tc, bundle_path, sidecar_path, att_path)
        failed = [r for r in results if not r.passed]
        # EAV-01 and EAV-02 must fail
        failed_ids = {r.rule_id for r in failed}
        assert "EAV-01" in failed_ids, "EAV-01 must fail for Wave 15 pattern"
        assert "EAV-02" in failed_ids, "EAV-02 must fail for Wave 15 pattern"
