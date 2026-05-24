# Sprint 75 — Sprint 27 Strict Evidence Contract Revalidation

**Date:** 2026-05-23
**Weekly Review Item 6 Classification:** GOVERNANCE_EXCEPTION_REQUIRED

## Summary

Sprint 27 bundle retroactively fails StrictEvidenceContract V1. This was documented in Sprint 28
(commit `20686d3`). Sprint 75 confirms the finding and applies a formal governance classification.

## What Sprint 27 Was

- **Commit:** 774f516084ff55e0701bf14feb90846cdce129c8 (Sprint 27, circa 2026-05-17)
- **Bundle:** `workspace/verification/sprint27-evidence-gated-publication-pr3-pr9-and-final-pdf-closeout-20260517-165525.zip`
- **File count:** 17 files
- **Era:** Pre-StrictEvidenceContract — this was before Sprint 28 introduced the formal contract

## Evidence of Missing Categories

Sprint 28 Lane 0 audit (`workspace/verification/sprint28/lanes/lane-0/sprint27-evidence-audit.json`)
identified 17 missing artifacts spanning these categories:

| Category | Missing |
|----------|---------|
| FINAL_GIT_STATE (git-status-final.txt) | MISSING |
| FINAL_GIT_DIFF (git-diff-final.patch) | MISSING |
| CHANGED_FILES_LIST | MISSING |
| FINAL_STATE_SUMMARY | MISSING |
| FINAL_VERDICT | MISSING |
| BUNDLE_CONTRACT_DEFINITION | MISSING |
| BUNDLE_CONTRACT_VALIDATION | MISSING |
| PR_APPROVAL_BLOCKED_PROOF (×6) | MISSING |
| PUBLICATION_STATUS | MISSING |
| FAMILY_SCOREBOARD | MISSING |
| TASKCARD_RECONCILIATION | MISSING |
| TEST_LOG_RAW | MISSING (only summary present) |

Sprint 28 audit supervisor verdict: `SPRINT27_EVIDENCE_BUNDLE_PRESENT_BUT_CONTRACT_TOO_WEAK`
StrictEvidenceContract V1 verdict for Sprint 27: **FAILS (≥10 categories missing)**

## Local Availability

- `reports/sprint27/` does **NOT** exist in local `reports/` directory
- Earliest report in `reports/` is `sprint57/`
- Sprint 27 artifacts exist only in `workspace/verification/sprint27/` (original era storage)

## Can Sprint 27 Be Rebuilt?

**No.** Sprint 27 represents a historical work state from 2026-05-17. Rebuilding it would require:
- The exact runtime environment from that date
- The exact test suite state from that date
- Deterministic reproduction of all 17 missing artifacts

This is not achievable without time travel. Sprint 28 already performed the best-effort
reconstruction: 11 of 17 missing artifacts were reconstructed in sprint28/lanes/lane-b/ and
sprint28/lanes/lane-g/.

## Downstream Compliance (Sprints 28–30)

| Sprint | Evidence Contract Version | Status |
|--------|--------------------------|--------|
| Sprint 28 | V1 (37 categories, 36/37 PRESENT — 1 bootstrap discrepancy) | PASSED |
| Sprint 29 | V2 (45 categories, 46/46 tests pass) | PASSED |
| Sprint 30 | V3 (45 categories, BUNDLE_CONTRACT_PASSED) | PASSED |

Sprints 28–30 are compliant with their respective contract versions. The Sprint 27 gap does NOT
propagate downstream because Sprint 28 was designed specifically to document and close Sprint 27's
gaps, and Sprints 29–30 built progressively stronger contracts.

## Governance Disposition

Sprint 27 is classified as **HISTORICAL_NON_COMPLIANT** with the following exception applied:
- Exception type: PRE_CONTRACT_ERA_BUNDLE
- Evidence gap documented: YES (Sprint 28 Lane 0 audit)
- Best-effort reconstruction: YES (Sprint 28 Lane B — 11/17 artifacts)
- EV/ECC rules: Will NOT validate Sprint 27 retroactively
- Future sprints: Must not treat Sprint 27 as fully compliant without explicit exception note

See `historical-evidence-exception-policy.md` for the full governance policy.

## Conclusion

Weekly Review Item 6: **GOVERNANCE_EXCEPTION_REQUIRED — applied**
- Sprint 27 evidence status is no longer ambiguous.
- The failure is documented, classified, and governed.
- EV/ECC does not silently treat Sprint 27 as fully compliant.
