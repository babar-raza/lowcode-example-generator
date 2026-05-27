# Healing Sprint 1 — Healing Plan

**Author:** Coordinator Agent (Lane 0)
**Date:** 2026-05-27

## Goal

Stress-test the full LowCode publication/evidence machinery so future tasks do not require
dozens of narrow repair sprints.

## Lane Plan

| Lane | Owner | Key Output | Stop Condition |
|---|---|---|---|
| 0 | Coordinator | Plan, overlap check, ECC, final verdict | — |
| 1 | Final Proof | Stale-wording audit, proof template rule | Active file contains stale text that can't be fixed without altering accepted history |
| 2 | Replay | Bad-bundle regression matrix | No fixtures creatable, validator CLI unavailable |
| 3 | Gate Simulation | Dry-run PR/merge plan, no-op proof | Gate simulation attempts real mutation |
| 4 | Validator | Gap analysis, invariant hardening, tests | Validator source unavailable |
| 5 | Evidence Contract | Final-closeout contract, bundle audit | — |
| 6 | Dry-Run | Local machinery dry-run, file plan verification | Handoff data missing |
| 7 | State Sync | Taskcard audit, no-readiness-loop check | — |
| 8 | IV | All lane verification | IV finds unrepaired blocking issue |

## Execution Order

1. All lanes run in parallel (non-overlapping paths)
2. Lane 8 (IV) runs after all other lanes complete
3. Coordinator runs repair loop if IV finds issues
4. Final ECC, bundle, commit

## Overlap Rules

- Lane 0 owns all `reports/healing-sprint-1/final-verdict.md`, `sprint-state.json`, `bundle-manifest.json`, `review/*`
- Lane 1 owns `final-proof/`, `git/`, `evidence-consistency/`
- Lane 2 owns `replay/`
- Lane 3 owns `gates/`
- Lane 4 owns `evidence/validator-*`
- Lane 5 owns `evidence-contract/`, `bundle-audit/`
- Lane 6 owns `dry-run/`
- Lane 7 owns `state-sync/`, `tracking/`
- Lane 8 owns `iv/`, `review/iv-findings.md`
- No lane writes to another lane's owned paths
