# Planned Example Completion Model

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/planned-example-completion-model.json`
**Verdict:** COMPLETION_MODEL_DEFINED

## 12-Stage Completion Model

| Stage | Name | Description |
|-------|------|-------------|
| 1 | discovered_api_item | Public type in LowCode namespace via DllReflector |
| 2 | candidate_scenario | Type classified as runnable (workflow_root/operation_facade) |
| 3 | planned_example | Scenario planner built Scenario object |
| 4 | selected_example | Passes allowlist + readiness checks |
| 5 | generated_example | LLM produced Program.cs + project files |
| 6 | repaired_example | Build/runtime repair succeeded (optional) |
| 7 | reviewer_checked | Reviewer evaluated the example |
| 8 | validated_example | All gates passed |
| 9 | package_candidate | Assembled into PR dry-run package |
| 10 | pr_published | Live PR created |
| 11 | merged | PR merged, clean-checkout validated |
| 12 | deferred/backlogged | Intentionally excluded with documented path |

## Key Definitions

- **Planned** = Stage 3 (scenario planner creates a Scenario)
- **Acceptable exclusion** = non-runnable type OR intentional pilot scope limit with backlog
- **System gap exclusion** = runnable type excluded because system lacks capability
- **Full completion metric** = merged_count / candidate_scenario_count

## Current True Completion Rate: 35% (15/43)
