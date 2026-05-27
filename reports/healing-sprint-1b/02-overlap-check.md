# Healing Sprint 1B — Overlap Check

**Author:** Coordinator Agent (Lane 0)
**Date:** 2026-05-27

## File Ownership Matrix

| Path Prefix | Owner Lane | Conflict Risk |
|---|---|---|
| `reports/healing-sprint-1b/00-*.md` | Lane 0 | NONE |
| `reports/healing-sprint-1b/01-*.md` | Lane 0 | NONE |
| `reports/healing-sprint-1b/02-*.md` | Lane 0 | NONE |
| `reports/healing-sprint-1b/final-verdict.md` | Lane 0 | NONE |
| `reports/healing-sprint-1b/sprint-state.json` | Lane 0 | NONE |
| `reports/healing-sprint-1b/bundle-manifest.json` | Lane 0 | NONE |
| `reports/healing-sprint-1b/evidence/healing-validation-result.json` | Lane 0 | NONE |
| `reports/healing-sprint-1b/evidence/evidence-contract-computed.json` | Lane 0/5 | LOW (Lane 5 generates, Lane 0 uses) |
| `reports/healing-sprint-1b/review/` | Lane 0 | NONE |
| `reports/healing-sprint-1b/git/` | Lane 1 | NONE |
| `reports/healing-sprint-1b/final-proof/` | Lane 1 | NONE |
| `reports/healing-sprint-1b/evidence-consistency/` | Lane 1 | NONE |
| `reports/healing-sprint-1b/tracking/` | Lane 2 | NONE |
| `reports/healing-sprint-1b/state-sync/` | Lane 2 | NONE |
| `reports/healing-sprint-1b/replay/` | Lane 3 | NONE |
| `reports/healing-sprint-1b/gates/` | Lane 4 | NONE |
| `reports/healing-sprint-1b/dry-run/` | Lane 4 | NONE |
| `reports/healing-sprint-1b/evidence/validator-*.* ` | Lane 5 | NONE |
| `reports/healing-sprint-1b/evidence-contract/` | Lane 5 | NONE |
| `reports/healing-sprint-1b/bundle-audit/` | Lane 5 | NONE |
| `reports/healing-sprint-1b/iv/` | Lane 6 | NONE |

## Shared File Coordination

`evidence/evidence-contract-computed.json`:
- Lane 5 generates the raw ECC output
- Lane 0 treats it as authoritative input for final-verdict

## External File Modified by Lane 1 Only

- `README.md` — Lane 1 stages and commits this file. No other lane touches it.

## No Conflicts Detected

All lanes have non-overlapping write paths.
