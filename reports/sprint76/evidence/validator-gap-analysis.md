# Validator Gap Analysis — Sprint 76

**Date:** 2026-05-24
**Purpose:** Identify gaps in Sprint 75 EV rules that allowed defects S75-B1 and S75-B2 to pass.

---

## Sprint 75 Defects That Passed EV/ECC

### Defect S75-B1 — Slides Compress Overclaim

**What passed:** EV rule 90 (`email_slides_runtime_validated`)
**What it checked:** post-merge-validation-matrix.json exists with at least one `post_merge_validated: true` record
**What it MISSED:** Whether `output_confirmed` was also `true`. Rule 90 only checked for the presence of validated records — it did not verify that compression actually occurred.

**Gap:** No rule checked that `post_merge_validated=true` implies `output_confirmed=true`.
**Fix:** Rules 94 and 95 now enforce this invariant.

### Defect S75-B2 — Dirty-State Documentation Inconsistency

**What passed:** EV rule 91 (`dirty_tree_classified`)
**What it checked:** `git/dirty-file-classification.md` exists with >50 chars of content
**What it MISSED:**
- Whether `dirty-file-classification.md` was internally consistent with `dirty-state-after.txt`
- Whether `dirty-state-after.txt` showed source/test files modified (which it did)
- Whether `final-clean-proof.txt` contained a verifiable commit SHA

**Gap 1:** No rule cross-referenced dirty-state-after.txt against dirty-file-classification.md.
**Fix:** Rule 96 checks that if dirty-state-after.txt shows src/tests modified, the classification must acknowledge it.

**Gap 2:** No rule checked that dirty-state-after.txt was captured AFTER the final commit (i.e., src/tests must be clean).
**Fix:** Rule 100 rejects dirty-state-after.txt that shows src/ or tests/ as modified.

**Gap 3:** No rule required a verifiable commit SHA in final-clean-proof.txt.
**Fix:** Rule 97 requires at least one 7-character hex SHA in the proof.

---

## Sprint 76 Rule Additions (94-101)

| Rule # | Rule ID | What It Catches |
|--------|---------|----------------|
| 94 | `runtime_matrix_output_confirmed_for_validated` | post_merge_validated=true without output_confirmed=true |
| 95 | `runtime_matrix_no_graceful_exit_labelled_validated` | NO_INPUT_FIXTURE runtime_result while post_merge_validated=true |
| 96 | `dirty_classification_must_match_after_snapshot` | dirty-file-classification.md says no src/test dirty while dirty-state-after.txt shows them modified |
| 97 | `final_clean_proof_contains_commit_sha` | final-clean-proof.txt lacks a verifiable commit SHA |
| 98 | `final_clean_proof_documents_remaining_dirty` | workspace/verification/latest dirty files not acknowledged in proof |
| 99 | `weekly_review_no_repaired_while_output_unconfirmed` | weekly review claims REPAIRED while matrix has output_confirmed=false |
| 100 | `dirty_after_no_uncommitted_source_test` | dirty-state-after.txt shows src/ or tests/ as modified (not committed) |
| 101 | `final_verdict_workspace_exception_explicit` | workspace/verification/latest dirty but not named in final verdict |

---

## Sprint 76 Revalidation of Sprint 75

Sprint 75 bundle fails 4 of 8 new rules:
- Rule 94: FAIL (slides-compress output_confirmed=false)
- Rule 95: FAIL (slides-compress NO_INPUT_FIXTURE)
- Rule 96: FAIL (dirty-state-after vs classification contradiction)
- Rule 100: FAIL (dirty-state-after shows evidence_validator.py modified)

Rules 97, 98, 99, 101 pass on sprint75 (the final-clean-proof has SHA pattern b2a2748, etc.)

Sprint 76 bundle passes all 101 rules.
