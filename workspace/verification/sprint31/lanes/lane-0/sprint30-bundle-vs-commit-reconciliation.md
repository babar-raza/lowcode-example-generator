# Sprint 30 Bundle vs. Commit Reconciliation — Sprint 31 Lane 0

**Date:** 2026-05-17
**Subject:** Sprint 30 contradiction resolution

## Sprint 30 Bundle Contents — What Was Claimed

Sprint 30 bundle `sprint30-live-publication-pr3-pr9-package-cleanup-and-evidence-contract-v3-20260517-205506.zip`:
- 58 files
- `bundle-contract-validation-report.json`: passed=true, 45/45 categories, BUNDLE_CONTRACT_PASSED
- `test-summary.json`: 1682/1682 tests passing

## The Contradiction (Sprint 30 Internal Error)

Sprint 30's `pdf-pr7-final-package-audit.json` listed:
```json
"examples": ["form-flattener"]
```

But the **actual** `workspace/pr-dry-run/pdf-controlled-pilot-pr7/` directory has ALWAYS contained:
- `examples/pdf/lowcode/form-flattener/`
- `examples/pdf/lowcode/security/`

This was established in Sprint 23 commit `8dce137`:
> "Wave E (Security + FormFlattener): both ALL_PASS via template_first generation."

## Why the Contract Passed Despite the Error

`StrictEvidenceContractV3` validates **category presence and content-level checks** but does NOT validate the **contents of per-PR audit JSON files**. Specifically, v3 does not:
- Parse `examples` lists from per-PR audit files
- Cross-check PR example counts against scoreboards
- Verify Security is listed in any PR audit

This is the gap that `StrictEvidenceContractV4` must close.

## Sprint 30 Commit State (Verified)

- `e379cdf` (HEAD): Bundle ZIP
- `8094a46` (HEAD~1): StrictEvidenceContractV3, test suite, 249 bin/obj deletions, all evidence
- Both source changes (evidence_contract.py, test_evidence_contract.py) ARE committed
- PR#8 and PR#9 bin/obj deletions ARE committed
- No uncommitted source/test/config changes in working tree

## Sprint 31 Fix

The fix is entirely in evidence artifacts, not in packages:
1. Correct PR#7 audit: `examples: ["security", "form-flattener"]`, `total_files: 9`
2. Correct PDF closeout matrix: `total_pr_dry_run_ready: 14`
3. Add StrictEvidenceContractV4 to validate example counts
4. Re-audit all 6 packages with correct counts

No package modifications are required. No Security recovery is needed. Security is present, clean, and always has been.
