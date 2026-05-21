# EvidenceValidator Gap Analysis — Sprint 61

## Purpose

Documents the gaps in the Sprint 60 EvidenceValidator (12 rules) that allowed the Sprint 60
false-closure to pass validation. Sprint 61 adds 8 new semantic rules that close each gap.

---

## Sprint 60 Validator: 12 Original Rules

The Sprint 60 validator caught all Sprint 59 false-complete cases:

| Rule | SD59 Defect Closed |
|------|--------------------|
| final_clean_proof_after_final_commit | SD59-01 (dirty tree in proof) |
| no_present_no_authority | SD59-02 |
| readme_audit_content_based | SD59-03 (shallow audit) |
| readme_gate_implemented_and_tested | SD59-04 (gate not wired) |
| todo_all_items_checked_or_carried | SD59-06 (unchecked items) |
| evidence_validator_actually_ran | SD59-07 (hardcoded rules) |
| zero_unknown_input_formats | SD59-05 |
| test_log_zero_failed | — |
| commands_log_complete | — |
| bundle_min_files | — |
| destination_42_42_authority_mapped | — |
| no_partial_without_partial_verdict | — |

**Gap:** The 12 rules were sufficient for Sprint 59 defects but did not anticipate the new
failure modes introduced in Sprint 60.

---

## Sprint 60 False-Closure: 8 New Defects

### SD60-01: final-clean-proof.txt is 0 bytes

**Root cause:** `git status --short` produces no stdout when the repository is clean.
The capture command `git status --short 2>&1 | tee file.txt` wrote 0 bytes.
The Sprint 60 rule `final_clean_proof_after_final_commit` only checked for dirty indicators
(`modified:`, `?? `) in the file content — an empty file has no dirty indicators, so it passed.

**Gap in old rule:** Absence of evidence ≠ evidence of absence.
**New rules added:**
- `final_clean_proof_nonzero_bytes` — file must be >0 bytes
- `required_files_nonzero_size` — all required evidence files must be nonzero

### SD60-01 (content): final-clean-proof.txt lacks git header

**Root cause:** A nonzero file could be anything (log entry, typo, whitespace).
Valid clean proof must contain git's own output.

**New rule added:**
- `final_clean_proof_has_git_header` — must contain "On branch", "HEAD detached at",
  "nothing to commit", "nothing added to commit", "Changes to be committed", or "Initial commit"

**Fix for capture:** Use `git status` (not `--short`). Verbose output always starts with
"On branch <name>" + "nothing to commit, working tree clean" when clean.

### SD60-02: README MATCH without I/O format documentation

**Root cause:** `content_audit=MATCH` was assigned based on `family_in_readme`,
`workflow_type_in_readme`, and `package_id_in_readme` only. The audit tracked
`input_format_in_readme` and `output_format_in_readme` but these fields were never gated.
Result: 22/42 `input_format_in_readme=false`, 23/42 `output_format_in_readme=false`,
yet `match=42/42` was claimed.

**Gap in old rule:** `readme_audit_content_based` checked for presence of content fields
but did not validate that I/O fields were true or that MATCH was conditional on them.

**New rule added:**
- `readme_io_format_not_falsely_complete` — if >30% records have I/O fields false AND
  match=100% is claimed, this is a false-completion contradiction.

### SD60-03: README gate is standalone-only (not wired in pipeline)

**Root cause:** `readme_audit_gate.py` was created and tested but never imported by any
pipeline command. The Sprint 60 rule `readme_gate_implemented_and_tested` checked for:
- `readme-gate-implementation.md`
- `readme-gate-test-results.txt`
- `readme-gate-source-proof.patch`

These files document the module but do not prove it is called by the pipeline.
The `next-work-register.md` admitted this was a P1 open item.

**Gap in old rule:** Evidence of a module ≠ evidence that the module is used.

**New rule added:**
- `readme_gate_wired_in_pipeline` — two-tier check:
  1. If `source_root` provided: scan Python files for `readme_audit_gate` imports
  2. Fallback: require `readme/readme-gate-flow-integration.md` (must not contain
     "not wired", "deferred", or "p1")

### SD60-04: EvidenceValidator is standalone-only (not wired in pipeline)

**Root cause:** Same pattern as SD60-03. `evidence_validator.py` was created and tested
but never imported by `__main__.py` or any pipeline command.

**New rule added:**
- `evidence_validator_wired_in_pipeline` — two-tier check:
  1. If `source_root` provided: scan for `evidence_validator` imports
  2. Fallback: require `evidence/pipeline-integration-proof.md`

### SD60-05: Destination Program.cs input format = null for all 42

**Root cause:** `content-audit-repaired.json` showed `input_format_in_programcs=null`
for all 42/42 records. No actual Program.cs files were parsed for input format usage.
The audit only checked for file existence and `api_type_in_programcs`.

**Gap in old rule:** No rule validated that Program.cs parsing actually happened.

**New rule added:**
- `destination_programcs_input_not_all_null` — if all records have null for both
  `input_format_in_programcs` and `input_classification`, the audit is incomplete.

### SD60-08: P1 open items coexist with COMPLETE verdict

**Root cause:** `process/next-work-register.md` listed 2 P1 items (README gate CLI wiring,
EvidenceValidator CLI wiring) while the final verdict claimed
`LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED`.

P1 = blocking. A sprint cannot be VERIFIED if P1 items remain open.

**New rule added:**
- `no_p1_items_with_complete_verdict` — scans `process/next-work-register.md` for lines
  matching `\bP1\b` that are not marked DONE/COMPLETE/RESOLVED. If found AND final verdict
  claims COMPLETE/VERIFIED/GATES_ACTIVE, this is a blocking contradiction.

---

## Sprint 60 Bundle Validation Result (with 20-rule validator)

```
overall_valid=False, passed=13, failed=7
```

| Rule | Result | Sprint 60 Defect |
|------|--------|-----------------|
| final_clean_proof_nonzero_bytes | **FAIL** | SD60-01 |
| final_clean_proof_has_git_header | **FAIL** | SD60-01 |
| readme_io_format_not_falsely_complete | **FAIL** | SD60-02 |
| readme_gate_wired_in_pipeline | PASS (source_root scan found import) | — |
| evidence_validator_wired_in_pipeline | **FAIL** | SD60-04 |
| destination_programcs_input_not_all_null | **FAIL** | SD60-05 |
| no_p1_items_with_complete_verdict | **FAIL** | SD60-08 |
| required_files_nonzero_size | **FAIL** | SD60-01 contributory |

Note: `readme_gate_wired_in_pipeline` passes because the source_root scan finds that
`__main__.py` was wired during Sprint 61 Phase 5. The Sprint 60 bundle itself did not
have wiring — this is a Sprint 61 repair artifact. The evidence-based fallback
(`readme-gate-flow-integration.md`) did not exist in the Sprint 60 bundle.

---

## Summary

Sprint 60 EvidenceValidator: 12 rules → caught SD59 defects, missed SD60 defects.
Sprint 61 EvidenceValidator: 20 rules → catches both SD59 and SD60 defects.

The Sprint 60 bundle fails 7/20 rules under the new validator.
Sprint 60 is reclassified as `EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED`.
