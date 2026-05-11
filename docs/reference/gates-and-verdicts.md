# Gates and Verdicts

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/gates/`, `src/plugin_examples/runner.py`

## Stage Gates

The runner executes ordered stages from `STAGE_DEFINITIONS`:

1. `load_config`
2. `nuget_fetch`
3. `dependency_resolution`
4. `extraction`
5. `reflection`
6. `plugin_detection`
7. `source_of_truth_gate` is combined into plugin detection
8. `api_delta`
9. `impact_mapping`
10. `fixture_registry`
11. `example_mining`
12. `scenario_planning`
13. `llm_preflight`
14. `generation`
15. `validation`
16. `reviewer`
17. `publisher`

Hard-stop stages are:

- `load_config`
- `nuget_fetch`
- `dependency_resolution`
- `extraction`
- `reflection`
- `plugin_detection`
- `scenario_planning`

## Aggregate Verdicts

Verdicts are defined in `src/plugin_examples/gates/models.py` and computed in `evaluator.py` and `example_gates.py`.

Successful or publishable verdicts:

- `FULL_E2E_PASSED`
- `PR_READY`
- `PR_DRY_RUN_READY`
- `PARTIAL_PR_READY`
- `PARTIAL_PR_DRY_RUN_READY`
- `SOURCE_OF_TRUTH_PROVEN_ONLY`
- `DATA_FLOW_PROTOTYPE_ONLY`

Blocked verdicts:

- `BLOCKED_SOURCE_OF_TRUTH`
- `BLOCKED_FIXTURE_DISCOVERY`
- `BLOCKED_SCENARIO_PLANNING`
- `BLOCKED_GENERATION`
- `BLOCKED_RESTORE_FAILED`
- `BLOCKED_BUILD_FAILED`
- `BLOCKED_RUN_FAILED`
- `BLOCKED_OUTPUT_VALIDATION_FAILED`
- `BLOCKED_REVIEWER_UNAVAILABLE`
- `BLOCKED_REVIEWER_FAILED`
- `BLOCKED_NO_PUBLISHABLE_EXAMPLES`

## Per-Example Verdicts

Per-example verdicts include:

- `EXAMPLE_READY`
- `EXAMPLE_BLOCKED_RESTORE_FAILED`
- `EXAMPLE_BLOCKED_BUILD_FAILED`
- `EXAMPLE_BLOCKED_RUN_FAILED`
- `EXAMPLE_BLOCKED_OUTPUT_VALIDATION_FAILED`
- `EXAMPLE_BLOCKED_REVIEWER_FAILED`
- `EXAMPLE_BLOCKED_MISSING_FIXTURE`
- `EXAMPLE_BLOCKED_RUNTIME_CONTEXT_REQUIRED`

## Output Files

- `gate-results.json`
- `example-gate-results.json`
- `aggregate-gate-results.json`
- `pr-candidate-manifest.json`
- `scenario-feedback-updates.json`
- `example-lifecycle-records.json`

See [File Contracts](file-contracts.md).
