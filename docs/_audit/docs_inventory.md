# Documentation Inventory

Audit date: 2026-05-30

Status vocabulary:

- Accurate: appears aligned with current code surface at a high level.
- Partial: useful but needs refresh or narrower source-of-truth language.
- Outdated: conflicts with current code or governance.
- Duplicate: overlaps with another doc and should be merged or archived.
- Unknown: not fully validated against code in this audit.

Root-orphan result: no root orphan files were found. `docs/README.md` is the only direct file under `docs/`.

## Active Docs

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| `README.md` | operator/contributor | Repository entry point. | Partial | keep | Must stay clear that this is pipeline repo, not published examples repo. |
| `AGENTS.md` | agents/contributors | Governance and agent rules. | Partial | keep | LLM endpoint rules conflict with `llm_router/router.py`; docs/code alignment needed. |
| `docs/README.md` | all | Docs index/root landing. | Accurate | keep | Only permitted docs root file. |
| `docs/overview/product.md` | user/operator | Product/system overview. | Partial | keep | Should be refreshed from `pyproject.toml`, `__main__.py`, and `runner.py`. |
| `docs/overview/concepts.md` | user/operator/contributor | Core concepts. | Partial | keep | Should link source-of-truth hierarchy to reflection/catalog code. |
| `docs/architecture/decisions.md` | contributor | Active governance/decision summary. | Partial | keep | Required by AGENTS. Needs explicit known code mismatch for LLM endpoint or tracked remediation link. |
| `docs/architecture/system-design.md` | contributor | System architecture. | Partial | keep | Refresh against current component map and stage list. |
| `docs/architecture/pipeline-stages.md` | operator/contributor | Pipeline stage reference. | Partial | keep | Must include current `version_drift_preflight`, replay behavior, family-scoped evidence. |
| `docs/getting-started/operator-quickstart.md` | operator | First-run operator guide. | Partial | keep | Needs current env var guidance: `GH_TOKEN` mapping to `GITHUB_TOKEN`, GPT endpoint hard blocker. |
| `docs/getting-started/contributor-quickstart.md` | contributor | Contributor setup. | Partial | keep | Should align with Python `>=3.12`, pytest config, package script. |
| `docs/guides/run-family-pipeline.md` | operator | Run a family pipeline. | Partial | keep | Refresh command flags from `__main__.py`. |
| `docs/guides/generate-and-validate-examples.md` | operator/contributor | Generation and validation workflow. | Partial | keep | Must mention deterministic template paths and validation stop order. |
| `docs/guides/discovery-sweep.md` | operator | Discovery-only sweep. | Partial | keep | Align with `discover-lowcode` flags and discovery-only status rules. |
| `docs/guides/add-or-update-family.md` | contributor | Family config authoring. | Partial | keep | Should be regenerated from `family-config.schema.json` and `family_config/models.py`. |
| `docs/operations/live-publishing.md` | operator | Live PR publishing. | Partial | keep | Must include approval/env/token/repo access gates from publisher code. |
| `docs/operations/monthly-maintenance.md` | operator | Maintenance and reruns. | Partial | keep | Needs current version drift and denominator behavior. |
| `docs/operations/post-merge-verification.md` | operator | Post-merge verification. | Duplicate | merge | Merge with `docs/publishing/post-merge-verification-runbook.md`; keep one canonical ops doc. |
| `docs/publishing/post-merge-verification-runbook.md` | operator | Post-merge verification runbook. | Duplicate | merge | Duplicate target with operations doc. Proposed canonical target: `docs/operations/post-merge-verification.md`. |
| `docs/operations/readme-publishing.md` | operator | README rendering/publishing. | Partial | keep | Verify current approval env vars and `--cumulative` behavior. |
| `docs/operations/telemetry.md` | operator | Metrics/telemetry operations. | Partial | keep | Align with `pipeline/configs/metrics.yml` and `metrics/config.py`; family map is limited. |
| `docs/operations/troubleshooting.md` | operator | Troubleshooting. | Partial | keep | Should include LLM endpoint hard blocker and evidence path guidance. |
| `docs/development/contributing.md` | contributor | Contribution workflow. | Partial | keep | Should reference no direct main push and PR evidence gates. |
| `docs/development/repo-structure.md` | contributor | Repo layout. | Partial | keep | Needs current component map and data dirs. |
| `docs/development/testing.md` | contributor | Test running strategy. | Partial | keep | Should include 101 unit test files and focused test groups. |
| `docs/development/taskcards.md` | contributor/operator | Taskcard workflow. | Unknown | keep | Needs code evidence from `sync-taskcard-docs` and related scripts. |
| `docs/development/open-taskcard-closure-matrix.md` | contributor/operator | Generated taskcard closure matrix. | Unknown | keep | Likely generated; verify against `scripts/sync_taskcards.py`. |
| `docs/reference/cli.md` | operator/contributor | CLI reference. | Partial | keep | High drift risk; update from argparse in `__main__.py`. |
| `docs/reference/config.md` | contributor/operator | Config reference. | Partial | keep | Should be generated from schema/models. |
| `docs/reference/environment-variables.md` | operator | Env var reference. | Outdated | merge | Needs hard correction for LLM endpoint governance and current env vars. |
| `docs/reference/file-contracts.md` | contributor/operator | File/evidence contracts. | Partial | keep | Needs current family-scoped evidence and full evidence filename list. |
| `docs/reference/gates-and-verdicts.md` | operator/contributor | Gate/verdict reference. | Partial | keep | Must include degraded partial runtime semantics and publishable verdicts. |
| `docs/reference/metrics.md` | operator | Metrics reference. | Partial | keep | Align with metrics config and ledger behavior. |
| `docs/reference/publishing-and-github.md` | operator | GitHub publishing reference. | Partial | keep | Align with approval gate, repo access, permission probes. |
| `docs/reference/schemas-and-contracts.md` | contributor | JSON schema/evidence contract reference. | Partial | keep | Separate current schemas from historical report bundle rules. |
| `docs/reference/validation-and-reviewer.md` | operator/contributor | Validation/reviewer details. | Partial | keep | Align with dotnet runner, output validator, reviewer preflight. |
| `pipeline/format-authority/README.md` | contributor | Format authority README. | Partial | keep | Should be linked from active reference docs. |
| `pipeline/prompts/example-generator.md` | LLM/pipeline | Generation prompt template. | Accurate | keep | Code input, not operator guide. |
| `pipeline/prompts/example-repair.md` | LLM/pipeline | Repair prompt template. | Accurate | keep | Code input, not operator guide. |

## Audit Docs

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| `docs/_audit/system_audit.md` | humans/future LLMs | Code-first system audit. | Accurate | keep | Refreshed by this audit. |
| `docs/_audit/docs_inventory.md` | humans/future LLMs | Documentation inventory and actions. | Accurate | keep | Refreshed by this audit. |
| `docs/_audit/traceability.md` | humans/future LLMs | Feature to evidence/docs/gaps traceability. | Accurate | keep | Refreshed by this audit. |
| `docs/_audit/root_orphans.md` | humans/future LLMs | Docs root hygiene sweep. | Accurate | keep | Refreshed by this audit; no orphans found. |
| `docs/_audit/docs_migration_plan.md` | contributor | Prior migration plan. | Partial | archive | Keep as historical after current audit drives next migration. |
| `docs/_audit/README_IA_PROPOSAL.md` | contributor | Prior IA proposal. | Partial | archive | Superseded by current inventory unless still actively used. |
| `docs/_audit/style_guide.md` | contributor | Docs style guide. | Unknown | keep | Validate separately before using as policy. |

## Archive Docs

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| `docs/_archive/README.md` | contributor | Archive index. | Accurate | keep | Archive marker. |
| `docs/_archive/discovery/*.md` | contributor/auditor | Historical discovery reports. | Outdated | archive | Do not use as active guidance unless decision is restated in `docs/architecture/decisions.md` or code. |
| `docs/_archive/merged/*.md` | contributor/auditor | Historical docs merged into active docs. | Duplicate | archive | Keep archived; avoid linking from active quickstarts except history. |
| `docs/_archive/plans/*.md` | contributor/auditor | Historical plans. | Outdated | archive | `plugin-example-generation-execution-plan.md` is historical per `docs/architecture/decisions.md`. |
| `docs/_archive/publishing/*.md` | contributor/auditor | Historical publishing results/reviews. | Outdated | archive | Use current publisher code and active ops docs for procedure. |
| `docs/_archive/root-orphans/monthly-runbook.md` | contributor/auditor | Prior root orphan archived from docs root. | Outdated | archive | Confirms prior orphan was archived. |
| `docs/_archive/root-orphans/verifier-integration.md` | contributor/auditor | Prior root orphan archived from docs root. | Outdated | archive | Confirms prior orphan was archived. |

## Reports and Generated Documentation Artifacts

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| `reports/final-publication/**/*.md` | auditor/operator | Final publication evidence and verdicts. | Unknown | archive | Treat as evidence bundle, not active procedure. |
| `reports/full-system-qualification-repair-20260529/**/*.md` | auditor | System qualification repair evidence. | Unknown | archive | Historical evidence. |
| `reports/healing-sprint-*/*.md` | auditor | Healing sprint plans/verdicts. | Unknown | archive | Historical evidence. |
| `reports/lowcode-*/**/*.md` | auditor | LowCode closure/e2e/generated source reports. | Unknown | archive | Historical/generated artifacts; do not use as source of active behavior. |
| `reports/system-qualification/**/*.md` | auditor | System qualification evidence. | Unknown | archive | Historical evidence. |
| `reports/sprint91/**/*.md` | auditor | Sprint 91 state/evidence. | Unknown | archive | Historical evidence. |

## Root Orphans

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| None | N/A | No root orphan files found. | Accurate | keep | Sweep found only `docs/README.md` directly under `docs/`. |

## Top Documentation Problems

1. LLM endpoint policy in governance conflicts with router code; docs must not hide this.
2. CLI reference is likely stale because commands/flags are numerous and centralized in code.
3. Post-merge verification docs are duplicated between `docs/operations/` and `docs/publishing/`.
4. Historical reports and archived plans can be mistaken for active guidance.
5. File-contract docs must distinguish run-scoped evidence from promoted family-scoped evidence and legacy aliases.
6. Config docs need to be generated or checked from schema/dataclasses.
7. Environment variable docs need to separate operator storage `GH_TOKEN` from code-read `GITHUB_TOKEN`.
8. Metrics docs must not imply all families are mapped when config maps only `cells`, `words`, `pdf`.
9. Generation docs need to cover template-first and deterministic paths, not only LLM paths.
10. There is no found root-doc hygiene enforcement despite the root-orphan contract.
