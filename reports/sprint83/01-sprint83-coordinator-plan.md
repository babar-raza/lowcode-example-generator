# Sprint 83 -- Coordinator Plan

## Sprint Type: PUBLICATION_MEGA_SPRINT (Multi-Lane)

## Approval Status

| Gate | Env Var | Status |
|------|---------|--------|
| PR creation | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL | NOT_SET |
| PR merge | PLUGIN_EXAMPLES_MERGE_PR_APPROVAL | NOT_SET |

**Decision: LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL**

## Lane Assignments

| Lane | Owner | Purpose | Approval Required? |
|------|-------|---------|------------------|
| A | Publication Agent | Live README I/O PR creation | YES (SKIP if NOT_SET) |
| B | Conflict Strategy Agent | Root README PR conflict analysis | NO |
| C | Handoff/Remote Agent | Revalidate handoff + remote truth | NO |
| D | Product Advancement Agent | Version drift, FormImporter, readiness | NO |
| E | Validator Agent | Add EV rules 112-115 | NO |
| F | Evidence Consistency Agent | Clean Sprint 82 stale labels | NO |
| G | State Sync Agent | Taskcard/docs synchronization | NO |
| H | IV Agent | Independent verification | NO |
| Coord | Coordinator | Integration, shared files, final bundle | N/A |

## Shared Authority Files (Coordinator-only)

- reports/sprint83/final-verdict.md
- reports/sprint83/sprint-state.json
- reports/sprint83/publication/publication-truth-matrix-final.json
- reports/sprint83/publication/publication-summary.md
- reports/sprint83/evidence/evidence-contract-computed.json
- reports/sprint83/evidence/sprint83-final-validation-result.json
- reports/sprint83/review/final-consistency-check.json
- reports/sprint83/bundle-manifest.json

## Global Forbidden Actions

- no broad git add .
- no git reset --hard
- no git clean
- no direct push to main
- no PR creation without PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
- no merge without PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
- no branch deletion before post-merge verification
- no secret printing

## Overlap Check Reference

See 02-overlap-check.md for file ownership matrix.

## Integration Sequence

1. Lanes B, C, D, F, G run independently (no mutual dependencies)
2. Lane E runs independently (validator source + tests)
3. Lane A checks approval gate → SKIP (approval absent)
4. Lane H runs after all lanes complete
5. Coordinator integrates shared authority files
6. EV/ECC validation
7. Final adversarial review
8. Bundle and commit

---
*Sprint 83 coordinator plan -- 2026-05-24*
