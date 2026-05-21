# Evidence Validator Gap Analysis — Sprint 60 Phase 5

**Sprint:** sprint60-sprint59-closure-repair-destination-readme-gate-20260521
**Date:** 2026-05-21
**Author:** Sprint 60 independent review

---

## 1. Sprint 59 False-Complete Root Cause

Sprint 59 closed with `IO_AUTHORITY_COMPLETE_DESTINATION_CONTENT_VERIFIED` but was found to have
7 blocking defects (SD59-01 through SD59-07). The evidence validator that ran in Sprint 59
hardcoded its `validation_rules_passed` list rather than actually evaluating the evidence bundle.
This allowed a false-complete bundle to produce a passing validator result.

---

## 2. Defect Classification

| Defect | Description | Validator Rule Added |
|--------|-------------|----------------------|
| SD59-01 | git-status.txt captured BEFORE final bundle commit — showed 7 dirty files | `final_clean_proof_after_final_commit` |
| SD59-02 | 39/42 destination content (3 PRESENT_NO_AUTHORITY) claimed as 42/42 | `destination_42_42_authority_mapped`, `no_present_no_authority` |
| SD59-03 | README audit was presence/size only — not content-based | `readme_audit_content_based` |
| SD59-04 | README gate documented but not implemented or wired into publication flow | `readme_gate_implemented_and_tested` |
| SD59-05 | Root README version gaps (Words/Diagram) not classified or policy-documented | (classified in root-readme-content-audit.json, policy in readme-validator-policy.md) |
| SD59-06 | todo.md had unchecked `[ ]` items throughout all phases | `todo_all_items_checked_or_carried` |
| SD59-07 | `validation_rules_passed` was a hardcoded list, not the result of running rules | `evidence_validator_actually_ran` |

---

## 3. New Validation Rules (Sprint 60)

### Rule 1: `final_clean_proof_after_final_commit`
- **What it checks:** `git/final-clean-proof.txt` must exist and must NOT contain dirty
  indicators (`modified:`, `untracked files:`, `?? `).
- **Sprint 59 gap it closes:** SD59-01 — git status was captured before the final commit
  (showed 7 modified workspace files).
- **Test:** `test_fails_when_final_clean_proof_shows_dirty_state`

### Rule 2: `destination_42_42_authority_mapped`
- **What it checks:** `destination/content-audit-repaired.json` must show `authority_mapped=42/42`
  and `present_no_authority=0`.
- **Sprint 59 gap it closes:** SD59-02 — Sprint 59 had 3 PRESENT_NO_AUTHORITY cases.
- **Test:** `test_fails_when_present_no_authority_exists`

### Rule 3: `no_present_no_authority`
- **What it checks:** No example record may have `content_match == "PRESENT_NO_AUTHORITY"`.
- **Sprint 59 gap it closes:** SD59-02 (secondary check).
- **Test:** `test_fails_when_present_no_authority_exists`

### Rule 4: `no_partial_without_partial_verdict`
- **What it checks:** If any PARTIAL entries exist in the content audit, the final verdict
  must explicitly acknowledge them.
- **Sprint 59 gap it closes:** SD59-02 partial — 1/42 PARTIAL was not properly classified.
- **Test:** (integration test in `test_sprint59_style_bundle_detected_as_invalid`)

### Rule 5: `readme_audit_content_based`
- **What it checks:** `readme/example-readme-content-audit.json` must have records with at
  least one of: `workflow_type_in_readme`, `family_in_readme`, `package_id_in_readme`,
  `content_audit`. Presence+size-only records are detected as shallow.
- **Sprint 59 gap it closes:** SD59-03 — Sprint 59 README audit was size/presence only.
- **Test:** `test_fails_when_readme_audit_is_shallow`

### Rule 6: `readme_gate_implemented_and_tested`
- **What it checks:** Three evidence files must exist:
  1. `readme/readme-gate-implementation.md`
  2. `readme/readme-gate-test-results.txt` (must show passing tests)
  3. `readme/readme-gate-source-proof.patch`
- **Sprint 59 gap it closes:** SD59-04 — Gate was documented but not wired into publication.
- **Test:** `test_fails_when_readme_gate_evidence_missing`

### Rule 7: `evidence_validator_actually_ran`
- **What it checks:** `evidence/validator-test-results.txt` must exist and contain pytest-style
  output (`\d+ passed`, `PASSED`, or `passed in`). A hardcoded rules list does NOT qualify.
- **Sprint 59 gap it closes:** SD59-07 — `validation_rules_passed` was a hardcoded list.
- **Detection:** The Sprint 59 format `validation_rules_passed:\n- rule_id\n...` does NOT match
  any of the required pytest patterns.
- **Test:** `test_fails_when_output_not_test_output`

### Rule 8: `todo_all_items_checked_or_carried`
- **What it checks:** `todo.md` must have zero `^- \[ \]` patterns (unchecked items).
- **Sprint 59 gap it closes:** SD59-06 — All phases had unchecked items despite work done.
- **Test:** `test_fails_when_todo_has_unchecked_items`

### Rules 9-12 (inherited from Sprint 59, now actually enforced):
- `zero_unknown_input_formats` — checks io-authority matrix, 0 unknown
- `test_log_zero_failed` — lanes/lane-I/test-run.log must exist, show 0 failed
- `commands_log_complete` — commands.log must not contain `IN_PROGRESS`
- `bundle_min_files` — ≥35 files in bundle directory

---

## 4. Test Coverage Summary

| Test Class | Tests | All Pass |
|-----------|-------|---------|
| TestFinalCleanProof | 3 | YES |
| TestPresentNoAuthority | 2 | YES |
| TestReadmeAuditContentBased | 3 | YES |
| TestReadmeGateImplemented | 3 | YES |
| TestTodoAllChecked | 3 | YES |
| TestEvidenceValidatorActuallyRan | 3 | YES |
| TestCommandsLog | 2 | YES |
| TestTestLog | 2 | YES |
| TestUnknownInputFormats | 2 | YES |
| TestCompleteBundle | 4 | YES |
| **Total** | **27** | **27/27** |

---

## 5. Sprint 59 Bundle Verdict Under New Rules

If the Sprint 59 bundle were evaluated against the new `EvidenceValidator` rules:

| Rule | Sprint 59 Result | Reason |
|------|-----------------|--------|
| final_clean_proof_after_final_commit | **FAIL** | Proof shows 7 modified files (captured pre-commit) |
| destination_42_42_authority_mapped | **FAIL** | present_no_authority=3 |
| no_present_no_authority | **FAIL** | 3 PRESENT_NO_AUTHORITY entries |
| no_partial_without_partial_verdict | **FAIL** | 1 PARTIAL not in verdict |
| readme_audit_content_based | **FAIL** | Records have only readme_present/readme_size |
| readme_gate_implemented_and_tested | **FAIL** | No source-proof.patch exists |
| evidence_validator_actually_ran | **FAIL** | validation_rules_passed was hardcoded list |
| todo_all_items_checked_or_carried | **FAIL** | 8+ unchecked items remain |
| zero_unknown_input_formats | PASS | 0 unknown |
| test_log_zero_failed | PASS | 2826 passed, 0 failed |
| commands_log_complete | PASS | No IN_PROGRESS in log |
| bundle_min_files | PASS | 81 files |

**Sprint 59 would score: 4/12 rules pass, 8/12 FAIL → overall_valid=False**

---

## 6. Source Files

| File | Description |
|------|-------------|
| `src/plugin_examples/evidence_validator.py` | New EvidenceValidator module (584 lines) |
| `tests/unit/test_evidence_validator.py` | 27 tests covering all Sprint 59 failure modes |
| `reports/sprint60/evidence/validator-test-results.txt` | Actual pytest run output |
| `reports/sprint60/evidence/validator-hardening-source-proof.patch` | Source diff (1030 lines) |
