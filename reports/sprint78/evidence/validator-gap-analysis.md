# Sprint 78 Validator Gap Analysis

**Date:** 2026-05-24
**Sprint:** 78 (FINISH_LINE_SPRINT)
**Previous EV rule count:** 105 (after Sprint 77)

---

## Gap Analysis

### Gap S77-D1: publication-truth-matrix stub can overclaim REMOTE_STALE when examples are published

**Observed defect:** commands.log Phase 8 stub said "42 examples, all REMOTE_STALE_LOCAL_HANDOFF_READY_APPROVAL_BLOCKED" but the actual release-status showed `all_published=true, all_merged=true`. This is a false assertion — if all examples are published and merged, no family should be labeled REMOTE_STALE.

**New rule:** `publication_truth_no_stale_remote_claimed` (Rule 106)
- Checks: if `all_published=true AND all_merged=true` in publication-truth-matrix-final.json, no family entry may have status containing "REMOTE_STALE"
- Applicable when: `all_published: true` and `all_merged: true` are set in the matrix
- Passes trivially when: these fields are absent or false (not applicable)

### Gap S77-D2: handoff validation result may be missing or show invalid flag

**Observed gap:** No EV rule required `handoff/handoff-prepublish-validation.json` to explicitly assert `overall_handoff_valid: true`. A missing or absent flag would pass undetected.

**New rule:** `handoff_validation_result_has_valid_flag` (Rule 107)
- Checks: if `handoff/handoff-prepublish-validation.json` exists, it must have `overall_handoff_valid: true`
- Passes trivially when: file is absent (not applicable)

### Gap S77-D3: remote repo state may show blocked repos without detection

**Observed gap:** No EV rule verified that all repos in `remote/remote-repo-state-before.json` are accessible. A blocked repo would only be surfaced by reading the file manually.

**New rule:** `remote_repo_state_all_accessible` (Rule 108)
- Checks: if `remote/remote-repo-state-before.json` exists, `summary.accessible == summary.total_checked`
- Fails when: any repos are blocked or total_checked=0
- Passes trivially when: file is absent (not applicable)

---

## Summary

| Rule | ID | Gap Closed | Severity |
|------|----|-----------|---------|
| publication_truth_no_stale_remote_claimed | 106 | S77-D1 | FAILURE |
| handoff_validation_result_has_valid_flag | 107 | S77-D2 | FAILURE |
| remote_repo_state_all_accessible | 108 | S77-D3 | FAILURE |

**New total EV rules: 108** (105 → +3)

---

## Test Coverage

Added `TestSprint78PublicationTruthRules` class with 11 tests (3-4 per new rule).
All 134 EV tests pass.
