# Planner Action-State Semantics Repair

## Problem
Planner board listed recurring read-only checks (PORTFOLIO_CONSERVATION_CHECK, VERSION_DRIFT_CHECK, etc.) as safe_to_execute_now=true even after execution, confusing agents about what work remains.

## Solution
- Added `execution_state` field to Action with 8 possible values
- Added `RECURRING_CHECK_IDS` to identify read-only recurring checks
- Added `mark_executed()` to set execution_state after planner loop execution
- Added `next_required_actions()` that excludes executed no-ops
- Blocked actions get proper `blocked_by_*` execution_state on creation

## Tests
10 new tests added. 71 total tests pass.

## Commit: f216bd7
