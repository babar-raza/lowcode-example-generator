"""
Tests for Closeout-vs-Bundle (CVB) Validators — CVB-01..CVB-05

Regression fixtures derived from Wave 14 evidence integrity defects:
  W14-CONTRA-01: Bundled iv-results.json=IV_FAIL while closeout.iv.verdict=IV_PASS
  W14-CONTRA-02: Closeout claims sha256=9a34a24... but actual bundle sha256=0cfddd35...
  W14-CONTRA-03: Closeout claims size_bytes=747861 but actual bundle size=747902
  W14-CONTRA-04: IV re-run after bundle finalization — bundle captures stale IV_FAIL
  W14-CONTRA-05: Adversarial review did not check bundled iv-results.json vs closeout
"""

import pytest

from src.plugin_examples.fixture_factory.closeout_vs_bundle_validators import (
    cvb_01_bundled_iv_verdict_must_match_closeout,
    cvb_02_bundle_sha256_matches_closeout,
    cvb_03_bundle_size_matches_closeout,
    cvb_04_bundle_entry_count_matches_closeout,
    cvb_05_sidecar_sha_matches_bundle,
    run_all_cvb_validators,
)

# Wave 14 fixture constants (real values from the defect)
W14_ACTUAL_SHA = "0cfddd35f4a013eff83e2d28266e90fe6c35f7e1a37ff82af7c78fe026fc4de4"
W14_STALE_SHA = "9a34a24060d87a3368a05a3efc3b22def9bec82afef0528387fdd665d8f526b7"
W14_ACTUAL_SIZE = 747902
W14_STALE_SIZE = 747861
W14_ENTRIES = 51


# ─────────────────────────────────────────────────────────────────
# CVB-01: Bundled IV verdict must match closeout IV verdict
# ─────────────────────────────────────────────────────────────────


class TestCVB01:
    def test_pass_when_both_iv_pass(self):
        r = cvb_01_bundled_iv_verdict_must_match_closeout("IV_PASS", "IV_PASS")
        assert r["status"] == "PASS"

    def test_pass_when_both_none(self):
        r = cvb_01_bundled_iv_verdict_must_match_closeout(None, None)
        assert r["status"] == "PASS"

    def test_pass_when_bundled_iv_none(self):
        r = cvb_01_bundled_iv_verdict_must_match_closeout(None, "IV_PASS")
        assert r["status"] == "PASS"

    def test_pass_when_closeout_iv_none(self):
        r = cvb_01_bundled_iv_verdict_must_match_closeout("IV_PASS", None)
        assert r["status"] == "PASS"

    def test_fail_w14_contra_01_bundled_fail_closeout_pass(self):
        """Wave 14 W14-CONTRA-01 regression: bundled IV_FAIL with closeout IV_PASS."""
        r = cvb_01_bundled_iv_verdict_must_match_closeout("IV_FAIL", "IV_PASS")
        assert r["status"] == "FAIL"
        assert "CONTRADICTION" in r["message"]
        assert "IV_FAIL" in r["message"]
        assert "IV_PASS" in r["message"]
        assert "W14-CONTRA-01" in r["message"]

    def test_fail_bundled_fail_closeout_sprint_complete(self):
        """Bundled IV_FAIL with closeout claiming SPRINT_COMPLETE fails CVB-01."""
        r = cvb_01_bundled_iv_verdict_must_match_closeout("IV_FAIL", "IV_PASS", sprint_verdict="SPRINT_COMPLETE")
        assert r["status"] == "FAIL"

    def test_pass_when_both_iv_fail(self):
        """Consistent IV_FAIL/IV_FAIL is not a contradiction (sprint should not close, but that is EVC-04's job)."""
        r = cvb_01_bundled_iv_verdict_must_match_closeout("IV_FAIL", "IV_FAIL")
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# CVB-02: Bundle SHA-256 must match closeout claim
# ─────────────────────────────────────────────────────────────────


class TestCVB02:
    def test_pass_when_sha_matches(self):
        r = cvb_02_bundle_sha256_matches_closeout(W14_ACTUAL_SHA, W14_ACTUAL_SHA)
        assert r["status"] == "PASS"
        assert W14_ACTUAL_SHA[:16] in r["message"]

    def test_pass_when_both_none(self):
        r = cvb_02_bundle_sha256_matches_closeout(None, None)
        assert r["status"] == "PASS"

    def test_pass_when_actual_none(self):
        r = cvb_02_bundle_sha256_matches_closeout(None, W14_STALE_SHA)
        assert r["status"] == "PASS"

    def test_fail_w14_contra_02_sha_mismatch(self):
        """Wave 14 W14-CONTRA-02 regression: closeout claims stale SHA."""
        r = cvb_02_bundle_sha256_matches_closeout(W14_ACTUAL_SHA, W14_STALE_SHA)
        assert r["status"] == "FAIL"
        assert "SHA-256 MISMATCH" in r["message"]
        assert W14_ACTUAL_SHA[:16] in r["message"]
        assert W14_STALE_SHA[:16] in r["message"]
        assert "W14-CONTRA-02" in r["message"]

    def test_fail_sha_reversed(self):
        """Actual=stale, claimed=actual — also a mismatch."""
        r = cvb_02_bundle_sha256_matches_closeout(W14_STALE_SHA, W14_ACTUAL_SHA)
        assert r["status"] == "FAIL"


# ─────────────────────────────────────────────────────────────────
# CVB-03: Bundle size must match closeout claim
# ─────────────────────────────────────────────────────────────────


class TestCVB03:
    def test_pass_when_size_matches(self):
        r = cvb_03_bundle_size_matches_closeout(W14_ACTUAL_SIZE, W14_ACTUAL_SIZE)
        assert r["status"] == "PASS"

    def test_pass_when_both_none(self):
        r = cvb_03_bundle_size_matches_closeout(None, None)
        assert r["status"] == "PASS"

    def test_fail_w14_contra_03_size_mismatch(self):
        """Wave 14 W14-CONTRA-03 regression: closeout claims smaller size."""
        r = cvb_03_bundle_size_matches_closeout(W14_ACTUAL_SIZE, W14_STALE_SIZE)
        assert r["status"] == "FAIL"
        assert "SIZE MISMATCH" in r["message"]
        assert str(W14_ACTUAL_SIZE) in r["message"]
        assert str(W14_STALE_SIZE) in r["message"]
        assert "W14-CONTRA-03" in r["message"]

    def test_fail_size_too_large(self):
        """Closeout overclaims size."""
        r = cvb_03_bundle_size_matches_closeout(1000, 2000)
        assert r["status"] == "FAIL"
        assert "-1000" in r["message"]

    def test_fail_size_too_small(self):
        """Closeout underclaims size (bundle grew after closeout was written)."""
        r = cvb_03_bundle_size_matches_closeout(W14_ACTUAL_SIZE, W14_STALE_SIZE)
        delta = W14_ACTUAL_SIZE - W14_STALE_SIZE
        r2 = cvb_03_bundle_size_matches_closeout(W14_ACTUAL_SIZE, W14_STALE_SIZE)
        assert r2["status"] == "FAIL"
        assert f"+{delta}" in r2["message"]


# ─────────────────────────────────────────────────────────────────
# CVB-04: Bundle entry count must match closeout claim
# ─────────────────────────────────────────────────────────────────


class TestCVB04:
    def test_pass_when_entries_match(self):
        r = cvb_04_bundle_entry_count_matches_closeout(W14_ENTRIES, W14_ENTRIES)
        assert r["status"] == "PASS"

    def test_pass_when_both_none(self):
        r = cvb_04_bundle_entry_count_matches_closeout(None, None)
        assert r["status"] == "PASS"

    def test_pass_when_actual_none(self):
        r = cvb_04_bundle_entry_count_matches_closeout(None, 51)
        assert r["status"] == "PASS"

    def test_fail_entry_count_mismatch(self):
        r = cvb_04_bundle_entry_count_matches_closeout(45, 51)
        assert r["status"] == "FAIL"
        assert "ENTRY COUNT MISMATCH" in r["message"]
        assert "45" in r["message"]
        assert "51" in r["message"]

    def test_fail_entry_count_extra(self):
        r = cvb_04_bundle_entry_count_matches_closeout(55, 51)
        assert r["status"] == "FAIL"


# ─────────────────────────────────────────────────────────────────
# CVB-05: Sidecar SHA must match bundle SHA
# ─────────────────────────────────────────────────────────────────


class TestCVB05:
    def test_pass_when_no_sidecar_and_not_referenced(self):
        r = cvb_05_sidecar_sha_matches_bundle(
            None, W14_ACTUAL_SHA, sidecar_present=False, closeout_references_sidecar=False
        )
        assert r["status"] == "PASS"

    def test_fail_when_closeout_references_sidecar_but_not_present(self):
        r = cvb_05_sidecar_sha_matches_bundle(
            None, W14_ACTUAL_SHA, sidecar_present=False, closeout_references_sidecar=True
        )
        assert r["status"] == "FAIL"
        assert "sidecar" in r["message"].lower()
        assert "no sidecar" in r["message"].lower()

    def test_pass_when_sidecar_sha_matches_bundle(self):
        r = cvb_05_sidecar_sha_matches_bundle(
            W14_ACTUAL_SHA, W14_ACTUAL_SHA, sidecar_present=True, closeout_references_sidecar=True
        )
        assert r["status"] == "PASS"

    def test_fail_when_sidecar_sha_stale(self):
        """Sidecar records stale SHA from prior bundle build."""
        r = cvb_05_sidecar_sha_matches_bundle(
            W14_STALE_SHA, W14_ACTUAL_SHA, sidecar_present=True, closeout_references_sidecar=True
        )
        assert r["status"] == "FAIL"
        assert "SIDECAR SHA MISMATCH" in r["message"]
        assert W14_STALE_SHA[:16] in r["message"]
        assert W14_ACTUAL_SHA[:16] in r["message"]

    def test_pass_when_sidecar_present_but_no_sha_values(self):
        r = cvb_05_sidecar_sha_matches_bundle(None, None, sidecar_present=True, closeout_references_sidecar=True)
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# run_all_cvb_validators — aggregate runner
# ─────────────────────────────────────────────────────────────────


class TestRunAllCVBValidators:
    def _clean_kwargs(self):
        return {
            "bundled_iv_verdict": "IV_PASS",
            "closeout_iv_verdict": "IV_PASS",
            "bundle_sha256_actual": W14_ACTUAL_SHA,
            "closeout_sha256_claimed": W14_ACTUAL_SHA,
            "bundle_size_actual": W14_ACTUAL_SIZE,
            "closeout_size_claimed": W14_ACTUAL_SIZE,
            "bundle_entries_actual": W14_ENTRIES,
            "closeout_entries_claimed": W14_ENTRIES,
            "sidecar_sha256": W14_ACTUAL_SHA,
            "sidecar_present": True,
            "closeout_references_sidecar": True,
            "sprint_verdict": "SPRINT_COMPLETE",
        }

    def test_all_pass_clean_bundle(self):
        r = run_all_cvb_validators(**self._clean_kwargs())
        assert r["verdict"] == "ALL_PASS"
        assert r["pass"] == 5
        assert r["fail"] == 0

    def test_wave14_defect_all_three_contradictions(self):
        """Simulate the full Wave 14 defect scenario: IV_FAIL in bundle, SHA mismatch, size mismatch."""
        kwargs = self._clean_kwargs()
        kwargs["bundled_iv_verdict"] = "IV_FAIL"
        kwargs["closeout_sha256_claimed"] = W14_STALE_SHA
        kwargs["closeout_size_claimed"] = W14_STALE_SIZE
        r = run_all_cvb_validators(**kwargs)
        assert r["verdict"] == "FAIL"
        assert r["fail"] >= 3  # CVB-01, CVB-02, CVB-03 all fail

    def test_wave14_iv_contradiction_only(self):
        """Only IV verdict contradicts — CVB-01 fails."""
        kwargs = self._clean_kwargs()
        kwargs["bundled_iv_verdict"] = "IV_FAIL"
        r = run_all_cvb_validators(**kwargs)
        assert r["verdict"] == "FAIL"
        failing = [rule for rule in r["rules"] if rule["status"] == "FAIL"]
        assert any(rule["rule"] == "CVB-01" for rule in failing)

    def test_sha_mismatch_only(self):
        """Only SHA mismatches — CVB-02 fails."""
        kwargs = self._clean_kwargs()
        kwargs["closeout_sha256_claimed"] = W14_STALE_SHA
        r = run_all_cvb_validators(**kwargs)
        assert r["verdict"] == "FAIL"
        failing = [rule for rule in r["rules"] if rule["status"] == "FAIL"]
        assert any(rule["rule"] == "CVB-02" for rule in failing)

    def test_result_structure(self):
        r = run_all_cvb_validators(**self._clean_kwargs())
        assert r["suite"] == "CVB"
        assert len(r["rules"]) == 5
        for rule in r["rules"]:
            assert "rule" in rule
            assert "status" in rule
            assert "message" in rule
            assert rule["rule"].startswith("CVB-")
