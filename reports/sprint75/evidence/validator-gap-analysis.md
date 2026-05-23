# Sprint 75 — Validator Gap Analysis

**Date:** 2026-05-23

## Gaps Addressed (Sprint 75 New Rules)

The following gaps were identified against the weekly review specification. Each gap
is now closed by a new EV rule (rules 86-93).

| Rule ID | Gap | New Rule |
|---------|-----|----------|
| 86 | Weekly review items not classified — no artifact requirement | `weekly_review_claim_matrix_present` |
| 87 | PDF publication truth inferred from old PR numbers | `pdf_publication_truth_reconciled` |
| 88 | FormImporter bug lacks durable taskcard/retest trigger | `formimporter_taskcard_durable` |
| 89 | Words version drift ignored or undocumented | `words_version_drift_documented` |
| 90 | Email/Slides merged but runtime validation deferred silently | `email_slides_runtime_validated` |
| 91 | Dirty source/test/workspace files not explicitly classified | `dirty_tree_classified` |
| 92 | Sprint 27 evidence gap not formally classified | `sprint27_governance_classified` |
| 93 | Final verdict claims closure while weekly review items unclassified | `weekly_review_verdict_not_complete_while_unclassified` |

## Why Sprint 74 Fails Under Sprint 75 Rules

Sprint 74 predates these rules and lacks:
- `02-weekly-review-claim-vs-proof-matrix.md` (rules 86, 93)
- `pdf-publication/pdf-pr-reconciliation.json` (rule 87)
- `formimporter/formimporter-repro-inventory.json` (rule 88)
- `version-drift/words-version-drift-current.json` (rule 89)
- `post-merge-runtime/post-merge-validation-matrix.json` (rule 90)
- `git/dirty-file-classification.md` (rule 91)
- `governance/sprint27-strict-contract-revalidation.md` (rule 92)

Sprint 74 revalidation result is documented in `evidence/sprint74-revalidation-result.json`.

## Rule Count Evolution

| Sprint | Rules |
|--------|-------|
| Sprint 60 | 12 |
| Sprint 61 | 20 |
| Sprint 62 | 21 |
| Sprint 64 | 22 |
| Sprint 65 | 32 |
| Sprint 66 | 42 |
| Sprint 67 | 52 |
| Sprint 68 | 57 |
| Sprint 69 | 67 |
| Sprint 70 | 72 |
| Sprint 71 | 78 |
| Sprint 72 | 85 |
| **Sprint 75** | **93** |

## New Allowed Verdicts

Sprint 75 adds 3 new allowed verdicts to `_rule_final_verdict_is_precise`:
- `LOWCODE_WEEKLY_REVIEW_ITEMS_CLASSIFIED_PUBLICATION_APPROVAL_BLOCKED`
- `LOWCODE_WEEKLY_REVIEW_REPAIRED_AND_README_IO_PRS_CREATED`
- `LOWCODE_PUBLICATION_AND_REVIEW_ITEMS_PARTIAL_WITH_EXPLICIT_BLOCKERS`
