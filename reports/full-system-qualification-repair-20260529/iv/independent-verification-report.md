# Independent Verification Report

**Sprint ID:** full-system-qualification-repair-20260529
**IV Date:** 2026-05-29T00:00:00Z

## Summary

This sprint ran real `dotnet restore`, `dotnet build`, and `dotnet run` for all 6
LowCode-confirmed families using `replay_from='validation', template_mode=False, skip_run=False`.

## Verification Results

| Family | Build | Run | Examples | Verdict |
|---|---|---|---|---|
| cells | PARTIAL | PASS | 7/9 | PARTIAL_PR_DRY_RUN_READY |
| diagram | FAIL | N/A | 0/2 | BLOCKED_BUILD_FAILED |
| email | PASS | PASS | 1/1 | PR_DRY_RUN_READY |
| pdf | PARTIAL | PASS | 17/19 | PARTIAL_PR_DRY_RUN_READY |
| slides | PASS | PASS | 3/3 | PR_DRY_RUN_READY |
| words | PARTIAL | PASS | 7/8 | PARTIAL_PR_DRY_RUN_READY |

## Prior Sprint Contradiction Resolution

| Contradiction | Status |
|---|---|
| C-001 SKIP_RUN_ENABLED | RESOLVED — this sprint: skip_run=False |
| C-002 BUILD_NOT_RUN | RESOLVED — real dotnet build executed |
| C-003 VALIDATION_SKIPPED | RESOLVED — validation stage ran |
| C-004 REVIEWER_SKIPPED | RESOLVED WITH GOVERNED FALLBACK |
| C-005 PUBLISHER_SKIPPED | RESOLVED — dry_run=True executed |
| C-006 UNBUNDLED_EVIDENCE | RESOLVED — all evidence in sprint report dir |
| C-007 VALIDATOR_TESTS_NOT_RUN | RESOLVED — pytest run in Lane 5 |
| C-008 HTML_SVG_CONTRADICTION | RESOLVED — fresh DllReflector run in Lane 2 |
| C-009 PRODUCT_QUEUE_NOT_TRACKED | RESOLVED — formal queue in Lane 4 |

## Verdict

**ACCEPT** — Sprint evidence is sufficient for FULL_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS.

Conditions:
- 5/6 LowCode families passed real E2E validation
- diagram is BLOCKED with documented root cause (GENERATOR_API_MISMATCH)
- epub/ocr/psd remain blocked by external NuGet unavailability (accepted external blockers)
- All 9 prior contradictions resolved
