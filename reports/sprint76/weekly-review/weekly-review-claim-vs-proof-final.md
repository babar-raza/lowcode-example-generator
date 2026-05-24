# Weekly Review — Claim vs Proof Final Matrix (Sprint 76)

**Date:** 2026-05-24
**Status:** All 6 items fully classified. Slides Compress corrected from Sprint 75.

---

## Item 1 — PDF Publication Truth Reconciliation

| Field | Value |
|-------|-------|
| Sprint 75 Claim | "14 PDF examples blocked" was accurate historically; all 19 now remotely present |
| Sprint 76 Verdict | VERIFIED_HISTORICAL_BUT_SUPERSEDED |
| Evidence | pdf-scenario-publication-map.json (19 records), pdf-pr-reconciliation.json |
| Change from Sprint 75 | None — VERIFIED, no correction needed |

---

## Item 2 — FormImporter Upstream Bug

| Field | Value |
|-------|-------|
| Sprint 75 Claim | Aspose.PDF 26.5.0 NullRef bug, BLOCKED_EXTERNAL |
| Sprint 76 Verdict | BLOCKED_EXTERNAL |
| Evidence | formimporter-repro-inventory.json, defect-repros/pdf-formimporter-nullref/ |
| Retest Trigger | TRG-01: NuGet > 26.5.0 |
| Change from Sprint 75 | None — VERIFIED |

---

## Item 3 — Words Version Drift

| Field | Value |
|-------|-------|
| Sprint 75 Claim | Remote=26.4.0, handoff=26.5.0, repair approval-blocked |
| Sprint 76 Verdict | NEEDS_REPAIR_APPROVAL_BLOCKED |
| Evidence | words-version-drift-current.json (drift + drift_type fields present) |
| Change from Sprint 75 | None — VERIFIED |

---

## Item 4 — Email/Slides Post-Merge Runtime Validation

**Corrected in Sprint 76.** Sprint 75 overclaimed full repair for Slides Compress.

| Example | Sprint 75 Status | Sprint 76 Status | Output Confirmed |
|---------|-----------------|------------------|------------------|
| email-converter | RUNTIME_VALIDATED | RUNTIME_VALIDATED ✓ | Yes (input.html) |
| slides-compress | RUNTIME_VALIDATED_NO_INPUT_FIXTURE (overclaim) | **RUNTIME_VALIDATED** ✓ | **Yes (19807 bytes)** |
| slides-convert | RUNTIME_VALIDATED | RUNTIME_VALIDATED ✓ | Yes (64837 bytes PDF) |
| slides-merger | RUNTIME_VALIDATED | RUNTIME_VALIDATED ✓ | Yes (42020 bytes PPTX) |

**Sprint 76 Item 4 Verdict:** REPAIRED — all 4 examples fully RUNTIME_VALIDATED

**Sprint 75 Error:** Slides Compress was classified `post_merge_validated=true` with
`output_confirmed=false`. This was an overclaim. Sprint 76 places real fixture and
confirms `output_confirmed=true`.

---

## Item 5 — Dirty Tree / Uncommitted Modifications

**Corrected documentation in Sprint 76.** Sprint 75 had internally inconsistent documents.

| Sprint 75 Document | Claim | Accuracy |
|-------------------|-------|----------|
| dirty-state-after.txt | evidence_validator.py, test files = modified | TRUE at time of capture (pre-commit) |
| dirty-file-classification.md | "No Source or Test Files Are Dirty" | CONTRADICTS dirty-state-after.txt |
| final-clean-proof.txt | All source/test files committed in b2a2748 | TRUE |

**Root cause:** dirty-state-after.txt captured pre-commit state; classification document
was written independently and did not match the captured snapshot.

**Current state (after b2a2748+278c528):**
- Source/test files: CLEAN (all committed in b2a2748)
- workspace/verification/latest/: 7 files dirty (governance exception, ongoing)

**Sprint 76 Item 5 Verdict:** WORKSPACE_LATEST_DIRTY_GOVERNANCE_EXCEPTION

The source/test contradiction from sprint75 is acknowledged and documented.
Sprint76 git documents are internally consistent.

---

## Item 6 — Sprint 27 Historical Governance Exception

| Field | Value |
|-------|-------|
| Sprint 75 Claim | GOVERNANCE_EXCEPTION_REQUIRED |
| Sprint 76 Verdict | GOVERNANCE_EXCEPTION_APPLIED |
| Evidence | governance/historical-evidence-exception-policy.md, sprint27-strict-contract-revalidation.md |
| Change from Sprint 75 | Label upgraded: REQUIRED → APPLIED (policy was applied, not just required) |

---

## Summary

| Item | Sprint 75 Classification | Sprint 76 Classification | Changed |
|------|------------------------|------------------------|---------|
| 1. PDF publication | VERIFIED_HISTORICAL_BUT_SUPERSEDED | VERIFIED_HISTORICAL_BUT_SUPERSEDED | No |
| 2. FormImporter | BLOCKED_EXTERNAL | BLOCKED_EXTERNAL | No |
| 3. Words drift | NEEDS_REPAIR_APPROVAL_BLOCKED | NEEDS_REPAIR_APPROVAL_BLOCKED | No |
| 4a. email-converter | RUNTIME_VALIDATED | RUNTIME_VALIDATED | No |
| 4b. slides-compress | RUNTIME_VALIDATED_NO_INPUT_FIXTURE | **RUNTIME_VALIDATED** | YES — repaired |
| 4c. slides-convert | RUNTIME_VALIDATED | RUNTIME_VALIDATED | No |
| 4d. slides-merger | RUNTIME_VALIDATED | RUNTIME_VALIDATED | No |
| 5. Dirty tree | VERIFIED_HISTORICAL_BUT_SUPERSEDED | WORKSPACE_LATEST_DIRTY_GOVERNANCE_EXCEPTION | YES — clarified |
| 6. Sprint 27 | GOVERNANCE_EXCEPTION_REQUIRED | GOVERNANCE_EXCEPTION_APPLIED | Minor label |
