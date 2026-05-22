# Publication State Model — Sprint 69

Date: 2026-05-22
Sprint: sprint69
Defects closed: S68-D2, S68-D3

## Two Distinct Publication Events

Sprint 69 separates two publication events that were conflated in Sprint 68:

### Event 1: Original Example Publication (COMPLETED)

All 42 LowCode examples (Program.cs + csproj) have been published to the 6
destination repositories. This happened across Sprints 54-62.

Fields in publication-truth-matrix-final.json:
- `remote_example_present=true` — example is published in destination repo
- `remote_programcs_matches_handoff=true` — content verified
- These fields reflect a COMPLETED event. They do NOT reference any pending PR.

### Event 2: README I/O Update Publication (PENDING — APPROVAL_BLOCKED)

A second publication event is needed to add `## Input and Output` sections to all
42 example READMEs and update the 6 family root READMEs. This has NOT been done.

Fields tracking this PENDING event:
- `remote_example_readme_has_io_docs=false` — no I/O section in any remote README
- `readme_io_update_needed=true` — update required for all 42
- `live_pr_needed=true` — PR must be created
- `live_pr_open=false` — no PR created yet
- `readme_io_pr_merged=false` — not merged
- `readme_io_post_merge_verified=false` — NOT verified because not merged
- `approval_blocked=true` — requires APPROVE_LIVE_PR token

## Rule: No Mixed State

The following combinations are INVALID and will fail EV rule 64:

- `remote_example_readme_has_io_docs=false` AND `readme_io_post_merge_verified=true`
  → Contradicts: cannot be post-merge-verified if remote README lacks I/O docs

- `approval_blocked=true` AND `readme_io_pr_merged=true`
  → Contradicts: PR cannot be merged if approval was blocked

## Current Sprint 69 State

All 42 examples:
```
publication_status = REMOTE_EXAMPLE_PRESENT_README_IO_STALE_LOCAL_HANDOFF_READY_APPROVAL_BLOCKED
```

Meaning:
- Remote example is present (Event 1 complete)
- Remote README lacks I/O docs (Event 2 not done)
- Local handoff is ready (sprint69 package prepared)
- Publication of README I/O update is blocked by APPROVE_LIVE_PR

## Allowed Publication Statuses

| Status | Meaning |
|--------|---------|
| `REMOTE_EXAMPLE_PRESENT_README_IO_STALE_LOCAL_HANDOFF_READY_APPROVAL_BLOCKED` | Current sprint69 state |
| `README_IO_PR_CREATED_MERGE_APPROVAL_BLOCKED` | After PR creation, before merge approval |
| `README_IO_PR_MERGED_POST_MERGE_VERIFIED` | After merge and verification |
| `REMOTE_EXAMPLE_PRESENT_README_IO_CURRENT` | Full completion state |
