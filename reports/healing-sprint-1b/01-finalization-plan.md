# Healing Sprint 1B — Finalization Plan

**Author:** Coordinator Agent (Lane 0)
**Date:** 2026-05-27

## Sprint Type

Machinery-healing finalization. Not product work. Not publication work.
No new readiness loop. No live PRs. No merges.

## Lane Assignments

| Lane | Owner | Scope |
|---|---|---|
| 0 | Coordinator | Audit, overlap, ECC, verdict, bundle |
| 1 | Final Proof Agent | README.md commit, git proof, SHA authority |
| 2 | State Sync Agent | Taskcard finalization, next-gate register |
| 3 | Replay Agent | Executable bad-bundle checks |
| 4 | Gate Agent | Re-run gate/dry-run simulation |
| 5 | Validator Agent | ECC, evidence contract, bundle audit |
| 6 | IV Agent | Full independent verification |

## Execution Order

1. Lane 1 first — must commit README.md and capture clean git state
2. Lanes 2-5 in parallel (independent)
3. Lane 6 after all other lanes complete
4. Final integration after Lane 6

## Stop Conditions

| Condition | Action |
|---|---|
| README.md commit fails | Abort, classify as ENV_BLOCKER |
| ECC closure_valid=false | Repair missing files, re-run |
| IV finds stale text in any final authority file | Repair and re-run IV |
| Any final file says "will be committed" or "will be updated" | Repair immediately |
| Phantom SHA in manifest | Repair immediately |

## Allowed Verdicts

- LOWCODE_MACHINERY_HEALING_ACCEPTED
- LOWCODE_MACHINERY_HEALING_ACCEPTED_WITH_NON_BLOCKING_NOTES
- LOWCODE_MACHINERY_HEALING_PARTIAL_WITH_EXPLICIT_BLOCKERS
- EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED

## Preferred Verdict

LOWCODE_MACHINERY_HEALING_ACCEPTED (if all blockers resolved)

## Healing Sprint 2 Decision Rule

Healing Sprint 2 is recommended ONLY IF:
- Any key automated replay check cannot be implemented safely in Sprint 1B
- OR any blocker cannot be fully resolved in Sprint 1B

Otherwise: Healing Sprint 2 is NOT needed.
