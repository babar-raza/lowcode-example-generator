# Sprint 75 — Weekly Review Intake

**Date:** 2026-05-23
**Reviewer:** Babar Raza (independent)
**Intake Sprint:** sprint75

## Purpose

This document records Babar's six independent weekly review findings as formal sprint inputs.
Each item is treated as a high-priority claim requiring reconciliation — not automatic acceptance,
not dismissal. Authority comes from current repo state, remote GitHub state, runtime logs,
and deterministic validators.

## Review Items

### Item 1 — 14 PDF Examples Blocked by Approval Gate

**Claim:** 14 PDF examples were technically ready (via PR#3/PR#5/PR#6/PR#7/PR#8/PR#9) but not
published because the live-publish approval gate was absent.

**Source:** Commit `a0319bb` (Sprint 21), mega-train-005 PDF retest report, prior sprint notes.

**Initial classification:** NEEDS_FRESH_REMOTE_CHECK

**Assigned to Phase:** 2 (PDF Publication Truth Reconciliation)

---

### Item 2 — FormImporter Upstream Aspose.PDF 26.5.0 Bug

**Claim:** FormImporter is permanently blocked by NullReferenceException in
`Forms.Form.#=zZQILclhNTKUB` (Aspose.PDF 26.5.0). Three test cases confirm it.
Minimal repro at `workspace/defect-repros/pdf-formimporter-nullref/`.
Taskcard: TC-PDF-FORMIMPORTER-RETEST.

**Source:** mega-train-005 pdf-formimporter-retest-report.md, package_watcher/formimporter_watch.py.

**Initial classification:** NEEDS_FRESH_REMOTE_CHECK (check if 26.6.0+ NuGet available)

**Assigned to Phase:** 3 (FormImporter Bug Tracking)

---

### Item 3 — Words Version Drift 26.4.0 vs 26.5.0

**Claim:** Words examples were published at 26.4.0. NuGet/current target is 26.5.0.
No regeneration was performed. Words is marked PUBLISHED_VERSION_DRIFT.

**Source:** Sprint 75 version-truth-matrix.json, MEMORY.md portfolio table.

**Initial classification:** PARTIALLY_VERIFIED (drift confirmed in sprint75 artifacts)

**Assigned to Phase:** 4 (Words Version Drift Repair Plan)

---

### Item 4 — Email and Slides Post-Merge Runtime Validation Deferred

**Claim:** Commit `afca831` says all_post_merge_validated=false. Commit `a0319bb` deferred
runtime validation for Email PR#1 and Slides PR#1. These examples were merged but never
end-to-end runtime verified.

**Source:** Commit messages `afca831` and `a0319bb` (confirmed to exist in git log).

**Initial classification:** PARTIALLY_VERIFIED (commits confirmed, runtime status unknown)

**Assigned to Phase:** 5 (Email/Slides Post-Merge Runtime Validation)

---

### Item 5 — Working Tree Has Uncommitted Modifications

**Claim:** Working tree has uncommitted modifications to `evidence_validator.py`,
two test files, and seven `workspace/verification/latest/**` JSON files, plus
untracked `reports/sprint72/`.

**Source:** Weekly review snapshot (prior to sprint75 start).

**Initial classification:** NEEDS_FRESH_REMOTE_CHECK (current git status must be captured)

**Assigned to Phase:** 1 (Dirty Tree Reconciliation)

---

### Item 6 — Sprint 27 Bundle Fails StrictEvidenceContract V1

**Claim:** Commit `20686d3` documents Sprint 27 bundle retroactively failing
StrictEvidenceContract V1 with at least 10 missing categories. Downstream Sprints 28-30
are compliant.

**Source:** Commit `20686d3` message (confirmed in git log): "Sprint 27 thin bundle
retroactively FAILS contract (≥10 missing categories)."

**Initial classification:** PARTIALLY_VERIFIED (commit confirmed; sprint27 bundle
existence in local reports/ TBD)

**Assigned to Phase:** 6 (Sprint 27 Strict Evidence Contract Revalidation)

---

## Acceptance Criteria for This Document

- [x] All 6 items recorded.
- [x] No item is dropped as "informational."
- [x] No item is blindly accepted without current evidence — each assigned to a reconciliation phase.
- [x] Initial classifications noted with basis.
- [x] Final classifications will be determined in respective phases.
