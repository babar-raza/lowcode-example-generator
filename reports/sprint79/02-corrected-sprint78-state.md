# Corrected Sprint 78 State

**Date:** 2026-05-24
**Sprint:** 79

## What Sprint 78 Got Right

- **42/42 examples published** — all_merged=true confirmed by release-status
- **6/6 remote repos accessible** — verified via resolve-repo-access
- **108 EV rules active** — rules 106-108 correctly added
- **3075 tests pass** — confirmed post-commit
- **Handoff valid** — 6/6 families, overall_handoff_valid=true
- **Weekly review items classified** — all 6 items have classification labels
- **FormImporter carry-forward** — STILL_BLOCKED with durable retest trigger
- **Words version drift documented** — drift=REMOTE_DRIFT, approval-blocked
- **Sprint 27 governance classified** — PRE_CONTRACT_ERA_BUNDLE exception

## What Sprint 78 Got Wrong (Evidence Authority Defects)

### S78-E1: ECC contradiction — closure_valid=true AND blocking_failures=1
**Root cause:** EC27 was bootstrapped as PRESENT before the file physically existed. The real ECC computation returned blocking_failures=1 (EC27 file not found). The bootstrap note recorded "File not found" but set status=PRESENT. The aggregation produced blocking_failures=1 but closure_valid was then manually overridden to true.
**Impact:** Any audit tool checking `if blocking_failures > 0 then closure_valid must be false` would correctly flag this as a lie.
**Sprint 79 fix:** Two-pass ECC (write placeholder → run ECC → ECC finds placeholder → genuine blocking_failures=0). New EV Rule 109 prevents this class of defect going forward.

### S78-E2: Diagnostic bundle file not labeled as non-blocking
**Root cause:** `sprint78-bundle-validation-result.json` had `overall_valid=false` and `bundle_type=FINISH_LINE_SPRINT`, but lacked `diagnostic_rules_are_non_blocking=true`. Independent reviewers cannot distinguish this from a genuine failure file.
**Impact:** The external review identified this as a contradiction requiring repair.
**Sprint 79 fix:** The Sprint 78 Phase A content is preserved as `diagnostic-full-rules-non-applicable.json` in Sprint 79's evidence folder with `diagnostic_rules_are_non_blocking=true` added. Sprint 79's own `sprint79-bundle-validation-result.json` includes this field from the start. New EV Rule 110 enforces this for all future sprints.

### S78-E3: Validator test results stale (Sprint 77 labeled)
**Root cause:** `validator-test-results.txt` was copied from Sprint 77 without updating Sprint, test count, or new test names. It claims 123 tests but Sprint 78 added 11 more (total 134).
**Impact:** Breaks durable evidence chain — cannot independently verify Sprint 78 rule additions from the test evidence.
**Sprint 79 fix:** Fresh test run captured, 142 EV tests (134 Sprint 78 + 8 Sprint 79). `validator-test-count-authority.md` traces the lineage.

### S78-E4: Pipeline integration proof is a one-line assertion
**Root cause:** The single-line proof was an assertion, not durable evidence. Source path, function name, and CLI argument were not documented.
**Impact:** Cannot independently verify validator wiring from the evidence file alone.
**Sprint 79 fix:** Full proof with source path (`src/plugin_examples/__main__.py:1477`), function signature, CLI argument (`--validate-bundle`), and source map.

### S78-E5: No evidence bundle ZIP
**Root cause:** Sprint 78 provided loose files only. No ZIP bundle with SHA256 manifest was created.
**Impact:** Cannot confirm completeness or detect file tampering.
**Sprint 79 fix:** `bundles/sprint79-finish-line-evidence-<timestamp>.zip` created with SHA256 manifest.

## Corrected Sprint 78 Verdicts

All five defects above are repair items. The Sprint 78 publication verdict remains unchanged:
- **Evidence verdict:** REPAIRED_IN_SPRINT79
- **Publication verdict (unchanged):** `LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL`
- Sprint 78 is NOT accepted until Sprint 79 evidence repair is accepted.
