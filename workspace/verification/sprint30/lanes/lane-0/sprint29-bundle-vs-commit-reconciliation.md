# Sprint 29 Bundle vs. Commit Reconciliation

**Lane:** lane-0
**Sprint:** sprint30
**Date:** 2026-05-17
**Subject:** Explain why Sprint 29 bundle git-log-proof starts at 20686d3, not ef74d9b

## The Discrepancy

The Sprint 29 evidence bundle (`sprint29-live-publication-and-evidence-contract-v2-finalization-20260517-174956.zip`) contains a `git-log-proof.txt` whose most recent entry is `20686d3` — the Sprint 28 HEAD commit. It does NOT contain `4be32c1` or `ef74d9b` (the two Sprint 29 commits).

## Root Cause: Bootstrap Pattern (Expected)

The bundle was built **inside** the Sprint 29 execution, before the final Sprint 29 commits were made. The execution sequence is:

```
[Sprint 29 execution starts]
  → Lane A-F lanes executed → evidence JSON files written
  → Lane TEST: 1662 tests run, test-summary.json captured
  → Lane BUNDLE: bundle ZIP assembled from all lane evidence
  → Lane BUNDLE: git log captured → shows 20686d3 as HEAD (Sprint 29 not yet committed)
  → Lane BUNDLE: git-log-proof.txt written INTO the bundle
  ↓
[COMMIT 1 — 4be32c1]
  → src/plugin_examples/evidence_contract.py (StrictEvidenceContractV2)
  → tests/unit/test_evidence_contract.py (46 tests)
  → All sprint29 lane files
  → bundle-contract-definition.json
↓
[COMMIT 2 — ef74d9b]
  → sprint29-live-publication-and-evidence-contract-v2-finalization-20260517-174956.zip (the bundle itself)
  → bundle-contract-validation-report.json
  → changed-files.txt, git-status-final.txt, git-diff-final.patch
  → final-state-summary.yaml, final-verdict.md
```

The bundle ZIP is added to git in commit `ef74d9b`. At the time the ZIP was assembled, commit `4be32c1` had not yet occurred — so neither Sprint 29 commit can appear inside the bundle's git-log-proof.

## This Is Expected — Not a Defect

This is the same bootstrap pattern documented in Sprint 29's own Lane 0 reconciliation for Sprint 28:

> "Bundle is built before final commit — expected pattern."
> — `workspace/verification/sprint29/lanes/lane-0/sprint28-bundle-vs-commit-reconciliation.md`

The pattern recurs every sprint because the bundle is always assembled as part of the sprint execution, before the sprint is committed.

## Verification That Sprint 29 Work IS Committed

The Sprint 29 work is provably present in git:

| Item | Evidence |
|------|---------|
| StrictEvidenceContractV2 implementation | `src/plugin_examples/evidence_contract.py` in commit `4be32c1` |
| 46 v2 evidence contract tests | `tests/unit/test_evidence_contract.py` in commit `4be32c1` |
| All sprint29 lane JSON files | committed in `4be32c1` |
| Evidence bundle ZIP (49 files, 45,314 bytes) | committed in `ef74d9b` |
| BUNDLE_CONTRACT_PASSED validation report | `bundle-contract-validation-report.json` in `ef74d9b` |
| Sprint 28 HEAD (20686d3) is ancestor of Sprint 29 HEAD | confirmed via `git log` ancestry chain |

## Sprint 30 V3 Classification

For `StrictEvidenceContractV3`, the bundle bootstrap discrepancy is classified as:

- **CATEGORY**: `BOOTSTRAP_PATTERN_EXPECTED`
- **SEVERITY**: `NON_BLOCKING`
- **REQUIRED_V3_CHECK**: The v3 contract must verify that Sprint 30's two sprint commits (`lane-0/sprint30-commit-proof.json`) appear in the post-commit git log — not inside the bundle's own git-log-proof, but in the repository HEAD at the time Lane BUNDLE runs.
- **CLASSIFICATION**: `BUNDLE_GIT_LOG_STOPS_AT_SPRINT_START_BOOTSTRAP_EXPECTED`

## Conclusion

The sprint29 bundle git-log-proof starting at `20686d3` is **expected and correct**. It does not indicate missing work. All Sprint 29 deliverables (StrictEvidenceContractV2, 46 tests, lane evidence, bundle ZIP) are committed to the repository at commits `4be32c1` and `ef74d9b`. These two commits have been verified as HEAD and HEAD~1 respectively at Sprint 30 lane-0 execution time.
