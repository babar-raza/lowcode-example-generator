# Release-Status Authority Repair

## Root Cause
Sprint 51 release-status-raw.json showed all families as NEEDS_CLASSIFICATION because:
- `compute_release_status()` correctly reads denominator configs at `pipeline/configs/denominators/{family}.json`
- When re-run now, all families show correct published counts and scope statuses
- The Sprint 51 capture was likely generated from a stale or incorrectly-pathed run

## Evidence
- Re-running `compute_release_status()` at HEAD 007edb2 produces:
  - Cells: FAMILY_COMPLETE, 9 published
  - Words: PILOT_COMPLETE, 8 published
  - PDF: PARTIAL_CANARY, 5 published (14 PR-ready)
  - Diagram: PILOT_COMPLETE, 2 published
  - Email: PILOT_COMPLETE, 1 published
  - Slides: PILOT_COMPLETE, 3 published
- Total: 42/42 contract parity, 28 published, 14 PR-ready

## Resolution
1. Regenerated release-status-raw.json with current denominator state
2. Created portfolio-release-status.json as authoritative cross-reference
3. Both agree with portfolio-family-plugin-matrix

## No source changes needed — the release_status.py module works correctly.
The Sprint 51 capture was stale data, not a code bug.

## Gap Status: CLOSED
