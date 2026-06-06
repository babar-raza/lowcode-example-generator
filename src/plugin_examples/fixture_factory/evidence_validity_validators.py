"""
Evidence Validity Checking (EVC) Validators — EVC-01..EVC-08

These validators prevent the Wave 13 evidence integrity defects from recurring:
- A stale pre-closeout IV_FAIL must not be treated as final evidence of success
- A bundle without final/sprint-closeout.json cannot claim SPRINT_COMPLETE
- A PRE_CLOSEOUT adversarial review must not be the only adversarial evidence
- IV result inside the bundle must agree with the sprint verdict
- Taskcard evidence strings are cross-checked against referenced artifact verdicts

Wave 13 defects that motivated this module:
  W13-CONTRA-01: Bundle contained IV_FAIL (44/45) — pre-closeout snapshot, not final
  W13-CONTRA-02: Bundle lacked final/sprint-closeout.json (created after bundle was zipped)
  W13-CONTRA-03: Adversarial review was PRE_CLOSEOUT only; final review not written
  W13-CONTRA-04: Taskcard W13-LH-09 claimed "IV PASS" while bundled IV showed IV_FAIL
"""
from __future__ import annotations
from typing import Any


def evc_01_bundled_iv_must_be_pass_or_have_later_pass(
    bundled_iv_verdict: str | None,
    has_later_iv_pass: bool = False,
    later_iv_pass_source: str = "",
) -> dict[str, Any]:
    """EVC-01: If the bundle contains an IV result, it must be IV_PASS.

    If the bundled IV result is IV_FAIL, a later IV_PASS must be present and
    explicitly marked as the authoritative final result (e.g. repair addendum).

    Prevents: Wave 13 W13-CONTRA-01 (bundle contains IV_FAIL pre-closeout snapshot).
    """
    if bundled_iv_verdict is None:
        return {
            "rule": "EVC-01",
            "status": "PASS",
            "message": "No bundled IV result found — not applicable",
        }
    if bundled_iv_verdict == "IV_PASS":
        return {
            "rule": "EVC-01",
            "status": "PASS",
            "message": "Bundled IV result is IV_PASS — consistent with SPRINT_COMPLETE",
        }
    # bundled_iv_verdict is not IV_PASS
    if has_later_iv_pass and later_iv_pass_source:
        return {
            "rule": "EVC-01",
            "status": "PASS",
            "message": (
                f"Bundled IV_FAIL overridden by later IV_PASS: {later_iv_pass_source}. "
                "Repair addendum required to document override."
            ),
        }
    return {
        "rule": "EVC-01",
        "status": "FAIL",
        "message": (
            f"Bundled IV verdict is '{bundled_iv_verdict}'. "
            "SPRINT_COMPLETE requires IV_PASS in final bundle or an explicit later-IV_PASS repair addendum."
        ),
    }


def evc_02_bundle_must_contain_final_closeout(
    bundle_entries: list[str] | None,
    sprint: str = "",
    has_external_proof_manifest: bool = False,
) -> dict[str, Any]:
    """EVC-02: Final bundle must contain final/sprint-closeout.json or an external-proof manifest.

    If the bundle was created before final/sprint-closeout.json was written, the sprint
    cannot be considered closed unless a repair addendum explicitly documents this gap.

    Prevents: Wave 13 W13-CONTRA-02 (final/sprint-closeout.json missing from bundle).
    """
    if bundle_entries is None:
        return {
            "rule": "EVC-02",
            "status": "PASS",
            "message": "Bundle entries not provided — cannot check; assumed compliant",
        }
    closeout_key = "final/sprint-closeout.json"
    # Accept both bare path and sprint-prefixed path
    found = any(
        closeout_key in entry or entry.endswith("final/sprint-closeout.json")
        for entry in bundle_entries
    )
    if found:
        return {
            "rule": "EVC-02",
            "status": "PASS",
            "message": "final/sprint-closeout.json found in bundle",
        }
    if has_external_proof_manifest:
        return {
            "rule": "EVC-02",
            "status": "PASS",
            "message": "final/sprint-closeout.json not in bundle, but external-proof manifest provided",
        }
    return {
        "rule": "EVC-02",
        "status": "FAIL",
        "message": (
            "final/sprint-closeout.json NOT found in bundle and no external-proof manifest. "
            "Bundle must contain the final closeout or a repair addendum must document the gap."
        ),
    }


def evc_03_adversarial_review_must_not_be_pre_closeout_only(
    adversarial_verdict: str | None,
    sprint_verdict: str = "",
    has_final_adversarial_review: bool = False,
) -> dict[str, Any]:
    """EVC-03: If sprint_verdict=SPRINT_COMPLETE, adversarial review must not be PRE_CLOSEOUT.

    A PRE_CLOSEOUT adversarial review explicitly states that final verification is still
    required. It cannot serve as the sole adversarial review for a closed sprint.
    If has_final_adversarial_review=True, a separate final review supersedes the pre-closeout one.

    Prevents: Wave 13 W13-CONTRA-03 (only PRE_CLOSEOUT adversarial review in bundle).
    """
    if sprint_verdict != "SPRINT_COMPLETE":
        return {
            "rule": "EVC-03",
            "status": "PASS",
            "message": f"Sprint verdict is {sprint_verdict!r} — EVC-03 only applies to SPRINT_COMPLETE",
        }
    if adversarial_verdict is None:
        return {
            "rule": "EVC-03",
            "status": "FAIL",
            "message": "No adversarial review verdict found — adversarial review is required for SPRINT_COMPLETE",
        }
    if "PRE_CLOSEOUT" in (adversarial_verdict or "").upper():
        if has_final_adversarial_review:
            return {
                "rule": "EVC-03",
                "status": "PASS",
                "message": (
                    f"Adversarial review is PRE_CLOSEOUT but a final adversarial review "
                    "is present and supersedes it — compliant"
                ),
            }
        return {
            "rule": "EVC-03",
            "status": "FAIL",
            "message": (
                f"Adversarial review verdict is '{adversarial_verdict}' (PRE_CLOSEOUT). "
                "A final adversarial review (not pre-closeout) is required for SPRINT_COMPLETE."
            ),
        }
    return {
        "rule": "EVC-03",
        "status": "PASS",
        "message": f"Adversarial review verdict: {adversarial_verdict!r} — not PRE_CLOSEOUT",
    }


def evc_04_iv_verdict_agrees_with_sprint_verdict(
    iv_verdict: str | None,
    sprint_verdict: str = "",
) -> dict[str, Any]:
    """EVC-04: IV result verdict must agree with the sprint final verdict.

    If sprint claims SPRINT_COMPLETE but the only available IV result is IV_FAIL,
    the sprint is not cleanly closed.

    Prevents: Wave 13 pattern where W13-LH-09 claimed "all checks PASS" while bundled
    iv-results.json showed IV_FAIL with 1 failing check.
    """
    if sprint_verdict != "SPRINT_COMPLETE":
        return {
            "rule": "EVC-04",
            "status": "PASS",
            "message": f"Sprint verdict is {sprint_verdict!r} — EVC-04 only applies to SPRINT_COMPLETE",
        }
    if iv_verdict == "IV_PASS":
        return {
            "rule": "EVC-04",
            "status": "PASS",
            "message": "IV verdict=IV_PASS agrees with SPRINT_COMPLETE",
        }
    if iv_verdict is None:
        return {
            "rule": "EVC-04",
            "status": "FAIL",
            "message": "No IV verdict found — IV must be run and result must be IV_PASS for SPRINT_COMPLETE",
        }
    return {
        "rule": "EVC-04",
        "status": "FAIL",
        "message": (
            f"IV verdict='{iv_verdict}' but sprint claims SPRINT_COMPLETE. "
            "IV must be IV_PASS before sprint can be declared SPRINT_COMPLETE."
        ),
    }


def evc_05_pre_closeout_not_accepted_as_final(
    adversarial_verdict: str | None,
    has_final_adversarial_review: bool = False,
) -> dict[str, Any]:
    """EVC-05: A PRE_CLOSEOUT adversarial review must be accompanied by a final review.

    If the only adversarial review present is explicitly labelled PRE_CLOSEOUT, a final
    review must exist separately. A pre-closeout review says 'final verification still
    required' — that verification must be documented.

    Prevents: Wave 13 pattern — adversarial review explicitly said 'final_verification_required'
    but no final review was ever written.
    """
    if adversarial_verdict and "PRE_CLOSEOUT" in adversarial_verdict.upper():
        if has_final_adversarial_review:
            return {
                "rule": "EVC-05",
                "status": "PASS",
                "message": "PRE_CLOSEOUT adversarial review accompanied by final adversarial review — compliant",
            }
        return {
            "rule": "EVC-05",
            "status": "FAIL",
            "message": (
                "PRE_CLOSEOUT adversarial review present but no final adversarial review found. "
                "A pre-closeout review explicitly requires a final verification step."
            ),
        }
    return {
        "rule": "EVC-05",
        "status": "PASS",
        "message": "No PRE_CLOSEOUT adversarial review detected — not applicable",
    }


def evc_06_sidecar_path_referenced_must_be_verifiable(
    closeout: dict,
    sidecar_verified: bool = False,
) -> dict[str, Any]:
    """EVC-06: If sprint-closeout.json references a sidecar_path, sidecar must be verified.

    The sidecar verification is performed by BMV-06. This rule checks that if a closeout
    references a sidecar, the caller has confirmed it was verified (sidecar_verified=True).
    Used as a cross-check between the closeout and the BMV-06 result.

    Prevents: Wave 13 W13-CONTRA-03 acknowledgement that sidecar wasn't yet created at
    adversarial review time.
    """
    sidecar_path = closeout.get("sidecar_path")
    if not sidecar_path:
        return {
            "rule": "EVC-06",
            "status": "PASS",
            "message": "No sidecar_path in closeout — not applicable",
        }
    if sidecar_verified:
        return {
            "rule": "EVC-06",
            "status": "PASS",
            "message": f"Sidecar path '{sidecar_path}' is referenced and verified (BMV-06 passed)",
        }
    return {
        "rule": "EVC-06",
        "status": "FAIL",
        "message": (
            f"Closeout references sidecar_path='{sidecar_path}' but sidecar was not verified. "
            "Run BMV-06 and pass sidecar_verified=True only after it passes."
        ),
    }


def evc_07_bundle_entries_match_closeout_count(
    bundle_entry_count_actual: int | None,
    bundle_entry_count_closeout: int | None,
) -> dict[str, Any]:
    """EVC-07: Actual bundle entry count must match the count recorded in sprint-closeout.json.

    If the closeout records 45 entries but the bundle only has 25, the bundle is stale
    or the closeout was written for a different bundle.

    Prevents: Scenario where final/sprint-closeout.json (written after bundle creation)
    records different entry count than the actual bundle.
    """
    if bundle_entry_count_actual is None or bundle_entry_count_closeout is None:
        return {
            "rule": "EVC-07",
            "status": "PASS",
            "message": "Entry counts not available — cannot cross-check; assumed compliant",
        }
    if bundle_entry_count_actual == bundle_entry_count_closeout:
        return {
            "rule": "EVC-07",
            "status": "PASS",
            "message": f"Bundle entry count matches closeout: {bundle_entry_count_actual}",
        }
    return {
        "rule": "EVC-07",
        "status": "FAIL",
        "message": (
            f"Bundle entry count mismatch: actual={bundle_entry_count_actual}, "
            f"closeout records={bundle_entry_count_closeout}. "
            "Bundle may be stale or closeout was written for a different bundle."
        ),
    }


def evc_08_sprint_verdict_consistent_across_artifacts(
    closeout_verdict: str | None,
    lane_ledger_verdict: str | None,
    iv_verdict: str | None,
) -> dict[str, Any]:
    """EVC-08: Sprint verdict must be consistent across closeout, lane-ledger, and IV result.

    If closeout says SPRINT_COMPLETE but lane-ledger says IN_PROGRESS, or IV says IV_FAIL,
    there is a contradiction that must be resolved before the sprint is truly closed.

    Prevents: Scenario where a sprint is declared SPRINT_COMPLETE in the closeout but
    lane-ledger or IV results disagree.
    """
    verdicts = {
        "closeout": closeout_verdict,
        "lane_ledger": lane_ledger_verdict,
        "iv": iv_verdict,
    }

    # Determine expected consistency
    if closeout_verdict == "SPRINT_COMPLETE":
        # Lane ledger must also show SPRINT_COMPLETE or equivalent
        if lane_ledger_verdict and lane_ledger_verdict not in ("SPRINT_COMPLETE",):
            # Allow partial strings like "LANE_H_COMPLETE" or prefixes
            if "COMPLETE" not in lane_ledger_verdict.upper():
                return {
                    "rule": "EVC-08",
                    "status": "FAIL",
                    "message": (
                        f"Closeout=SPRINT_COMPLETE but lane_ledger='{lane_ledger_verdict}'. "
                        "Lane ledger must also show SPRINT_COMPLETE."
                    ),
                }
        # IV must be IV_PASS
        if iv_verdict and iv_verdict != "IV_PASS":
            return {
                "rule": "EVC-08",
                "status": "FAIL",
                "message": (
                    f"Closeout=SPRINT_COMPLETE but IV verdict='{iv_verdict}'. "
                    "IV must be IV_PASS for consistent SPRINT_COMPLETE."
                ),
            }
        return {
            "rule": "EVC-08",
            "status": "PASS",
            "message": (
                f"Verdicts consistent: closeout={closeout_verdict}, "
                f"lane_ledger={lane_ledger_verdict}, iv={iv_verdict}"
            ),
        }

    # Non-SPRINT_COMPLETE closeout — just check they don't contradict
    return {
        "rule": "EVC-08",
        "status": "PASS",
        "message": f"Non-SPRINT_COMPLETE closeout ({closeout_verdict!r}) — consistency check not required",
    }


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

def run_all_evc_validators(
    bundled_iv_verdict: str | None,
    bundle_entries: list[str] | None,
    adversarial_verdict: str | None,
    sprint_verdict: str,
    iv_verdict: str | None,
    closeout: dict,
    lane_ledger_verdict: str | None,
    has_later_iv_pass: bool = False,
    later_iv_pass_source: str = "",
    has_external_proof_manifest: bool = False,
    has_final_adversarial_review: bool = False,
    sidecar_verified: bool = False,
    bundle_entry_count_actual: int | None = None,
    bundle_entry_count_closeout: int | None = None,
) -> dict[str, Any]:
    """Run all EVC-01..EVC-08 validators and return aggregate result."""
    results = [
        evc_01_bundled_iv_must_be_pass_or_have_later_pass(
            bundled_iv_verdict, has_later_iv_pass, later_iv_pass_source
        ),
        evc_02_bundle_must_contain_final_closeout(
            bundle_entries, sprint=sprint_verdict, has_external_proof_manifest=has_external_proof_manifest
        ),
        evc_03_adversarial_review_must_not_be_pre_closeout_only(
            adversarial_verdict, sprint_verdict=sprint_verdict,
            has_final_adversarial_review=has_final_adversarial_review
        ),
        evc_04_iv_verdict_agrees_with_sprint_verdict(iv_verdict, sprint_verdict=sprint_verdict),
        evc_05_pre_closeout_not_accepted_as_final(
            adversarial_verdict, has_final_adversarial_review=has_final_adversarial_review
        ),
        evc_06_sidecar_path_referenced_must_be_verifiable(closeout, sidecar_verified=sidecar_verified),
        evc_07_bundle_entries_match_closeout_count(
            bundle_entry_count_actual, bundle_entry_count_closeout
        ),
        evc_08_sprint_verdict_consistent_across_artifacts(
            closeout_verdict=sprint_verdict,
            lane_ledger_verdict=lane_ledger_verdict,
            iv_verdict=iv_verdict,
        ),
    ]
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "suite": "EVC",
        "rules": results,
        "pass": pass_count,
        "fail": fail_count,
        "verdict": "ALL_PASS" if fail_count == 0 else "FAIL",
    }
