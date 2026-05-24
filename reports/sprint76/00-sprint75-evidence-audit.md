# Sprint 75 Evidence Audit — Independent Review Findings

**Audit Date:** 2026-05-24
**Auditor:** Sprint 76 (independent review of evd(3).zip)
**Sprint 75 Commits:** b2a2748 (bundle) → 278c528 (final-clean-proof)

---

## Accepted Progress (Sprint 75 Items Verified)

| Item | Sprint 75 Claim | Audit Result |
|------|----------------|--------------|
| PDF publication truth | 14 blocked claim is historical, all 19 PDF examples now remotely present | VERIFIED |
| FormImporter upstream bug | Aspose.PDF 26.5.0 NullRef tracked as BLOCKED_EXTERNAL | VERIFIED |
| Words version drift | Remote=26.4.0, handoff=26.5.0, repair approval-blocked | VERIFIED |
| Email Converter runtime | Build+run PASS, output confirmed (input.html) | VERIFIED |
| Slides Convert runtime | Build+run PASS, output confirmed (64837 bytes PDF) | VERIFIED |
| Slides Merger runtime | Build+run PASS, output confirmed (42020 bytes PPTX) | VERIFIED |
| Sprint 27 governance | PRE_CONTRACT_ERA_BUNDLE, Historical Exception Policy v1.0 applied | VERIFIED |
| EV rules | 93/93 PASS, 8 new rules 86-93 | VERIFIED |
| ECC categories | 46/46 PRESENT, closure_valid=true | VERIFIED |
| Tests | 3041/3041 PASS, 3 skipped, 0 failed | VERIFIED |

---

## Sprint 75 Closure Blockers Found

### Blocker 1 — Slides Compress Overclaim

**Location:** `post-merge-runtime/post-merge-validation-matrix.json`

The matrix records `slides-compress` with:
- `post_merge_validated: true`
- `output_confirmed: false`
- `runtime_result: "RUNTIME_VALIDATED_NO_INPUT_FIXTURE"`

**Evidence:** `post-merge-runtime/slides-runtime-validation.txt` confirms:
> "dotnet run → exit 0 / stdout: 'Input file not found: input.pptx'"

No compression was performed. No output.pptx was produced. The program exited cleanly
because of a missing-input guard, not because compression succeeded.

**Contradiction:**
- `post_merge_validated: true` implies the example's functionality was post-merge validated.
- But `output_confirmed: false` and `runtime_result: RUNTIME_VALIDATED_NO_INPUT_FIXTURE`
  mean the compression API was never actually called.
- Weekly Review Item 4 was classified as fully "REPAIRED" when it is only partially repaired
  for Slides Compress.

**Required Fix:** Run Slides Compress with a real `.pptx` fixture, confirm output.pptx produced,
update matrix to `RUNTIME_VALIDATED` with `output_confirmed: true`.

### Blocker 2 — Dirty-State Documentation Inconsistency

**Contradiction between two documents:**

`reports/sprint75/git/dirty-state-after.txt` shows:
```
modified: src/plugin_examples/evidence_validator.py
modified: tests/unit/test_evidence_validator.py
```

`reports/sprint75/git/dirty-file-classification.md` states:
> "No Source or Test Files Are Dirty"
> "No modifications to `src/plugin_examples/evidence_validator.py`"

**What actually happened:**
- `dirty-state-after.txt` captured the state DURING sprint75 work, before the bundle commit.
  At that moment, evidence_validator.py and test files were uncommitted/modified.
- `dirty-file-classification.md` was written separately and said no source/test were dirty
  — contradicting the snapshot.
- The source/test changes WERE committed in b2a2748 (confirmed by `git show --stat b2a2748`).
- Current `git status --short` only shows workspace/verification/latest/ files — consistent
  with source/test having been committed.

**Impact:** The two sprint75 documents are internally inconsistent.
`final-clean-proof.txt` correctly states source/test were committed, but the contradicting
documents undermine the audit trail.

**Required Fix:** Sprint 76 must document this accurately and ensure sprint76 dirty-state
documents are internally consistent.

### Consequence: EV/ECC Passed Despite Contradictions

Sprint 75 added rule 90 (`email_slides_runtime_validated`) which checks that the
post-merge validation matrix has records — but does NOT verify:
- That `output_confirmed: true` for each validated example
- That `post_merge_validated: true` implies real end-to-end output was produced
- That `RUNTIME_VALIDATED_NO_INPUT_FIXTURE` is not counted as fully validated

Sprint 75 added rule 91 (`dirty_tree_classified`) which checks that
`git/dirty-file-classification.md` exists and has content — but does NOT verify:
- That the classification matches what is actually shown in dirty-state-after.txt
- That source/test dirty claims are cross-checked against the staging plan

These gaps are addressed in Sprint 76 Phase 4 (EV/ECC hardening).

---

## Final Sprint 75 Verdict Status

The sprint 75 verdict `LOWCODE_WEEKLY_REVIEW_ITEMS_CLASSIFIED_PUBLICATION_APPROVAL_BLOCKED`
is **too strong** given the Slides Compress partial validation and dirty-state contradiction.
The correct assessment is PARTIALLY_VERIFIED pending Sprint 76 repairs.

Sprint 75 is reopened and Sprint 76 will either confirm or repair each blocker.
