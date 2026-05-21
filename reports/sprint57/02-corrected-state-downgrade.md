# Sprint 56 Corrected State Downgrade

**Sprint 57 Phase 0 — State Correction**
**Generated:** 2026-05-21

---

## State Transition Applied

### 14 PDF entries: POST_MERGE_VERIFIED (CONTRACT_AUTHORITY) → MERGED

All 14 entries have GitHub API-confirmed merge with real merge commit SHAs.
They do NOT yet have destination repo content verification (Phase 7 will provide that).
Correct state is MERGED until Phase 7 content verification completes.

| Entry | PR# | Old State | Old post_merge_validation | GitHub Merge SHA | New State |
|-------|-----|-----------|--------------------------|-----------------|-----------|
| pdf-doc-converter | #11 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 20b858958d1df2965893eb305cb9ac418c3ea285 | MERGED |
| pdf-html | #11 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 20b858958d1df2965893eb305cb9ac418c3ea285 | MERGED |
| pdf-xls-converter | #11 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 20b858958d1df2965893eb305cb9ac418c3ea285 | MERGED |
| pdf-jpeg | #17 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | d793cbec89e2ed7d0a7a868551f9e5824dd332d7 | MERGED |
| pdf-png | #17 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | d793cbec89e2ed7d0a7a868551f9e5824dd332d7 | MERGED |
| pdf-tiff | #17 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | d793cbec89e2ed7d0a7a868551f9e5824dd332d7 | MERGED |
| pdf-image-extractor | #18 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | a26a302ba43204309de52def7b4229bf932bd2c3 | MERGED |
| pdf-table-generator | #18 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | a26a302ba43204309de52def7b4229bf932bd2c3 | MERGED |
| pdf-toc-generator | #18 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | a26a302ba43204309de52def7b4229bf932bd2c3 | MERGED |
| pdf-form-flattener | #19 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | c354f633dec3b39133f813f150956bbbb0304b8c | MERGED |
| pdf-security | #19 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | c354f633dec3b39133f813f150956bbbb0304b8c | MERGED |
| pdf-form-editor | #20 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 3e6cf39a74345e200904cc56681ede1cf8d3631a | MERGED |
| pdf-form-exporter | #20 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 3e6cf39a74345e200904cc56681ede1cf8d3631a | MERGED |
| pdf-signature | #21 | POST_MERGE_VERIFIED | CONTRACT_AUTHORITY | 5aa0fa6f485be405f4c23e85162b68f31ec2a9cb | MERGED |

**GitHub API evidence source:** `gh api repos/aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples/pulls/{pr}`
**Query executed:** 2026-05-21 (Sprint 57 Phase 0)
**Fields checked:** `.state` (closed), `.merged_at` (non-null), `.merge_commit_sha`

---

## Queue State Summary (Corrected)

| State | Before Sprint 57 | After Correction | Change |
|-------|-----------------|-----------------|--------|
| POST_MERGE_VERIFIED | 42 | 28 | -14 |
| MERGED | 0 | 14 | +14 |
| PR_READY | 0 | 0 | 0 |
| BACKLOGGED | 5 | 5 | 0 |
| PERMANENTLY_BLOCKED | 7 | 7 | 0 |
| **Total Active** | **42** | **42** | 0 |

**Path to POST_MERGE_VERIFIED for the 14 MERGED entries:**
Phase 7 (Lane G) will audit the destination repo contents for each entry.
If destination repo contains correct examples with correct I/O formats after merge → upgrade to POST_MERGE_VERIFIED with evidence.

---

## CONTRACT_AUTHORITY Token Retirement

The `CONTRACT_AUTHORITY` value for `post_merge_validation` is being retired:
- It was introduced in Sprint 56 LaneA as a workaround to upgrade 14 PR_READY entries
- The mechanism is invalid per sprint 57 rules
- All 14 entries now have real GitHub API merge SHAs
- `post_merge_validation` is set to null for MERGED state entries
- When content verification is done (Phase 7), post_merge_validation will be set to "ALL_PASS" or "CONTENT_VERIFIED"

The `CONTRACT_AUTHORITY` value is removed from the completion queue and tests must be updated.

---

## Test Updates Required

**test_completion_queue.py:**
1. `test_merged_entries_have_merge_sha` — Remove CONTRACT_AUTHORITY exception; all MERGED/POST_MERGE_VERIFIED entries now have merge_sha
2. `test_post_merge_verified_entries_have_post_merge_validation` — Remove CONTRACT_AUTHORITY from valid set; only ALL_PASS is valid
3. `test_pdf_all_merge_verified_or_better` — New test: all 42 PDF active entries should be MERGED or POST_MERGE_VERIFIED
4. `test_state_summary_counts_match_entries` — Update to expect POST_MERGE_VERIFIED: 28, MERGED: 14

---

## Completion Queue File Changes

The completion queue `workspace/queues/example-completion-queue.json` must be updated:
1. Change `state_summary.POST_MERGE_VERIFIED` from 42 to 28
2. Add `state_summary.MERGED: 14`
3. For each of the 14 entries: change `state` → "MERGED", `post_merge_validation` → null, `merge_sha` → actual GitHub merge SHA
4. Update header description to remove CONTRACT_AUTHORITY reference
