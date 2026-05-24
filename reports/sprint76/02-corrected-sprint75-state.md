# Corrected Sprint 75 State

**Date:** 2026-05-24
**Purpose:** Document what Sprint 75 actually achieved vs what it claimed.

---

## What Sprint 75 Got Right

- EV 93/93, ECC 46/46, tests 3041/3041 — all accurately reported
- PDF publication truth reconciliation — correctly superseded
- FormImporter BLOCKED_EXTERNAL — correctly tracked with retest trigger
- Words version drift — correctly classified, repair approval-blocked
- Email Converter post-merge validation — genuinely completed
- Slides Convert post-merge validation — genuinely completed (output_confirmed)
- Slides Merger post-merge validation — genuinely completed (output_confirmed)
- Sprint 27 governance exception — correctly applied

## What Sprint 75 Overclaimed

### Overclaim 1: Slides Compress "REPAIRED"

Sprint 75 Weekly Review Item 4 classification:
```
"NEEDS_REPAIR → REPAIRED"
```

Actual state:
- email-converter: RUNTIME_VALIDATED (repaired)
- slides-convert: RUNTIME_VALIDATED (repaired)
- slides-merger: RUNTIME_VALIDATED (repaired)
- slides-compress: RUNTIME_VALIDATED_NO_INPUT_FIXTURE (NOT repaired — partial only)

Correct Item 4 classification should have been:
```
PARTIALLY_REPAIRED — 3/4 examples fully validated, slides-compress deferred due to missing fixture
```

EV rule 90 (`email_slides_runtime_validated`) accepted the matrix without checking
that all examples with `post_merge_validated=true` also have `output_confirmed=true`.

### Overclaim 2: Dirty Tree Documentation

Sprint 75 `dirty-file-classification.md` states:
> "No Source or Test Files Are Dirty"

Sprint 75 `dirty-state-after.txt` shows:
> "modified: src/plugin_examples/evidence_validator.py"
> "modified: tests/unit/test_evidence_validator.py"

These two documents contradict each other. The actual truth (confirmed by git log):
- evidence_validator.py, test_evidence_validator.py, test_pipeline_evidence_gate.py
  were committed in b2a2748
- They were modified/unstaged when dirty-state-after.txt was captured
- dirty-file-classification.md incorrectly said they were not dirty at that point

The final-clean-proof.txt is accurate (lists all files committed), but the intermediate
evidence documents are inconsistent with each other.

---

## Sprint 75 True Status (Post-Audit)

| Dimension | Sprint 75 Claim | Corrected Status |
|-----------|----------------|------------------|
| Weekly Review Item 4 | REPAIRED | PARTIALLY_REPAIRED (slides-compress deferred) |
| Dirty tree | No source/test dirty | INTERNALLY_INCONSISTENT_DOCUMENTED (source/test were committed, but documents contradict) |
| EV rule coverage | 93/93 sufficient | GAPS_IN_RULES_90_91 (slides-compress partial, dirty-state internal inconsistency uncaught) |
| Overall closure | CLOSED | REOPENED — Sprint 76 repairs required |

---

## Sprint 76 Repair Plan

1. Phase 1: Capture truthful git state for sprint76 (no contradiction)
2. Phase 2: Run Slides Compress with real .pptx fixture, confirm output
3. Phase 3: Update weekly review matrix — separate 4 examples, correct Item 4
4. Phase 4: Add EV rules 94-101 to catch these failure modes
5. Phase 6: Run full test suite confirming new rules
6. Phase 7: Commit sprint76 bundle with honest final verdict
