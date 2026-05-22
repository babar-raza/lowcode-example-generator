# Release-Status Top-Level Field Repair

## Problem
`all_merged=true` was misleading when PDF had 14 PR-ready examples.

## Discovery
PDF denominator was already updated on disk to `published_count=19, pr_dry_run_ready_count=0` by a prior pipeline run (MT007 Sprint, 2026-05-20), reflecting that PRs #11, #17-#21 merged all 14 remaining PDF examples. This change was uncommitted.

## Solution
- Added explicit top-level fields: all_published, all_contracts_accounted_for, published_count, pr_ready_count, total_contracts, approval_blocked_count, families_complete_count, families_partial_count
- Committed the PDF denominator update (published_count 5→19)
- Portfolio is now: **42/42 parity, 42 published, 0 PR-ready**

## Tests
5 new tests added. 33 total tests pass.

## Commit: f216bd7
