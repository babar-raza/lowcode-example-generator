# Sprint A2 — Preflight Review

**Date:** 2026-05-04
**Sprint:** Sprint A2 — Consistency Hardening and Readiness Rank Repair
**Verdict:** `PROCEED_SPRINT_A2_NO_BLOCKING_CONCURRENT_WORK`

---

## A1 State Confirmed

| Check | Result |
|-------|--------|
| GAP-001 resolved | YES — both remote repos have pipeline-generated README on main |
| Cells README on main | 5346 bytes |
| Words README on main | 4555 bytes |
| Tests passing | 675 |
| All tests passing | YES |

---

## Concurrent Work

No active concurrent work detected. Git status shows modifications from the PDF Assembly Deduplication Sprint (already completed by another window). Safe to proceed.

---

## Target Files Assessment

| File | Issue | Status |
|------|-------|--------|
| `repo_access_resolver.py:42` | Uses `"token {token}"` not `"Bearer {token}"` | Clean to edit |
| `release_status.py:11-21` | Hardcoded dict has stale PDF entry (`followup-pdf-reflection-dedup` = CLOSED) | Clean to edit |
| `__main__.py` | discover-lowcode handler overwrites readiness rank; no sync-taskcard-docs command | Clean to edit |
| `discovery_sweep.py` | No single-family preserve logic; generation_ready already fixed | Clean to edit |
| `open-taskcard-closure-matrix.md` | Very stale (sprint header, wrong open/closed states, missing 8 taskcards) | Clean to edit |
| `docs/ci/` | Directory does not exist | Create |
| `monthly-maintenance-runbook.json` | References `followup-pdf-reflection-dedup` as unresolved (now CLOSED) | Clean to edit |

---

## GAP-NEW-01 Evidence

- `compute_generation_readiness()` already writes `generation_ready` (fixed in PDF Assembly Deduplication Sprint) ✓
- Single-family `discover-lowcode --families words` still overwrites the shared file with only the words entry
- Fix needed: merge/preserve existing entries when running single-family discovery

---

## Markdown Stale Details

**Wrong open (should be closed):**
- `followup-pdf-reflection-dedup` (closed in PDF Assembly Deduplication Sprint)
- `followup-words-options-aware-review` (closed in Words Readiness Review Sprint)
- `followup-words-role-classification-review` (closed in Words Readiness Review Sprint)

**Missing open:**
- `followup-words-split-criteria-enumeration`, `followup-words-pair-fixture-strategy`
- `followup-words-mail-merger-fixture-documentation`, `followup-words-docx-semantic-validation`
- `followup-pdf-role-classification-review`, `followup-pdf-options-aware-review`
- `followup-pdf-fixture-strategy-review`, `followup-pdf-family-repo-target-mapping`

---

## Stop Gates

- GATE-3: Any test regression → stop, revert
- GATE-6: No PDF generation (pdf.yml status=discovery_only)
- GATE-7: No examples generated
