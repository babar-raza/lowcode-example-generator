# Weekly Review Claim vs Proof — Final — Sprint 77

**Date:** 2026-05-24
**Sprint:** 77 (evidence repair)

## Final Classification of All Weekly Review Items

| Item | Description | Classification | Sprint | Notes |
|------|-------------|----------------|--------|-------|
| 1 | PDF publication blocked claim | VERIFIED_HISTORICAL_BUT_SUPERSEDED | S75 | PDF PRs are historical; no overclaim |
| 2 | FormImporter blocked by Aspose.PDF bug | BLOCKED_EXTERNAL | S75 | TRG-01 fires at NuGet > 26.5.0; task card durable |
| 3 | Words version drift (Remote=26.4.0, Handoff=26.5.0) | NEEDS_REPAIR_APPROVAL_BLOCKED | S75 | Approval token not present; version bump deferred |
| 4a | email-converter runtime validation | RUNTIME_VALIDATED | S75 | Real input/output confirmed; output_confirmed=true |
| 4b | slides-compress runtime validation | RUNTIME_VALIDATED | S76→S77 | S75 overclaim repaired in S76; output.pptx committed in S77 |
| 4c | slides-convert runtime validation | RUNTIME_VALIDATED | S75 | PPTX→PDF confirmed |
| 4d | slides-merger runtime validation | RUNTIME_VALIDATED | S75 | Merged PPTX confirmed |
| 5 | Dirty workspace state | WORKSPACE_LATEST_DIRTY_GOVERNANCE_EXCEPTION | S76→S77 | S75 contradiction resolved; only workspace/latest remains |
| 6 | Sprint 27 historical non-compliance | GOVERNANCE_EXCEPTION_REQUIRED | S75 | PRE_CONTRACT_ERA_BUNDLE; 17 categories grandfathered |

## Sprint 77 Changes from Sprint 76

- Item 4b: `output.pptx` now committed in sprint77 artifacts (previously untracked) — NO classification change, but evidence is now complete
- Item 5: Dirty workspace is confirmed clean of untracked files after Sprint 77 handles `output.pptx`

## Current Publication State

- **42/42 remote examples:** PRESENT (all families published)
- **README I/O:** 0/42 (approval blocked)
- **PRs created:** 0 (approval token not present)
- **Approval token:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` = NOT_SET
