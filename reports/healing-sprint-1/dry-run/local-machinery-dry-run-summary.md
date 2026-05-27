# Healing Sprint 1 — Lane 6: Local Dry-Run Machinery Test

**Lane:** 6 — Local Dry-Run Machinery Test
**Date:** 2026-05-27

## Handoff Source

`workspace/verification/latest/families/`

## Family Results

| Family | PR Candidates | Build | Run | Reviewer | Status |
|---|---|---|---|---|---|
| cells | 9 | passed_all | passed_all | passed_all | PASS |
| words | 7 (1 excluded) | passed_all | passed_all | passed_all | PASS |
| pdf | 19 | passed_all | passed_all | passed_all | PASS |
| diagram | 2 | passed_all | passed_all | passed_all | PASS |
| email | 1 | passed_all | passed_all | passed_all | PASS |
| slides | 3 | passed_all | passed_all | passed_all | PASS |

**Total PR candidates: 41** (cells:9, words:7, pdf:19, diagram:2, email:1, slides:3)

## Note on Cross-Family pr-candidate-manifest.json

The `pr-candidate-manifest.json` stored in each family directory is a cross-family
manifest containing all 41 candidates across all families. Per-family counts come
from `aggregate-gate-results.json`, not from the manifest directly.

## Machinery Health Check

| Check | Result |
|---|---|
| All 6 family directories exist | YES |
| All aggregate-gate-results.json present | YES |
| All families: build passed_all | YES |
| All families: run passed_all | YES |
| All families: reviewer passed_all | YES |
| Total candidates match publication truth matrix | YES (41 == 41 PR candidates) |

## Publication Gate

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`: NOT SET
→ Publication remains APPROVAL_BLOCKED
→ Dry-run only: no PRs executed

## Notes

- Words family: 8 examples generated, 7 PR candidates (1 excluded). This is expected
  and matches the publication truth matrix.
- Cross-family manifest shows 41 included, 0 excluded at the cross-family level.
  Words exclusion is at the family-local level.

## Lane 6 Verdict

**LANE_6_PASS** — All 6 families validated. Local machinery is healthy. 41 examples
ready for publication when approval gate is set.
