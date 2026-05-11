# Docs Migration Plan

Status: design only. Do not move, merge, split, archive, or delete docs in this phase.

## Migration Principles

- End state: `docs/` root contains only `README.md` plus approved folders and meta folders.
- Fewer canonical docs replace many preflight/result reports.
- Guides link to reference pages instead of repeating command/config/evidence tables.
- Historical reports move under `_archive/` with an archive note.
- Existing docs that are retained must be refreshed from code before becoming canonical.

## ROOT ORPHANS Mapping

Every root orphan from `docs/_audit/root_orphans.md` is accounted for here.

| orphan_path | new_path or merge target | action | rationale |
|---|---|---|---|
| `docs/monthly-runbook.md` | `docs/operations/monthly-maintenance.md` | merge | Root file is not allowed. Content overlaps monthly maintenance and must be reconciled with `.github/workflows/monthly-package-refresh.yml` and current CLI. |
| `docs/verifier-integration.md` | `docs/reference/validation-and-reviewer.md` | merge | Root file is not allowed. Content belongs in canonical validation/reviewer reference refreshed from `src/plugin_examples/verifier_bridge/`. |

No root orphan requires a Decision Needed entry.

## Migration Map

| current_path | new_path | action | rationale |
|---|---|---|---|
| `docs/monthly-runbook.md` | `docs/operations/monthly-maintenance.md` | merge | ROOT ORPHAN; consolidate monthly ops. |
| `docs/verifier-integration.md` | `docs/reference/validation-and-reviewer.md` | merge | ROOT ORPHAN; consolidate verifier bridge reference. |
| `docs/ci/environment-variables.md` | `docs/reference/environment-variables.md` | move | Env vars are canonical reference material. |
| `docs/discovery/current-state.md` | `docs/_archive/discovery/current-state.md` | archive | Outdated greenfield-era current state. |
| `docs/discovery/pipeline-module-integration-surface.md` | `docs/architecture/system-design.md` | merge | Preserve useful component material in canonical architecture. |
| `docs/discovery/implementation-gap-report.md` | `docs/_archive/discovery/implementation-gap-report.md` | archive | Historical gap report. |
| `docs/discovery/example-reviewer-integration-surface.md` | `docs/reference/validation-and-reviewer.md` | merge | Canonical reviewer reference target. |
| `docs/discovery/example-reviewer-fixture-system.md` | `docs/reference/validation-and-reviewer.md` | merge | Reviewer fixture details belong with validation/reviewer reference. |
| `docs/discovery/example-reviewer-feedback-loop-gap-analysis.md` | `docs/_archive/discovery/example-reviewer-feedback-loop-gap-analysis.md` | archive | Historical gap analysis. |
| `docs/discovery/llm-provider-policy-audit.md` | `docs/reference/metrics.md` | split | Provider policy goes to config/LLM sections; audit history archives. |
| `docs/discovery/family-scoped-evidence-layout-plan.md` | `docs/reference/evidence-and-file-contracts.md` | merge | Evidence layout is canonical reference material. |
| `docs/discovery/family-scoped-evidence-preflight-review.md` | `docs/_archive/discovery/family-scoped-evidence-preflight-review.md` | archive | Historical preflight. |
| `docs/discovery/family-scoped-evidence-promotion-result.md` | `docs/_archive/discovery/family-scoped-evidence-promotion-result.md` | archive | Historical result. |
| `docs/discovery/governance-closure-claim-audit.md` | `docs/_archive/discovery/governance-closure-claim-audit.md` | archive | Historical audit. |
| `docs/discovery/governance-closure-manual-review.md` | `docs/_archive/discovery/governance-closure-manual-review.md` | archive | Historical review. |
| `docs/discovery/live-pr-approval-implementation-review.md` | `docs/operations/live-publishing.md` | merge | Approval behavior belongs in live publishing runbook with links to publishing reference. |
| `docs/discovery/live-pr-approval-preflight-review.md` | `docs/_archive/discovery/live-pr-approval-preflight-review.md` | archive | Historical preflight. |
| `docs/discovery/real-pr-publisher-preflight-review.md` | `docs/_archive/discovery/real-pr-publisher-preflight-review.md` | archive | Superseded by publisher code and runbook. |
| `docs/discovery/repo-access-resolution-preflight-review.md` | `docs/reference/publishing-and-github.md` | merge | Repo access checks are canonical publishing reference. |
| `docs/discovery/repo-access-self-service-preflight.md` | `docs/reference/publishing-and-github.md` | merge | Repo access self-service belongs with publishing reference. |
| `docs/discovery/family-repo-mapping-preflight-review.md` | `docs/reference/configuration.md` | merge | Family repo mapping is family config reference material. |
| `docs/discovery/multi-family-discovery-claim-audit.md` | `docs/_archive/discovery/multi-family-discovery-claim-audit.md` | archive | Historical audit; discovery reference should be code-backed. |
| `docs/discovery/open-taskcard-closure-matrix.md` | `docs/development/taskcards.md` | merge | Keep generated matrix rules in contributor docs; generated output can be linked. |
| `docs/discovery/cross-family-example-lifecycle-audit.md` | `docs/reference/gates-and-verdicts.md` | merge | Lifecycle behavior belongs in gates/lifecycle reference. |
| `docs/discovery/cross-family-planned-completion-gap-analysis.md` | `docs/_archive/discovery/cross-family-planned-completion-gap-analysis.md` | archive | Historical analysis. |
| `docs/discovery/example-drop-prevention-capability-audit.md` | `docs/reference/gates-and-verdicts.md` | merge | Drop prevention maps to lifecycle/gate contracts. |
| `docs/discovery/example-lifecycle-backlog-hardening-preflight.md` | `docs/_archive/discovery/example-lifecycle-backlog-hardening-preflight.md` | archive | Historical preflight. |
| `docs/discovery/full-planned-example-completion-feasibility.md` | `docs/_archive/discovery/full-planned-example-completion-feasibility.md` | archive | Historical feasibility report. |
| `docs/discovery/planned-example-completion-gap-preflight.md` | `docs/_archive/discovery/planned-example-completion-gap-preflight.md` | archive | Historical preflight. |
| `docs/discovery/planned-example-completion-model.md` | `docs/reference/gates-and-verdicts.md` | merge | Only code-backed lifecycle model should remain canonical. |
| `docs/discovery/cells-pilot-proof-report.md` | `docs/_archive/discovery/cells-pilot-proof-report.md` | archive | Historical family report. |
| `docs/discovery/cells-tier5-e2e-evidence-review.md` | `docs/_archive/discovery/cells-tier5-e2e-evidence-review.md` | archive | Historical evidence review. |
| `docs/discovery/cells-tier5-monthly-rerun-proof.md` | `docs/_archive/discovery/cells-tier5-monthly-rerun-proof.md` | archive | Historical monthly proof. |
| `docs/discovery/cells-excluded-scenarios-root-cause-deep-dive.md` | `docs/_archive/discovery/cells-excluded-scenarios-root-cause-deep-dive.md` | archive | Historical family analysis. |
| `docs/discovery/words-catalog-review.md` | `docs/_archive/discovery/words-catalog-review.md` | archive | Historical family review. |
| `docs/discovery/words-excluded-scenarios-root-cause-deep-dive.md` | `docs/_archive/discovery/words-excluded-scenarios-root-cause-deep-dive.md` | archive | Historical family analysis. |
| `docs/discovery/words-fixture-registry-reprobe.md` | `docs/_archive/discovery/words-fixture-registry-reprobe.md` | archive | Historical reprobe. |
| `docs/discovery/words-pilot-verification-review.md` | `docs/_archive/discovery/words-pilot-verification-review.md` | archive | Historical verification report. |
| `docs/discovery/pdf-backlog-backfill-result.md` | `docs/_archive/discovery/pdf-backlog-backfill-result.md` | archive | Historical result. |
| `docs/discovery/pdf-excluded-examples-root-cause-review.md` | `docs/_archive/discovery/pdf-excluded-examples-root-cause-review.md` | archive | Historical analysis. |
| `docs/discovery/pdf-fixture-strategy-preflight-review.md` | `docs/_archive/discovery/pdf-fixture-strategy-preflight-review.md` | archive | Duplicate historical preflight. |
| `docs/discovery/pdf-fixture-strategy-review.md` | `docs/reference/evidence-and-file-contracts.md` | merge | Durable fixture findings belong in fixture/evidence reference. |
| `docs/discovery/pdf-options-aware-review.md` | `docs/_archive/discovery/pdf-options-aware-review.md` | archive | Historical family-specific review. |
| `docs/discovery/pdf-pilot-fixture-requirements.md` | `docs/reference/evidence-and-file-contracts.md` | merge | Only current fixture requirements should remain in canonical reference. |
| `docs/discovery/pdf-programmatic-fixture-validation.md` | `docs/_archive/discovery/pdf-programmatic-fixture-validation.md` | archive | Historical validation note. |
| `docs/discovery/pdf-role-options-sprint-preflight-review.md` | `docs/_archive/discovery/pdf-role-options-sprint-preflight-review.md` | archive | Historical sprint preflight. |
| `docs/discovery/pdf-splitter-optimizer-root-cause-deep-dive.md` | `docs/_archive/discovery/pdf-splitter-optimizer-root-cause-deep-dive.md` | archive | Historical root cause. |
| `docs/discovery/pdf-type-role-classification.md` | `docs/architecture/pipeline-stages.md` | merge | Code-backed type-role behavior belongs in scenario planning architecture. |
| `docs/discovery/pdf-wave1-preflight-review.md` | `docs/_archive/discovery/pdf-wave1-preflight-review.md` | archive | Historical preflight. |
| `docs/discovery/pdf-wave1-splitter-optimizer-result-analysis.md` | `docs/_archive/discovery/pdf-wave1-splitter-optimizer-result-analysis.md` | archive | Historical result. |
| `docs/discovery/pdf-wave1-tier5-preflight-review.md` | `docs/_archive/discovery/pdf-wave1-tier5-preflight-review.md` | archive | Historical preflight. |
| `docs/discovery/root-readme-template-preflight-review.md` | `docs/operations/readme-publishing.md` | merge | README workflow belongs in operations with reference links. |
| `docs/discovery/root-readme-workflow-manual-review.md` | `docs/operations/readme-publishing.md` | merge | README workflow belongs in operations. |
| `docs/discovery/sprint-a2-preflight-review.md` | `docs/_archive/discovery/sprint-a2-preflight-review.md` | archive | Historical sprint note. |
| `docs/plans/plugin-example-generation-execution-plan.md` | `docs/architecture/decisions.md` | split | Preserve active governance/decisions; archive stale plan body. AGENTS dependency must be updated in migration phase. |
| `docs/plans/plugin-example-generation-execution-plan copy.md` | `docs/_archive/plans/plugin-example-generation-execution-plan-copy.md` | archive | Duplicate copy; archive or delete after confirming no unique content. |
| `docs/plans/stream-a-plan-correction-review.md` | `docs/_archive/plans/stream-a-plan-correction-review.md` | archive | Historical correction review. |
| `docs/plans/r1-pdf-optimizer-rerun-result.md` | `docs/_archive/plans/r1-pdf-optimizer-rerun-result.md` | archive | Historical result. |
| `docs/plans/r1-preflight-truth-verification.md` | `docs/_archive/plans/r1-preflight-truth-verification.md` | archive | Historical preflight. |
| `docs/plans/r2-final-verification.md` | `docs/_archive/plans/r2-final-verification.md` | archive | Historical verification. |
| `docs/plans/r2-pdf-lifecycle-readiness-update.md` | `docs/_archive/plans/r2-pdf-lifecycle-readiness-update.md` | archive | Historical update. |
| `docs/plans/r3-final-verification.md` | `docs/_archive/plans/r3-final-verification.md` | archive | Historical verification. |
| `docs/plans/r3-pdf-pr3-live-pr-result.md` | `docs/_archive/plans/r3-pdf-pr3-live-pr-result.md` | archive | Historical PR result. |
| `docs/plans/r3-resume-final-verification.md` | `docs/_archive/plans/r3-resume-final-verification.md` | archive | Historical verification. |
| `docs/plans/agent-metrics-tc14-gate-checklist.md` | `docs/operations/telemetry.md` | merge | Metrics operation checklist belongs in telemetry ops. |
| `docs/plans/agent-metrics-tc14-independent-verification-preflight.md` | `docs/_archive/plans/agent-metrics-tc14-independent-verification-preflight.md` | archive | Historical preflight. |
| `docs/plans/agent-metrics-tc14-production-shaped-dry-run.md` | `docs/operations/telemetry.md` | merge | Durable metrics dry-run behavior belongs in telemetry ops. |
| `docs/plans/agent-metrics-tc14-sheet-confirmation.md` | `docs/_archive/plans/agent-metrics-tc14-sheet-confirmation.md` | archive | Historical confirmation. |
| `docs/plans/agent-metrics-tc14-source-gate-preflight.md` | `docs/_archive/plans/agent-metrics-tc14-source-gate-preflight.md` | archive | Historical preflight. |
| `docs/plans/example-failure-recovery-system-limitation-plan.md` | `docs/operations/troubleshooting.md` | merge | Failure recovery belongs in troubleshooting if code-backed. |
| `docs/plans/full-completion-remediation-architecture.md` | `docs/_archive/plans/full-completion-remediation-architecture.md` | archive | Historical architecture plan. |
| `docs/plans/full-completion-roadmap.md` | `docs/_archive/plans/full-completion-roadmap.md` | archive | Historical roadmap. |
| `docs/plans/lowcode-all-family-candidate-inventory.md` | `docs/_archive/plans/lowcode-all-family-candidate-inventory.md` | archive | Historical inventory; configs are source. |
| `docs/plans/lowcode-all-family-current-state-board.md` | `docs/_archive/plans/lowcode-all-family-current-state-board.md` | archive | Historical board. |
| `docs/plans/lowcode-all-family-denominator-model.md` | `docs/reference/schemas-and-contracts.md` | merge | Denominator model belongs in schema/contract reference. |
| `docs/plans/lowcode-all-family-roadmap.md` | `docs/_archive/plans/lowcode-all-family-roadmap.md` | archive | Historical roadmap. |
| `docs/plans/lowcode-dropped-planned-example-healing-model.md` | `docs/reference/gates-and-verdicts.md` | merge | Healing/backlog model belongs in lifecycle/gates reference if code-backed. |
| `docs/plans/lowcode-example-relaunch-governance.md` | `docs/_archive/plans/lowcode-example-relaunch-governance.md` | archive | Historical governance. |
| `docs/plans/lowcode-execution-handoff.md` | `docs/_archive/plans/lowcode-execution-handoff.md` | archive | Historical handoff. |
| `docs/plans/lowcode-failed-verification-root-cause-register.md` | `docs/_archive/plans/lowcode-failed-verification-root-cause-register.md` | archive | Historical register. |
| `docs/plans/lowcode-final-investigation-verdict.md` | `docs/_archive/plans/lowcode-final-investigation-verdict.md` | archive | Historical verdict. |
| `docs/plans/lowcode-risk-and-contradiction-register.md` | `docs/_archive/plans/lowcode-risk-and-contradiction-register.md` | archive | Historical register. |
| `docs/plans/lowcode-scope-correction-verdict.md` | `docs/_archive/plans/lowcode-scope-correction-verdict.md` | archive | Historical verdict. |
| `docs/plans/new-family-controlled-pilot-readiness-20260511-105914.md` | `docs/_archive/plans/new-family-controlled-pilot-readiness-20260511-105914.md` | archive | Timestamped report. |
| `docs/plans/new-family-fixture-harness-verdict.md` | `docs/_archive/plans/new-family-fixture-harness-verdict.md` | archive | Historical verdict. |
| `docs/plans/new-family-type-role-classification-summary-20260511-105914.md` | `docs/_archive/plans/new-family-type-role-classification-summary-20260511-105914.md` | archive | Timestamped report. |
| `docs/plans/pdf-fixture-generator-change-plan.md` | `docs/_archive/plans/pdf-fixture-generator-change-plan.md` | archive | Historical change plan. |
| `docs/publishing/monthly-maintenance-runbook.md` | `docs/operations/monthly-maintenance.md` | merge | Canonical monthly runbook target. |
| `docs/publishing/agent-metrics-runbook.md` | `docs/operations/telemetry.md` | merge | Metrics operations belong in telemetry ops with `reference/metrics.md`. |
| `docs/publishing/agent-operated-live-pr-runbook.md` | `docs/operations/live-publishing.md` | merge | Canonical live publishing runbook target. |
| `docs/publishing/post-merge-verification-runbook.md` | `docs/operations/post-merge-verification.md` | move | Canonical post-merge runbook. |
| `docs/publishing/live-pr-review-preflight.md` | `docs/operations/live-publishing.md` | merge | Merge durable preflight steps; archive old report. |
| `docs/publishing/repository-launch-consistency-preflight.md` | `docs/reference/publishing-and-github.md` | merge | Repo launch consistency belongs in publishing reference. |
| `docs/publishing/remote-root-readme-status.md` | `docs/_archive/publishing/remote-root-readme-status.md` | archive | Historical audit. |
| `docs/publishing/release-closure-review.md` | `docs/_archive/publishing/release-closure-review.md` | archive | Historical release review. |
| `docs/publishing/release-inventory-cells-words.md` | `docs/_archive/publishing/release-inventory-cells-words.md` | archive | Historical inventory. |
| `docs/publishing/sprint-a1-concurrency-state-review.md` | `docs/_archive/publishing/sprint-a1-concurrency-state-review.md` | archive | Historical sprint review. |
| `docs/publishing/stream-a-closure-verification.md` | `docs/_archive/publishing/stream-a-closure-verification.md` | archive | Historical closure verification. |
| `docs/publishing/cells-live-pr-result.md` | `docs/_archive/publishing/cells-live-pr-result.md` | archive | Historical result. |
| `docs/publishing/cells-merge-preflight-review.md` | `docs/_archive/publishing/cells-merge-preflight-review.md` | archive | Historical preflight. |
| `docs/publishing/cells-merge-result.md` | `docs/_archive/publishing/cells-merge-result.md` | archive | Historical result. |
| `docs/publishing/cells-post-merge-validation.md` | `docs/_archive/publishing/cells-post-merge-validation.md` | archive | Historical validation. |
| `docs/publishing/cells-readme-backfill-pr-result.md` | `docs/_archive/publishing/cells-readme-backfill-pr-result.md` | archive | Historical result. |
| `docs/publishing/words-live-pr-result.md` | `docs/_archive/publishing/words-live-pr-result.md` | archive | Historical result. |
| `docs/publishing/words-live-pr-post-creation-review.md` | `docs/_archive/publishing/words-live-pr-post-creation-review.md` | archive | Historical review. |
| `docs/publishing/words-merge-result.md` | `docs/_archive/publishing/words-merge-result.md` | archive | Historical result. |
| `docs/publishing/words-readme-backfill-pr-result.md` | `docs/_archive/publishing/words-readme-backfill-pr-result.md` | archive | Historical result. |
| `docs/publishing/pdf-live-pr-post-creation-full-review.md` | `docs/_archive/publishing/pdf-live-pr-post-creation-full-review.md` | archive | Historical review. |
| `docs/publishing/pdf-pr-packaging-preflight-review.md` | `docs/_archive/publishing/pdf-pr-packaging-preflight-review.md` | archive | Historical preflight. |
| `docs/publishing/pdf-pr1-and-cross-family-audit-preflight.md` | `docs/_archive/publishing/pdf-pr1-and-cross-family-audit-preflight.md` | archive | Historical preflight. |
| `docs/publishing/pdf-pr1-merge-result.md` | `docs/_archive/publishing/pdf-pr1-merge-result.md` | archive | Historical result. |
| `docs/publishing/pdf-pr1-post-merge-verification.md` | `docs/_archive/publishing/pdf-pr1-post-merge-verification.md` | archive | Historical verification. |
| `docs/publishing/pdf-pr1-pre-merge-clean-checkout-validation.md` | `docs/_archive/publishing/pdf-pr1-pre-merge-clean-checkout-validation.md` | archive | Historical validation. |
| `docs/publishing/readme-backfill-pr-review-preflight.md` | `docs/operations/readme-publishing.md` | merge | README PR workflow belongs in one runbook. |
| `docs/publishing/readme-backfill-token-recheck-preflight.md` | `docs/_archive/publishing/readme-backfill-token-recheck-preflight.md` | archive | Historical token preflight. |
| `docs/publishing/readme-backfill-post-merge-verification.md` | `docs/_archive/publishing/readme-backfill-post-merge-verification.md` | archive | Historical verification. |

## Canonical Merge Targets

| target | sources to merge |
|---|---|
| `docs/operations/monthly-maintenance.md` | `docs/monthly-runbook.md`, `docs/publishing/monthly-maintenance-runbook.md`, durable lessons from `docs/discovery/cells-tier5-monthly-rerun-proof.md` |
| `docs/reference/validation-and-reviewer.md` | `docs/verifier-integration.md`, `docs/discovery/example-reviewer-integration-surface.md`, `docs/discovery/example-reviewer-fixture-system.md` |
| `docs/operations/live-publishing.md` | `docs/publishing/agent-operated-live-pr-runbook.md`, `docs/publishing/live-pr-review-preflight.md`, `docs/discovery/live-pr-approval-implementation-review.md` |
| `docs/operations/readme-publishing.md` | `docs/discovery/root-readme-template-preflight-review.md`, `docs/discovery/root-readme-workflow-manual-review.md`, `docs/publishing/readme-backfill-pr-review-preflight.md` |
| `docs/reference/evidence-and-file-contracts.md` | `docs/discovery/family-scoped-evidence-layout-plan.md`, fixture strategy docs, evidence portions of audit |
| `docs/reference/gates-and-verdicts.md` | lifecycle/drop-prevention/planned-completion docs, gate references from audit |
| `docs/reference/configuration.md` | family repo mapping, denominator/config-related plans, config schema material |
| `docs/operations/telemetry.md` | agent metrics runbook and TC14 operational docs |
| `docs/reference/publishing-and-github.md` | repo access, publish readiness, GitHub publishing behavior |

## Decision Needed

None for root orphans. During actual migration, one decision remains outside root hygiene:

- `docs/plans/plugin-example-generation-execution-plan.md`: because `AGENTS.md` currently requires reading this plan before implementation, decide whether to keep an active slim governance document at this path temporarily or update `AGENTS.md` to point to `docs/architecture/decisions.md`. Criteria: preserve mandatory governance rules, remove stale current-state claims, and avoid a broken required link.
