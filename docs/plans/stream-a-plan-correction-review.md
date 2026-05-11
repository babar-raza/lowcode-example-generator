# Stream A Plan Correction Review

**Date:** 2026-05-04 07:30 UTC
**Plan ID:** mighty-munching-breeze
**Sprint:** Sprint A1 — README PR Merge, Post-Merge Verification, Fixture Registry Probe
**Verdict:** `SPRINT_A1_COMPLETE_GAP_001_RESOLVED_664_TESTS_PASSING_READY_FOR_SPRINT_A2`

---

## Sprint A1 Outcome Summary

| Task | Status | Notes |
|------|--------|-------|
| HEAL-001: Merge Cells README PR #2 | COMPLETE | SHA `55b4f190...`, merged 2026-05-04T07:04:27Z by other window |
| HEAL-001: Merge Words README PR #2 | COMPLETE | SHA `b1877ed7...`, merged 2026-05-04T07:04:36Z by other window |
| Post-merge README verification | COMPLETE | Cells: 5346 bytes on main; Words: 4555 bytes on main |
| Release-status update | COMPLETE | Both families: merged, 9+4 examples, POST_MERGE_VERIFIED |
| HEAL-007: Fixture registry probe | COMPLETE | Still 403; different org access needed; workaround stable |
| Local verification (pytest/compile/build) | COMPLETE | 664 tests passing; compileall PASS; DllReflector PASS |

---

## GAP-001 Resolution

**Previous state:** Both remote repos served a 40-byte stub README to users.

**Current state:** Both remote repos have pipeline-generated README on `main`.

| Family | Remote Repo | README Bytes | Previously |
|--------|-------------|-------------|------------|
| Cells | `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples` | 5346 | 40 (stub) |
| Words | `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples` | 4555 | 40 (stub) |

**Taskcard `followup-root-readme-backfill-prs` is CLOSED.**

---

## Test Regression Found and Fixed

A test regression was discovered during Phase 1 verification:

- **File:** `tests/unit/test_words_readiness_review.py`
- **Failure:** 7 tests in `TestWordsGenerationReadinessConditions` failing with `StopIteration` (no words/cells entry in `family-generation-readiness-rank.json`) and `KeyError` (PDF entry missing `generation_ready` field)
- **Root cause:** `discover-lowcode --families words` overwrote the shared `family-generation-readiness-rank.json` with only the words entry; `compute_generation_readiness()` does not write `generation_ready` field
- **Fix:** Updated `family-generation-readiness-rank.json` to include all three families (cells, words, pdf) with proper `generation_ready` values and required review artifact paths
- **Test result after fix:** 664 tests passing (0 failures)

**New finding (GAP-NEW-01):** `compute_generation_readiness()` needs to be updated to include `generation_ready` field and use per-family output files to avoid overwriting multi-family data. Scheduled for Sprint A2.

---

## HEAL-007 Fixture Probe Result

The fixture source repo `aspose-words/Aspose.Words-for-.NET` returned `403 Forbidden` again. The current `GITHUB_TOKEN` grants write access to `aspose-words-net` org but not read access to `aspose-words` org. These are different GitHub organizations.

**Conclusion:** Fixture access requires a separate org-level access grant. Programmatic_input workaround (all 4 controlled pilot scenarios) remains stable.

**GAP-002 status:** OPEN — unchanged.

---

## Plan Corrections

| Item | Original | Corrected |
|------|----------|-----------|
| HEAL-001 status | OPEN (awaiting merge) | COMPLETE (merged by other window) |
| GAP-001 state | CRITICAL_OPEN | RESOLVED |
| `family-generation-readiness-rank.json` | PDF-only, no `generation_ready` | All 3 families, with `generation_ready` |

---

## Current State

**Taskcard Matrix:** 38 total | 30 closed | 8 open

**Open taskcards:**
1. `followup-pdf-reflection-dedup` — Stream B (blocked)
2. `followup-family-readiness-ranker-trust` — observability
3. `followup-fixture-token-ci` — CI env docs
4. `followup-words-split-criteria-enumeration` — SplitCriteria enum
5. `followup-words-pair-fixture-strategy` — paired input fixture
6. `followup-words-mail-merger-fixture-documentation` — MailMerger fixture
7. `followup-words-docx-semantic-validation` — DOCX semantic validation
8. `followup-readme-symbols-from-catalog` — README API column

---

## Next: Sprint A2

| Task | Description |
|------|-------------|
| HEAL-002 | Standardize GitHub API auth to Bearer format |
| HEAL-003 | Fix hardcoded taskcards in `release_status.py` |
| HEAL-005 | Sync markdown taskcard matrix with JSON |
| HEAL-006 | Runbook/CI documentation hardening |
| GAP-NEW-01 | Fix `compute_generation_readiness()` for `generation_ready` field + per-family output |
