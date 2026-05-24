# Sprint 78 Evidence Audit — Sprint 79 Independent Review

**Date:** 2026-05-24
**Sprint:** 79 (REPAIR_SPRINT for Sprint 78 evidence authority)
**Auditor:** Sprint 79 internal adversarial review

---

## Sprint 78 Claims vs. Audit Findings

### 1. Canonical Validation Pass
**Sprint 78 claim:** `sprint78-final-validation-result.json` — `canonical_overall_valid=true`, `applicable_rules_passed=53`
**Audit verdict:** PARTIALLY_VERIFIED
**Detail:** The canonical file correctly identifies applicable rules and marks them passed. However, the companion `sprint78-bundle-validation-result.json` shows `overall_valid=false` with 55 failing rules, which confused independent reviewers. The canonical file lacked required Phase 1 fields: `applicable_rules_total`, `applicable_rules_failed`, `diagnostic_rules_are_non_blocking`, `reason_non_applicable`.

### 2. Failed Bundle Validation File
**Sprint 78 claim:** `sprint78-bundle-validation-result.json` is Phase A diagnostic run (non-applicable rules fail).
**Audit verdict:** CONTRADICTORY_OR_DIAGNOSTIC_MISLABELED
**Detail:** The file has `overall_valid=false`, 55 failed rules, and `bundle_type=FINISH_LINE_SPRINT`, but lacks `diagnostic_rules_are_non_blocking=true`. Independent reviewers cannot determine if failures are real blockers or non-applicable diagnostics. New EV Rule 110 (`diagnostic_bundle_file_has_nonblocking_label`) now requires this field.
**Repair:** Sprint 79 renames Sprint 78 Phase A content to `diagnostic-full-rules-non-applicable.json` with `diagnostic_rules_are_non_blocking=true` added.

### 3. ECC Closure Valid with Blocking Failure
**Sprint 78 claim:** `evidence-contract-computed.json` — `closure_valid=true`, `blocking_failures=1`
**Audit verdict:** CONTRADICTED
**Detail:** `closure_valid=true` while `blocking_failures=1` is a logical contradiction. The real EvidenceContractComputer sets `closure_valid = (blocking_failures == 0)`. The Sprint 78 file was hand-crafted to override this. EC27 detail explicitly says "File not found: reports/sprint78/evidence/evidence-contract-computed.json" — meaning the file was bootstrapped as PRESENT before it physically existed, resulting in a non-zero blocking count that was then ignored.
**Repair:** Sprint 79 uses two-pass ECC: write placeholder → run ECC → ECC finds placeholder → blocking_failures=0 → closure_valid=true (genuine). New EV Rule 109 (`ecc_closure_valid_only_if_no_blocking_failures`) now prevents this class of defect.

### 4. EC27 Self-Reference Bootstrap
**Sprint 78 claim:** EC27 bootstrapped as PRESENT per Sprint 75/76/77 precedent.
**Audit verdict:** NEEDS_REPAIR
**Detail:** The bootstrap procedure set `status=PRESENT` despite the file not existing at ECC computation time, introducing a phantom blocking_failures=1 that was then suppressed by manual `closure_valid=true`. The proper fix is two-pass computation: write a placeholder, run ECC, which finds the placeholder, producing genuine `blocking_failures=0`.
**Repair:** Sprint 79 ECC uses two-pass approach. `ecc-self-reference-policy.md` documents the policy.

### 5. Validator Test Results — Stale/Mislabeled
**Sprint 78 claim:** `validator-test-results.txt` proves Sprint 78 EV tests pass.
**Audit verdict:** STALE_OR_MISLABELED
**Detail:** The file is labeled "Sprint 77 Evidence Validator Test Results", reports 123 passed, and describes Sprint 77 new test details. Sprint 78 added 11 tests (TestSprint78PublicationTruthRules) bringing the total to 134 EV tests. The Sprint 78 file was a copy from Sprint 77 with stale content.
**Repair:** Sprint 79 captures a fresh EV test run confirming 142 tests (134 Sprint 78 + 8 new Sprint 79 tests for rules 109-110). `validator-test-count-authority.md` reconciles the count.

### 6. Pipeline Integration Proof — Insufficient
**Sprint 78 claim:** `pipeline-integration-proof.md` proves EvidenceValidator is wired into pipeline.
**Audit verdict:** INSUFFICIENT
**Detail:** The entire file was one sentence: "Evidence validator is wired in release-status command per Sprint 77 unchanged." This is an assertion, not a proof. It lacks source file paths, function names, command run, output, or diff.
**Repair:** Sprint 79 provides full `pipeline-integration-proof.md` with source path, function name, CLI argument, test evidence, and source hash.

### 7. Full Evidence Bundle ZIP — Missing
**Sprint 78 claim:** Sprint 78 evidence bundle is complete.
**Audit verdict:** MISSING
**Detail:** No ZIP bundle was provided. Individual loose files do not constitute an auditable bundle. Reviewers cannot confirm completeness, source integrity, or tamper-evidence.
**Repair:** Sprint 79 creates `bundles/sprint79-finish-line-evidence-<timestamp>.zip` with SHA256 manifest.

### 8. Publication Status
**Sprint 78 claim:** `LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL` — 42/42 examples published, README I/O approval-blocked.
**Audit verdict:** VERIFIED
**Detail:** `release-status` output confirms `all_merged=true`, `all_published=true`. No overclaim detected. Publication approval remains NOT_SET.

### 9. Handoff Status
**Sprint 78 claim:** `overall_handoff_valid=true`, 42/42 examples, 6/6 families.
**Audit verdict:** VERIFIED
**Detail:** `handoff-prepublish-validation.json` present with `overall_handoff_valid=true`. Handoff packages at `workspace/pr-dry-run/{family}-controlled-pilot/`.

### 10. Remote State
**Sprint 78 claim:** 6/6 repos accessible, `can_push=true` for all.
**Audit verdict:** VERIFIED
**Detail:** `remote-repo-state-before.json` shows 6/6 accessible. Sprint 79 refreshes remote state before any publication action.

---

## Sprint 79 Repair Summary

| Item | Sprint 78 Status | Sprint 79 Action |
|------|-----------------|-----------------|
| Canonical validation | PARTIALLY_VERIFIED | Add required Phase 1 fields to final-validation-result.json |
| Bundle validation file | CONTRADICTORY_OR_DIAGNOSTIC_MISLABELED | Rename to diagnostic-full-rules-non-applicable.json + add label |
| ECC closure_valid vs blocking_failures | CONTRADICTED | Two-pass ECC, new Rule 109 |
| EC27 self-reference bootstrap | NEEDS_REPAIR | Two-pass ECC policy, policy doc |
| Validator test results | STALE_OR_MISLABELED | Fresh EV test run, 142 tests |
| Pipeline integration proof | INSUFFICIENT | Full durable proof with source evidence |
| Evidence bundle ZIP | MISSING | Created at bundles/sprint79-*.zip |
| Publication status | VERIFIED | Carry forward |
| Handoff status | VERIFIED | Carry forward |
| Remote state | VERIFIED | Refreshed in Phase 6 |
