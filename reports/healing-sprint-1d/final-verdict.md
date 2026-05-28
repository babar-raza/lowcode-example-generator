# Healing Sprint 1D -- Final Verdict

**Sprint:** Healing Sprint 1D
**Date:** 2026-05-27
**Type:** Archive rebuild only (not a product sprint, not Healing Sprint 2)

---

## Verdict

**LOWCODE_MACHINERY_HEALING_ACCEPTED**

---

## Summary

Healing Sprint 1D rebuilds the Sprint 1C evidence ZIP to fix 4 archive defects in the
uploaded `healing-sprint-1c-evidence-20260527.zip`. All Sprint 1C machinery results are
carried forward unchanged.

### Uploaded 1C ZIP Defects (Corrected in 1D)

| # | Defect | Fix |
|---|---|---|
| 1 | `bundle-manifest.json` `file_count: 0` inside ZIP | 1D manifest: `file_count` = actual ZIP entry count |
| 2 | `head_sha` = step-2 SHA, final HEAD was `abeea0e` | 1D manifest: documents full SHA chain |
| 3 | `final-clean-proof.txt` shows step-1/2 style, placeholder wording | 1D proof: shows actual HEAD `abeea0e`, clean git state |
| 4 | `commands.log` contains `SHA=TBD_STEP3` | 1D commands.log: all SHAs real, no TBD |

### Sprint 1D: Supersedes Uploaded 1C ZIP

The uploaded `healing-sprint-1c-evidence-20260527.zip` is superseded by:
`reports/healing-sprint-1d/bundles/healing-sprint-1d-final-archive-evidence-20260527.zip`

### Carried Forward from Sprint 1C (Unchanged)

| Category | Result |
|---|---|
| Sprint 1C verdict | LOWCODE_MACHINERY_HEALING_ACCEPTED |
| Sprint 1B ECC (inherited) | 25/25 PRESENT, closure_valid=true, blocking_failures=0 |
| Sprint 1C ECC | 17/17 PRESENT, closure_valid=true |
| Canonical validation | canonical_overall_valid=true, applicable_rules_failed=0 |
| Replay automation | 7 PASS, 0 FAIL, 2 SKIP |
| Gate simulation | prs=0, merges=0, remote mutations=0 |
| Dry run | 41 PR candidates, 42 truth records, 6 families |
| Validator rules | 145 |

---

## Publication Gate

- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT_SET (APPROVAL_BLOCKED)
- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET (APPROVAL_BLOCKED)

## Healing Sprint 2

**NOT RECOMMENDED.** No new machinery defects. Archive defects corrected by Sprint 1D.
