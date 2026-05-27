# Healing Sprint 1 — Overlap Check

**Author:** Coordinator Agent (Lane 0)
**Date:** 2026-05-27

## File Ownership Matrix

| Path Prefix | Owner Lane | Shared Read | Conflict Risk |
|---|---|---|---|
| `reports/healing-sprint-1/final-verdict.md` | Lane 0 | Lane 8 (verify) | LOW |
| `reports/healing-sprint-1/sprint-state.json` | Lane 0 | Lane 8 (verify) | LOW |
| `reports/healing-sprint-1/bundle-manifest.json` | Lane 0 | Lane 8 (verify) | LOW |
| `reports/healing-sprint-1/review/adversarial-review.md` | Lane 0 | Lane 8 | LOW |
| `reports/healing-sprint-1/review/self-repair-actions.json` | Lane 0 | Lane 8 | LOW |
| `reports/healing-sprint-1/review/final-consistency-check.json` | Lane 0 | Lane 8 | LOW |
| `reports/healing-sprint-1/evidence/healing-validation-result.json` | Lane 0 | Lane 8 | LOW |
| `reports/healing-sprint-1/evidence/evidence-contract-computed.json` | Lane 0 (generates) | Lane 8 | LOW |
| `reports/healing-sprint-1/final-proof/` | Lane 1 | Lane 0, Lane 8 | LOW |
| `reports/healing-sprint-1/git/` | Lane 1 | Lane 0, Lane 8 | LOW |
| `reports/healing-sprint-1/evidence-consistency/` | Lane 1 | — | LOW |
| `reports/healing-sprint-1/replay/` | Lane 2 | Lane 8 | LOW |
| `reports/healing-sprint-1/gates/` | Lane 3 | Lane 8 | LOW |
| `reports/healing-sprint-1/evidence/validator-*` | Lane 4 | Lane 0, Lane 8 | LOW |
| `reports/healing-sprint-1/evidence-contract/` | Lane 5 | Lane 0, Lane 8 | LOW |
| `reports/healing-sprint-1/bundle-audit/` | Lane 5 | Lane 0, Lane 8 | LOW |
| `reports/healing-sprint-1/dry-run/` | Lane 6 | Lane 8 | LOW |
| `reports/healing-sprint-1/state-sync/` | Lane 7 | Lane 8 | LOW |
| `reports/healing-sprint-1/tracking/` | Lane 7 | Lane 8 | LOW |
| `reports/healing-sprint-1/iv/` | Lane 8 | Lane 0 | LOW |
| `reports/healing-sprint-1/review/iv-findings.md` | Lane 8 | Lane 0 | LOW |

## No Conflicts Detected

All lanes have non-overlapping write paths.
No circular dependencies.
