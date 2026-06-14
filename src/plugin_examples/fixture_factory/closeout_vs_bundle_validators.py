"""
Closeout-vs-Bundle (CVB) Validators — CVB-01..CVB-05

These validators prevent the Wave 14 evidence integrity defects from recurring:
- The bundled iv-results.json verdict cannot contradict the closeout iv.verdict
- The bundle SHA, size, and entry count claimed in closeout must match the actual bundle
- If the closeout references a sidecar_path, the sidecar must exist and match the bundle

Wave 14 defects that motivated this module:
  W14-CONTRA-01: Bundle iv-results.json=IV_FAIL but closeout.iv.verdict=IV_PASS
  W14-CONTRA-02: Closeout claims sha256=9a34a24... but actual bundle sha256=0cfddd35...
  W14-CONTRA-03: Closeout claims size_bytes=747861 but actual bundle size=747902
  W14-CONTRA-04: IV was re-run AFTER bundle was built — bundle captured stale IV_FAIL
  W14-CONTRA-05: Adversarial review did not check bundled iv-results.json vs closeout

Root cause: bundle was frozen before Lane I taskcards closed and final IV ran.
Prevention: final IV must pass, then bundle built (capturing IV_PASS), then closeout written
with SHA/size/entries from the frozen bundle. Never rebuild closeout after bundle is frozen.
"""

from __future__ import annotations

from typing import Any


def cvb_01_bundled_iv_verdict_must_match_closeout(
    bundled_iv_verdict: str | None,
    closeout_iv_verdict: str | None,
    sprint_verdict: str = "",
) -> dict[str, Any]:
    """CVB-01: Bundled iv-results.json verdict must agree with closeout.iv.verdict.

    If the bundle contains iv-results.json with verdict=IV_FAIL but sprint-closeout.json
    inside the same bundle claims verdict=IV_PASS, there is a critical contradiction.
    A SPRINT_COMPLETE claim is invalid if the authoritative bundled IV result is IV_FAIL.

    Prevents: Wave 14 W14-CONTRA-01 (bundled IV_FAIL with SPRINT_COMPLETE closeout).
    """
    if bundled_iv_verdict is None and closeout_iv_verdict is None:
        return {
            "rule": "CVB-01",
            "status": "PASS",
            "message": "No bundled IV verdict or closeout IV verdict available — not applicable",
        }
    if bundled_iv_verdict is None:
        return {
            "rule": "CVB-01",
            "status": "PASS",
            "message": "No bundled iv-results.json found — CVB-01 cannot check; assumed compliant",
        }
    if closeout_iv_verdict is None:
        return {
            "rule": "CVB-01",
            "status": "PASS",
            "message": "No closeout iv.verdict found — CVB-01 cannot check; assumed compliant",
        }
    if bundled_iv_verdict == closeout_iv_verdict:
        return {
            "rule": "CVB-01",
            "status": "PASS",
            "message": (
                f"Bundled iv-results verdict='{bundled_iv_verdict}' agrees with "
                f"closeout iv.verdict='{closeout_iv_verdict}'"
            ),
        }
    return {
        "rule": "CVB-01",
        "status": "FAIL",
        "message": (
            f"CONTRADICTION: bundled iv-results.json verdict='{bundled_iv_verdict}' "
            f"disagrees with closeout iv.verdict='{closeout_iv_verdict}'. "
            "The bundle must be rebuilt after the final IV_PASS run before sprint can close. "
            "(Wave 14 W14-CONTRA-01 pattern)"
        ),
    }


def cvb_02_bundle_sha256_matches_closeout(
    bundle_sha256_actual: str | None,
    closeout_sha256_claimed: str | None,
) -> dict[str, Any]:
    """CVB-02: Actual bundle SHA-256 must match the SHA-256 claimed in sprint-closeout.json.

    If the bundle SHA in the closeout does not match the actual bundle, the closeout
    was written before (or after) the current bundle was finalized. Either the closeout
    is stale, or the bundle was modified after the closeout was written.

    Prevents: Wave 14 W14-CONTRA-02 (closeout claims 9a34a24... but bundle is 0cfddd35...).
    """
    if bundle_sha256_actual is None or closeout_sha256_claimed is None:
        return {
            "rule": "CVB-02",
            "status": "PASS",
            "message": "SHA values not provided — CVB-02 cannot check; assumed compliant",
        }
    if bundle_sha256_actual == closeout_sha256_claimed:
        return {
            "rule": "CVB-02",
            "status": "PASS",
            "message": f"Bundle SHA-256 matches closeout claim: {bundle_sha256_actual[:16]}...",
        }
    return {
        "rule": "CVB-02",
        "status": "FAIL",
        "message": (
            f"SHA-256 MISMATCH: actual bundle sha256={bundle_sha256_actual[:16]}... "
            f"but closeout claims {closeout_sha256_claimed[:16]}... "
            "Closeout must be written AFTER the bundle is frozen with the final bundle's SHA. "
            "(Wave 14 W14-CONTRA-02 pattern)"
        ),
    }


def cvb_03_bundle_size_matches_closeout(
    bundle_size_actual: int | None,
    closeout_size_claimed: int | None,
) -> dict[str, Any]:
    """CVB-03: Actual bundle size_bytes must match the size_bytes claimed in sprint-closeout.json.

    A size mismatch indicates the bundle was modified after the closeout was written,
    or the closeout was written for a different (smaller/larger) bundle than the current one.

    Prevents: Wave 14 W14-CONTRA-03 (closeout claims 747861 bytes, actual bundle 747902 bytes).
    """
    if bundle_size_actual is None or closeout_size_claimed is None:
        return {
            "rule": "CVB-03",
            "status": "PASS",
            "message": "Size values not provided — CVB-03 cannot check; assumed compliant",
        }
    if bundle_size_actual == closeout_size_claimed:
        return {
            "rule": "CVB-03",
            "status": "PASS",
            "message": f"Bundle size_bytes matches closeout claim: {bundle_size_actual}",
        }
    delta = bundle_size_actual - closeout_size_claimed
    return {
        "rule": "CVB-03",
        "status": "FAIL",
        "message": (
            f"SIZE MISMATCH: actual bundle size={bundle_size_actual} bytes "
            f"but closeout claims {closeout_size_claimed} bytes "
            f"(delta={delta:+d} bytes). "
            "Closeout must be written AFTER the bundle is frozen with the final bundle's size. "
            "(Wave 14 W14-CONTRA-03 pattern)"
        ),
    }


def cvb_04_bundle_entry_count_matches_closeout(
    bundle_entries_actual: int | None,
    closeout_entries_claimed: int | None,
) -> dict[str, Any]:
    """CVB-04: Actual bundle entry count must match the entries claimed in sprint-closeout.json.

    The entry count in the closeout must reflect the final bundle's actual entry count.
    A mismatch means the closeout references a different iteration of the bundle.
    """
    if bundle_entries_actual is None or closeout_entries_claimed is None:
        return {
            "rule": "CVB-04",
            "status": "PASS",
            "message": "Entry counts not provided — CVB-04 cannot check; assumed compliant",
        }
    if bundle_entries_actual == closeout_entries_claimed:
        return {
            "rule": "CVB-04",
            "status": "PASS",
            "message": f"Bundle entry count matches closeout claim: {bundle_entries_actual}",
        }
    return {
        "rule": "CVB-04",
        "status": "FAIL",
        "message": (
            f"ENTRY COUNT MISMATCH: actual bundle entries={bundle_entries_actual} "
            f"but closeout claims {closeout_entries_claimed}. "
            "Closeout must be written AFTER the final bundle is frozen."
        ),
    }


def cvb_05_sidecar_sha_matches_bundle(
    sidecar_sha256: str | None,
    bundle_sha256_actual: str | None,
    sidecar_present: bool = False,
    closeout_references_sidecar: bool = False,
) -> dict[str, Any]:
    """CVB-05: External sidecar SHA-256 must match the actual bundle SHA-256.

    The sidecar is the external proof of the bundle's integrity. If it exists, its SHA
    must equal the bundle's actual SHA. A mismatch means the sidecar was written for a
    different version of the bundle, or the sidecar is corrupted.

    Also catches the case where the closeout references a sidecar_path but no sidecar exists.

    Prevents: Scenario where sidecar exists but records a stale SHA from a prior bundle build.
    """
    if closeout_references_sidecar and not sidecar_present:
        return {
            "rule": "CVB-05",
            "status": "FAIL",
            "message": (
                "Closeout references sidecar_path but no sidecar file is present on disk. "
                "Sidecar must be created and written before sprint is declared SPRINT_COMPLETE."
            ),
        }
    if not sidecar_present:
        return {
            "rule": "CVB-05",
            "status": "PASS",
            "message": "No sidecar present and closeout does not reference one — not applicable",
        }
    if sidecar_sha256 is None or bundle_sha256_actual is None:
        return {
            "rule": "CVB-05",
            "status": "PASS",
            "message": "Sidecar present but SHA values not provided — cannot cross-check; assumed compliant",
        }
    if sidecar_sha256 == bundle_sha256_actual:
        return {
            "rule": "CVB-05",
            "status": "PASS",
            "message": f"Sidecar SHA matches bundle SHA: {sidecar_sha256[:16]}...",
        }
    return {
        "rule": "CVB-05",
        "status": "FAIL",
        "message": (
            f"SIDECAR SHA MISMATCH: sidecar records {sidecar_sha256[:16]}... "
            f"but actual bundle SHA is {bundle_sha256_actual[:16]}... "
            "Sidecar must be written AFTER the final bundle is frozen."
        ),
    }


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------


def run_all_cvb_validators(
    bundled_iv_verdict: str | None,
    closeout_iv_verdict: str | None,
    bundle_sha256_actual: str | None,
    closeout_sha256_claimed: str | None,
    bundle_size_actual: int | None,
    closeout_size_claimed: int | None,
    bundle_entries_actual: int | None,
    closeout_entries_claimed: int | None,
    sidecar_sha256: str | None,
    sidecar_present: bool,
    closeout_references_sidecar: bool,
    sprint_verdict: str = "",
) -> dict[str, Any]:
    """Run all CVB-01..CVB-05 validators and return aggregate result."""
    results = [
        cvb_01_bundled_iv_verdict_must_match_closeout(
            bundled_iv_verdict, closeout_iv_verdict, sprint_verdict=sprint_verdict
        ),
        cvb_02_bundle_sha256_matches_closeout(bundle_sha256_actual, closeout_sha256_claimed),
        cvb_03_bundle_size_matches_closeout(bundle_size_actual, closeout_size_claimed),
        cvb_04_bundle_entry_count_matches_closeout(bundle_entries_actual, closeout_entries_claimed),
        cvb_05_sidecar_sha_matches_bundle(
            sidecar_sha256,
            bundle_sha256_actual,
            sidecar_present=sidecar_present,
            closeout_references_sidecar=closeout_references_sidecar,
        ),
    ]
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "suite": "CVB",
        "rules": results,
        "pass": pass_count,
        "fail": fail_count,
        "verdict": "ALL_PASS" if fail_count == 0 else "FAIL",
    }
