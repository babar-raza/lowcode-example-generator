# Sprint 75 — Weekly Review Taskcard Updates

**Date:** 2026-05-23

All 6 weekly review items are now in durable tracking. No item remains only in chat or summary.

---

## TC-SPRINT75-ITEM1: PDF Publication Truth

| Field | Value |
|-------|-------|
| Taskcard ID | TC-SPRINT75-ITEM1 |
| Title | PDF 14-examples-blocked claim reconciliation |
| Status | CLOSED |
| Resolution | VERIFIED_HISTORICAL_BUT_SUPERSEDED |
| Evidence | reports/sprint75/pdf-publication/ (4 artifacts) |
| Created | Sprint 75 Phase 2 |
| Closed | Sprint 75 Phase 2 |
| Notes | All 19 PDF examples are remotely present. Old "14 blocked" claim from Sprint 21 is superseded by bulk publication (PRs #11, #17-#21, 2026-05-19). |

---

## TC-PDF-FORMIMPORTER-RETEST (updated)

| Field | Value |
|-------|-------|
| Taskcard ID | TC-PDF-FORMIMPORTER-RETEST |
| Title | FormImporter NullReferenceException retest |
| Status | OPEN_BLOCKED_EXTERNAL |
| Resolution | BLOCKED_EXTERNAL (Aspose.PDF 26.5.0 bug not fixed) |
| Evidence | reports/sprint75/formimporter/ (4 artifacts) |
| Updated | Sprint 75 Phase 3 |
| NuGet latest | 26.5.0 (same as defect version) |
| Repro | workspace/defect-repros/pdf-formimporter-nullref/ [CONFIRMED] |
| Watch | src/plugin_examples/package_watcher/formimporter_watch.py [ACTIVE] |
| Trigger | Aspose.PDF NuGet > 26.5.0 |

---

## TC-SPRINT75-ITEM3: Words Version Drift

| Field | Value |
|-------|-------|
| Taskcard ID | TC-SPRINT75-ITEM3 |
| Title | Words version drift 26.4.0 vs 26.5.0 |
| Status | OPEN_APPROVAL_BLOCKED |
| Resolution | NEEDS_REPAIR — repair ready, blocked by approval absent |
| Evidence | reports/sprint75/version-drift/ (4 artifacts) |
| Created | Sprint 75 Phase 4 |
| Remote version | 26.4.0 |
| Handoff version | 26.5.0 |
| Repair action | README I/O PR for Words will include version bump |
| Trigger | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR |

---

## TC-SPRINT75-ITEM4: Email/Slides Post-Merge Runtime Validation

| Field | Value |
|-------|-------|
| Taskcard ID | TC-SPRINT75-ITEM4 |
| Title | Email/Slides post-merge runtime validation (deferred since Sprint 21) |
| Status | CLOSED |
| Resolution | REPAIRED — all 4 examples runtime validated |
| Evidence | reports/sprint75/post-merge-runtime/ (4 artifacts) |
| Created | Sprint 75 Phase 5 |
| Closed | Sprint 75 Phase 5 |
| Results | email-converter: PASS; slides-compress: PASS (no fixture); slides-convert: PASS (64837 bytes); slides-merger: PASS (42020 bytes) |

---

## TC-SPRINT75-ITEM5: Dirty Tree State

| Field | Value |
|-------|-------|
| Taskcard ID | TC-SPRINT75-ITEM5 |
| Title | Working tree dirty state from weekly review |
| Status | CLOSED |
| Resolution | VERIFIED_HISTORICAL_BUT_SUPERSEDED |
| Evidence | reports/sprint75/git/dirty-file-classification.md |
| Created | Sprint 75 Phase 1 |
| Closed | Sprint 75 Phase 1 |
| Notes | Source/test dirty files were committed in sprint73/74. Only 7 workspace/verification/latest/ files remain modified (pre-existing runtime state, governance exception). |

---

## TC-SPRINT75-ITEM6: Sprint 27 Evidence Governance

| Field | Value |
|-------|-------|
| Taskcard ID | TC-SPRINT75-ITEM6 |
| Title | Sprint 27 bundle fails StrictEvidenceContract V1 |
| Status | CLOSED |
| Resolution | GOVERNANCE_EXCEPTION_REQUIRED — applied |
| Evidence | reports/sprint75/governance/ (4 artifacts) |
| Created | Sprint 75 Phase 6 |
| Closed | Sprint 75 Phase 6 |
| Policy applied | Historical Evidence Exception Policy v1.0 |
| Sprint 27 classified | HISTORICAL_NON_COMPLIANT — grandfathered |

---

## Summary

| Item | Taskcard | Status |
|------|----------|--------|
| 1 — PDF truth | TC-SPRINT75-ITEM1 | CLOSED |
| 2 — FormImporter | TC-PDF-FORMIMPORTER-RETEST | OPEN_BLOCKED_EXTERNAL |
| 3 — Words drift | TC-SPRINT75-ITEM3 | OPEN_APPROVAL_BLOCKED |
| 4 — Email/Slides runtime | TC-SPRINT75-ITEM4 | CLOSED |
| 5 — Dirty tree | TC-SPRINT75-ITEM5 | CLOSED |
| 6 — Sprint 27 governance | TC-SPRINT75-ITEM6 | CLOSED |

4 items closed this sprint. 2 items remain open with explicit blockers.
No item in an ambiguous or untracked state.
