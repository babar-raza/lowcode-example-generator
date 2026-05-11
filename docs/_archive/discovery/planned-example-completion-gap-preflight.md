# Planned Example Completion Gap Analysis — Gate 0 Preflight

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/planned-example-completion-gap-preflight.json`
**Verdict:** GATE_0_PASS

## Summary

28 artifacts inspected. 24 VERIFIED, 2 STALE (non-blocking), 1 NEEDS_FIX (taskcard matrix missing entries), 1 VERIFIED with notes.

## Critical Finding

The "planned=51" number from the cross-family lifecycle audit UNDERCOUNTS total planned scenarios. It comes from the readiness rank's planned_count, which uses the controlled pilot scope (22+25+4=51), not the full namespace type counts (22+25+101=148). The true candidate scenario count (runnable types only) is 43: Cells 9, Words 9, PDF 25.

## Cross-Family Numbers Verified

| Family | Discovered Types | Candidate (Runnable) | Published | Excluded | True Completion Rate |
|--------|-----------------|---------------------|-----------|----------|---------------------|
| Cells | 22 | 9 | 9 | 13 (non-runnable) | 100% |
| Words | 25 | 9 | 4 | 21 (16 non-runnable + 5 scope) | 44% |
| PDF | 101 | 25 | 2 | 99 (76 non-runnable + 23 scope) | 8% |
| **Total** | **148** | **43** | **15** | **133** | **35%** |

## Contradictions

1. PDF planned_count=4 in lifecycle audit vs 25 candidate WORKFLOW_ROOTs in type-role-classification. Resolution: 4 is the pilot plan, 25 is the full candidate count.
2. Taskcard matrix missing followup-example-reviewer-feedback-loop. Will be added in Phase 10.
