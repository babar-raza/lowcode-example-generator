# Lane 4: Full E2E Validation Results

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## Aggregate

- Total generated: 42
- Total build passed: 42
- Total runtime passed: 42
- Total failed: 0
- All pass: True

## Per-Family Results

| Family | Run ID | Generated | Build Pass | Runtime Pass | Failed | Verdict |
|--------|--------|-----------|------------|--------------|--------|---------|
| cells | pilot-cells-20260529-221017 | 9 | 9 | 9 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| diagram | pilot-diagram-20260529-221021 | 2 | 2 | 2 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| words | pilot-words-20260529-221024 | 8 | 8 | 8 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| pdf | pilot-pdf-20260529-222233 | 19 | 19 | 19 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| email | pilot-email-20260529-220716 | 1 | 1 | 1 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| slides | pilot-slides-20260529-221814 | 3 | 3 | 3 | 0 | DATA_FLOW_PROTOTYPE_ONLY |
| **TOTAL** | | **42** | **42** | **42** | **0** | |

## Validation Method

Each example was validated via `dotnet restore && dotnet build && dotnet run` within the 
pipeline's `verifier_bridge.dotnet_runner` module. No manual workspace patching was performed.
All fixes are encoded in generator-level templates (`template_first: true` per_type_constraints).

## Gate Semantics

All families report `DATA_FLOW_PROTOTYPE_ONLY` verdict because `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`
approval gate is not set. This is the expected state for pre-publication review.
The gate_generation stage PASSES (examples_generated > 0) for all families.
