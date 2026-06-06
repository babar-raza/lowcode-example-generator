"""
Tests for Evidence Validity Checking (EVC) Validators — EVC-01..EVC-08

Regression fixtures derived from Wave 13 evidence integrity defects:
  W13-CONTRA-01: Bundle contains IV_FAIL pre-closeout snapshot
  W13-CONTRA-02: Bundle lacks final/sprint-closeout.json
  W13-CONTRA-03: Adversarial review is PRE_CLOSEOUT only
  W13-CONTRA-04: Taskcard claims IV PASS while bundled IV shows IV_FAIL
"""
import pytest

from src.plugin_examples.fixture_factory.evidence_validity_validators import (
    evc_01_bundled_iv_must_be_pass_or_have_later_pass,
    evc_02_bundle_must_contain_final_closeout,
    evc_03_adversarial_review_must_not_be_pre_closeout_only,
    evc_04_iv_verdict_agrees_with_sprint_verdict,
    evc_05_pre_closeout_not_accepted_as_final,
    evc_06_sidecar_path_referenced_must_be_verifiable,
    evc_07_bundle_entries_match_closeout_count,
    evc_08_sprint_verdict_consistent_across_artifacts,
    run_all_evc_validators,
)


# ─────────────────────────────────────────────────────────────────
# EVC-01: Bundled IV must be IV_PASS or have a later IV_PASS
# ─────────────────────────────────────────────────────────────────

class TestEVC01:
    def test_pass_when_bundled_iv_is_pass(self):
        r = evc_01_bundled_iv_must_be_pass_or_have_later_pass("IV_PASS")
        assert r["status"] == "PASS"

    def test_pass_when_no_bundled_iv(self):
        r = evc_01_bundled_iv_must_be_pass_or_have_later_pass(None)
        assert r["status"] == "PASS"

    def test_fail_when_bundled_iv_fail_no_later_pass(self):
        """Wave 13 W13-CONTRA-01 regression: bundle has IV_FAIL, no repair addendum."""
        r = evc_01_bundled_iv_must_be_pass_or_have_later_pass("IV_FAIL")
        assert r["status"] == "FAIL"
        assert "IV_FAIL" in r["message"]

    def test_pass_when_bundled_iv_fail_but_later_pass_documented(self):
        """Wave 13 repair scenario: IV_FAIL in bundle is overridden by repair addendum."""
        r = evc_01_bundled_iv_must_be_pass_or_have_later_pass(
            "IV_FAIL",
            has_later_iv_pass=True,
            later_iv_pass_source="wave14-closure-repair/wave13-final-iv-rerun.json",
        )
        assert r["status"] == "PASS"
        assert "wave14" in r["message"]

    def test_fail_when_bundled_iv_fail_later_pass_not_sourced(self):
        """has_later_iv_pass=True but no source provided — should FAIL."""
        r = evc_01_bundled_iv_must_be_pass_or_have_later_pass(
            "IV_FAIL", has_later_iv_pass=True, later_iv_pass_source=""
        )
        assert r["status"] == "FAIL"


# ─────────────────────────────────────────────────────────────────
# EVC-02: Bundle must contain final/sprint-closeout.json
# ─────────────────────────────────────────────────────────────────

class TestEVC02:
    def test_pass_when_closeout_in_bundle(self):
        entries = [
            "reports/sprint/iv/iv-results.json",
            "reports/sprint/final/sprint-closeout.json",
        ]
        r = evc_02_bundle_must_contain_final_closeout(entries)
        assert r["status"] == "PASS"

    def test_pass_when_no_entries_provided(self):
        r = evc_02_bundle_must_contain_final_closeout(None)
        assert r["status"] == "PASS"

    def test_fail_when_closeout_missing_from_bundle(self):
        """Wave 13 W13-CONTRA-02 regression: final/sprint-closeout.json missing."""
        entries = [
            "reports/sprint/iv/iv-results.json",
            "reports/sprint/taskcards/taskcards.json",
        ]
        r = evc_02_bundle_must_contain_final_closeout(entries)
        assert r["status"] == "FAIL"
        assert "final/sprint-closeout.json" in r["message"]

    def test_pass_with_external_proof_manifest(self):
        entries = ["reports/sprint/iv/iv-results.json"]
        r = evc_02_bundle_must_contain_final_closeout(entries, has_external_proof_manifest=True)
        assert r["status"] == "PASS"

    def test_pass_with_sprint_prefix_path_in_entries(self):
        entries = [
            "lowcode-plugin-canonical-package-wave14/final/sprint-closeout.json"
        ]
        r = evc_02_bundle_must_contain_final_closeout(entries)
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# EVC-03: Adversarial review must not be PRE_CLOSEOUT only
# ─────────────────────────────────────────────────────────────────

class TestEVC03:
    def test_pass_when_not_sprint_complete(self):
        r = evc_03_adversarial_review_must_not_be_pre_closeout_only(
            "ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT", sprint_verdict="IN_PROGRESS"
        )
        assert r["status"] == "PASS"

    def test_fail_when_sprint_complete_and_pre_closeout(self):
        """Wave 13 W13-CONTRA-03 regression."""
        r = evc_03_adversarial_review_must_not_be_pre_closeout_only(
            "ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT", sprint_verdict="SPRINT_COMPLETE"
        )
        assert r["status"] == "FAIL"
        assert "PRE_CLOSEOUT" in r["message"]

    def test_pass_when_final_adversarial_review(self):
        r = evc_03_adversarial_review_must_not_be_pre_closeout_only(
            "ADVERSARIAL_REVIEW_PASS", sprint_verdict="SPRINT_COMPLETE"
        )
        assert r["status"] == "PASS"

    def test_fail_when_sprint_complete_and_no_adversarial_review(self):
        r = evc_03_adversarial_review_must_not_be_pre_closeout_only(
            None, sprint_verdict="SPRINT_COMPLETE"
        )
        assert r["status"] == "FAIL"


# ─────────────────────────────────────────────────────────────────
# EVC-04: IV verdict must agree with sprint verdict
# ─────────────────────────────────────────────────────────────────

class TestEVC04:
    def test_pass_when_both_pass(self):
        r = evc_04_iv_verdict_agrees_with_sprint_verdict("IV_PASS", "SPRINT_COMPLETE")
        assert r["status"] == "PASS"

    def test_pass_when_not_sprint_complete(self):
        r = evc_04_iv_verdict_agrees_with_sprint_verdict("IV_FAIL", "IN_PROGRESS")
        assert r["status"] == "PASS"

    def test_fail_when_sprint_complete_but_iv_fail(self):
        """Wave 13 W13-CONTRA-04 regression."""
        r = evc_04_iv_verdict_agrees_with_sprint_verdict("IV_FAIL", "SPRINT_COMPLETE")
        assert r["status"] == "FAIL"
        assert "IV_FAIL" in r["message"]

    def test_fail_when_sprint_complete_but_no_iv(self):
        r = evc_04_iv_verdict_agrees_with_sprint_verdict(None, "SPRINT_COMPLETE")
        assert r["status"] == "FAIL"


# ─────────────────────────────────────────────────────────────────
# EVC-05: PRE_CLOSEOUT adversarial review requires final review
# ─────────────────────────────────────────────────────────────────

class TestEVC05:
    def test_pass_when_no_pre_closeout(self):
        r = evc_05_pre_closeout_not_accepted_as_final("ADVERSARIAL_REVIEW_PASS")
        assert r["status"] == "PASS"

    def test_fail_when_pre_closeout_only(self):
        r = evc_05_pre_closeout_not_accepted_as_final(
            "ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT", has_final_adversarial_review=False
        )
        assert r["status"] == "FAIL"

    def test_pass_when_pre_closeout_plus_final(self):
        r = evc_05_pre_closeout_not_accepted_as_final(
            "ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT", has_final_adversarial_review=True
        )
        assert r["status"] == "PASS"

    def test_pass_when_no_adversarial_verdict(self):
        r = evc_05_pre_closeout_not_accepted_as_final(None)
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# EVC-06: Sidecar path referenced must be verified
# ─────────────────────────────────────────────────────────────────

class TestEVC06:
    def test_pass_when_no_sidecar_path(self):
        r = evc_06_sidecar_path_referenced_must_be_verifiable({})
        assert r["status"] == "PASS"

    def test_pass_when_sidecar_verified(self):
        closeout = {"sidecar_path": ".local/evidence-bundles/sprint.zip.sha256"}
        r = evc_06_sidecar_path_referenced_must_be_verifiable(closeout, sidecar_verified=True)
        assert r["status"] == "PASS"

    def test_fail_when_sidecar_path_but_not_verified(self):
        closeout = {"sidecar_path": ".local/evidence-bundles/sprint.zip.sha256"}
        r = evc_06_sidecar_path_referenced_must_be_verifiable(closeout, sidecar_verified=False)
        assert r["status"] == "FAIL"
        assert "sidecar_path" in r["message"]


# ─────────────────────────────────────────────────────────────────
# EVC-07: Bundle entry count matches closeout record
# ─────────────────────────────────────────────────────────────────

class TestEVC07:
    def test_pass_when_counts_match(self):
        r = evc_07_bundle_entries_match_closeout_count(25, 25)
        assert r["status"] == "PASS"

    def test_fail_when_counts_differ(self):
        """Wave 13 scenario: closeout records 25 but bundle built at different time."""
        r = evc_07_bundle_entries_match_closeout_count(24, 25)
        assert r["status"] == "FAIL"
        assert "24" in r["message"]
        assert "25" in r["message"]

    def test_pass_when_not_provided(self):
        r = evc_07_bundle_entries_match_closeout_count(None, None)
        assert r["status"] == "PASS"

    def test_pass_when_one_missing(self):
        r = evc_07_bundle_entries_match_closeout_count(25, None)
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# EVC-08: Sprint verdict consistent across artifacts
# ─────────────────────────────────────────────────────────────────

class TestEVC08:
    def test_pass_all_consistent(self):
        r = evc_08_sprint_verdict_consistent_across_artifacts(
            "SPRINT_COMPLETE", "SPRINT_COMPLETE", "IV_PASS"
        )
        assert r["status"] == "PASS"

    def test_pass_non_sprint_complete(self):
        r = evc_08_sprint_verdict_consistent_across_artifacts(
            "IN_PROGRESS", "LANE_H_IN_PROGRESS", "IV_FAIL"
        )
        assert r["status"] == "PASS"

    def test_fail_when_sprint_complete_but_lane_ledger_in_progress(self):
        r = evc_08_sprint_verdict_consistent_across_artifacts(
            "SPRINT_COMPLETE", "LANE_H_IN_PROGRESS", "IV_PASS"
        )
        assert r["status"] == "FAIL"
        assert "LANE_H_IN_PROGRESS" in r["message"]

    def test_fail_when_sprint_complete_but_iv_fail(self):
        r = evc_08_sprint_verdict_consistent_across_artifacts(
            "SPRINT_COMPLETE", "SPRINT_COMPLETE", "IV_FAIL"
        )
        assert r["status"] == "FAIL"
        assert "IV_FAIL" in r["message"]

    def test_pass_when_lane_ledger_contains_complete(self):
        """Any lane ledger verdict containing 'COMPLETE' is accepted."""
        r = evc_08_sprint_verdict_consistent_across_artifacts(
            "SPRINT_COMPLETE", "ALL_LANES_COMPLETE", "IV_PASS"
        )
        assert r["status"] == "PASS"


# ─────────────────────────────────────────────────────────────────
# run_all_evc_validators aggregate runner
# ─────────────────────────────────────────────────────────────────

class TestRunAllEVC:
    def test_all_pass_clean_sprint(self):
        """Clean sprint with final closeout, IV_PASS, final adversarial review."""
        closeout = {"sidecar_path": ""}
        result = run_all_evc_validators(
            bundled_iv_verdict="IV_PASS",
            bundle_entries=["reports/sprint/final/sprint-closeout.json"],
            adversarial_verdict="ADVERSARIAL_REVIEW_PASS",
            sprint_verdict="SPRINT_COMPLETE",
            iv_verdict="IV_PASS",
            closeout=closeout,
            lane_ledger_verdict="SPRINT_COMPLETE",
            has_final_adversarial_review=True,
            sidecar_verified=False,
            bundle_entry_count_actual=1,
            bundle_entry_count_closeout=1,
        )
        assert result["verdict"] == "ALL_PASS"
        assert result["fail"] == 0

    def test_wave13_contradiction_scenario(self):
        """Regression: Wave 13 exact defect scenario must produce FAIL."""
        closeout = {"sidecar_path": ".local/evidence-bundles/wave13.zip.sha256"}
        result = run_all_evc_validators(
            bundled_iv_verdict="IV_FAIL",           # W13-CONTRA-01
            bundle_entries=["reports/wave13/taskcards/taskcards.json"],  # no final/sprint-closeout.json
            adversarial_verdict="ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT",  # W13-CONTRA-03
            sprint_verdict="SPRINT_COMPLETE",
            iv_verdict="IV_FAIL",                   # W13-CONTRA-04
            closeout=closeout,
            lane_ledger_verdict="SPRINT_COMPLETE",
            has_later_iv_pass=False,
            has_external_proof_manifest=False,
            has_final_adversarial_review=False,
            sidecar_verified=False,
            bundle_entry_count_actual=25,
            bundle_entry_count_closeout=25,
        )
        assert result["verdict"] == "FAIL"
        assert result["fail"] >= 3  # at least EVC-01, EVC-02, EVC-03 must fail

    def test_wave13_with_repair_addendum_passes(self):
        """Wave 14 repair scenario: Wave 13 defects resolved by addendum."""
        closeout = {"sidecar_path": ".local/evidence-bundles/wave13.zip.sha256"}
        result = run_all_evc_validators(
            bundled_iv_verdict="IV_FAIL",
            bundle_entries=["reports/wave13/taskcards/taskcards.json"],
            adversarial_verdict="ADVERSARIAL_REVIEW_PASS_PRE_CLOSEOUT",
            sprint_verdict="SPRINT_COMPLETE",
            iv_verdict="IV_PASS",  # disk state is IV_PASS (post-repair)
            closeout=closeout,
            lane_ledger_verdict="SPRINT_COMPLETE",
            has_later_iv_pass=True,
            later_iv_pass_source="wave14-closure-repair/wave13-final-iv-rerun.json",
            has_external_proof_manifest=True,  # repair addendum serves as proof manifest
            has_final_adversarial_review=True,  # Wave 14 provides final adversarial review
            sidecar_verified=True,
            bundle_entry_count_actual=None,
            bundle_entry_count_closeout=None,
        )
        assert result["verdict"] == "ALL_PASS"
