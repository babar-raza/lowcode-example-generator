# Documentation Migration Plan

Source inputs:

- `docs/_audit/system_audit.md`
- `docs/_audit/docs_inventory.md`
- `docs/_audit/traceability.md`
- `docs/_audit/root_orphans.md`

This is a design-only plan. Do not move, merge, archive, or delete files in this phase.

## Migration Table

| current_path | new_path | action | rationale |
|---|---|---|---|
| `README.md` | `README.md` | keep | Repo root README should remain brief and link to `docs/README.md`. |
| `AGENTS.md` | `AGENTS.md` | keep | Governance file remains at repo root; cite from docs where relevant without duplicating. |
| `docs/README.md` | `docs/README.md` | keep | Docs home and navigation front door. |
| `docs/overview/product.md` | `docs/overview/product.md` | refresh | Keep overview but align with code-derived system purpose. |
| `docs/overview/concepts.md` | `docs/overview/concepts.md` | refresh | Keep conceptual scope; link to reference pages for detail. |
| `docs/getting-started/operator-quickstart.md` | `docs/getting-started/operator-quickstart.md` | refresh | Keep as short operator path; link to CLI/env/file references. |
| `docs/getting-started/contributor-quickstart.md` | `docs/getting-started/contributor-quickstart.md` | refresh | Keep as contributor entry; link to testing, architecture, config reference. |
| `docs/guides/run-family-pipeline.md` | `docs/guides/run-family-pipeline.md` | refresh | Keep scenario guide; remove exhaustive flag tables and link to `reference/cli.md`. |
| `docs/guides/discovery-sweep.md` | `docs/guides/discovery-sweep.md` | refresh | Keep scenario guide for `discover-lowcode`; link to CLI/file contracts. |
| `docs/guides/add-or-update-family.md` | `docs/guides/add-or-update-family.md` | refresh | Keep workflow; link to canonical config/schema references. |
| `docs/guides/generate-and-validate-examples.md` | `docs/guides/generate-and-validate-examples.md` | refresh | Keep scenario guide; link to validation/reference pages for exhaustive details. |
| `docs/operations/monthly-maintenance.md` | `docs/operations/monthly-maintenance.md` | refresh | Include monthly/delta flow, `version-drift`, denominators, replay, and evidence checks. |
| `docs/operations/live-publishing.md` | `docs/operations/live-publishing.md` | merge | Canonical live PR runbook; merge unique content from `docs/publishing/agent-operated-live-pr-runbook.md`. |
| `docs/operations/readme-publishing.md` | `docs/operations/readme-publishing.md` | refresh | Keep canonical README publishing runbook; include render/publish/readme audit paths. |
| `docs/operations/post-merge-verification.md` | `docs/operations/post-merge-verification.md` | merge | Canonical post-merge runbook; merge unique content from `docs/publishing/post-merge-verification-runbook.md`. |
| `docs/operations/troubleshooting.md` | `docs/operations/troubleshooting.md` | refresh | Central troubleshooting page for LLM, NuGet, GitHub, dotnet, reviewer, evidence issues. |
| `docs/operations/telemetry.md` | `docs/operations/telemetry.md` | refresh | Keep as runbook for operating metrics; link to `reference/metrics.md` for schema/config. |
| `docs/architecture/decisions.md` | `docs/architecture/decisions.md` | keep | Active decision summary remains canonical. |
| `docs/architecture/pipeline-stages.md` | `docs/architecture/pipeline-stages.md` | refresh | Align with `STAGE_DEFINITIONS`, hard-stop stages, degraded stages. |
| `docs/architecture/system-design.md` | `docs/architecture/system-design.md` | refresh | Use component map from audit; keep design-level, not procedural. |
| `docs/development/contributing.md` | `docs/development/contributing.md` | refresh | Add docs root hygiene and canonical-reference rules. |
| `docs/development/repo-structure.md` | `docs/development/repo-structure.md` | refresh | Include `pipeline/contracts`, `pipeline/format-authority`, `_audit`, `_archive`. |
| `docs/development/taskcards.md` | `docs/development/taskcards.md` | refresh | Keep if it documents taskcard workflow and `sync-taskcard-docs`; otherwise merge into development/testing later. |
| `docs/development/testing.md` | `docs/development/testing.md` | refresh | Include test command, CI workflow, monthly workflow, and test-area map. |
| `docs/ci/environment-variables.md` | `docs/reference/environment-variables.md` | merge | Fold CI/env specifics into canonical env reference, then archive old CI page. |
| `docs/reference/cli.md` | `docs/reference/cli.md` | refresh | Make exhaustive and current from `src/plugin_examples/__main__.py`. |
| `docs/reference/config.md` | `docs/reference/config.md` | refresh | Make exhaustive from family config model/schema and config files. |
| `docs/reference/environment-variables.md` | `docs/reference/environment-variables.md` | refresh | Canonical env reference; must reflect governance and code mismatches explicitly until code is fixed. |
| `docs/reference/file-contracts.md` | `docs/reference/file-contracts.md` | refresh | Canonical run-local/promoted/file evidence contract page. |
| `docs/reference/gates-and-verdicts.md` | `docs/reference/gates-and-verdicts.md` | refresh | Canonical gate/verdict behavior from runner/gates code. |
| `docs/reference/metrics.md` | `docs/reference/metrics.md` | refresh | Canonical metrics config/payload/ledger/evidence reference. |
| `docs/reference/publishing-and-github.md` | `docs/reference/publishing-and-github.md` | refresh | Canonical low-level publishing/GitHub behavior; runbooks link here. |
| `docs/reference/schemas-and-contracts.md` | `docs/reference/schemas-and-contracts.md` | refresh | Canonical schema/contract inventory and update rules. |
| `docs/reference/validation-and-reviewer.md` | `docs/reference/validation-and-reviewer.md` | merge | Canonical validation/reviewer reference; merge reviewer-specific facts from discovery doc. |
| `docs/discovery/example-reviewer-fixture-system.md` | `docs/reference/validation-and-reviewer.md` and `docs/reference/file-contracts.md` | split | Reviewer behavior belongs in validation reference; fixture/file contracts belong in file contracts. Archive original after split. |
| `docs/discovery/open-taskcard-closure-matrix.md` | `docs/development/open-taskcard-closure-matrix.md` with workflow documented in `docs/development/taskcards.md` | move | Resolved during execution: this is a generated current taskcard view. The source JSON remains `workspace/verification/latest/open-taskcard-closure-matrix.json`; generation code now targets `docs/development/`. |
| `docs/publishing/agent-operated-live-pr-runbook.md` | `docs/operations/live-publishing.md` | merge | Duplicate live publishing runbook; archive original after unique content is merged. |
| `docs/publishing/post-merge-verification-runbook.md` | `docs/operations/post-merge-verification.md` | merge | Duplicate post-merge runbook; archive original after unique content is merged. |
| `docs/_audit/system_audit.md` | `docs/_audit/system_audit.md` | keep | Audit artifact. |
| `docs/_audit/docs_inventory.md` | `docs/_audit/docs_inventory.md` | keep | Audit artifact. |
| `docs/_audit/traceability.md` | `docs/_audit/traceability.md` | keep | Audit artifact. |
| `docs/_audit/root_orphans.md` | `docs/_audit/root_orphans.md` | keep | Audit artifact. |
| `docs/_audit/README_IA_PROPOSAL.md` | `docs/_audit/README_IA_PROPOSAL.md` | keep | Current IA proposal artifact. |
| `docs/_audit/docs_migration_plan.md` | `docs/_audit/docs_migration_plan.md` | keep | Current migration plan artifact. |
| `docs/_audit/style_guide.md` | `docs/_audit/style_guide.md` | keep | Current docs style rules artifact. |
| `docs/_archive/README.md` | `docs/_archive/README.md` | keep | Archive index. |
| `docs/_archive/discovery/*.md` | `docs/_archive/discovery/*.md` | archive | Historical discovery/preflight reports; not canonical. |
| `docs/_archive/merged/*.md` | `docs/_archive/merged/*.md` | archive | Already merged/historical duplicates. |
| `docs/_archive/plans/*.md` | `docs/_archive/plans/*.md` | archive | Historical plans; active decisions are in `architecture/decisions.md`. |
| `docs/_archive/publishing/*.md` | `docs/_archive/publishing/*.md` | archive | Historical publishing evidence/reviews. |
| `docs/_archive/root-orphans/*.md` | `docs/_archive/root-orphans/*.md` | archive | Previously triaged root orphans. |
| `plans/` | `docs/_archive/plans/` | decision needed | If historical, archive under docs archive; if active project management data, keep outside docs but remove from docs navigation. Criteria: owner confirms current use. |
| `reports/` | `reports/` | keep outside docs | Treat as generated/historical evidence output, not canonical docs. Link only from audit/archive indexes if needed. |
| `pipeline/format-authority/README.md` | `pipeline/format-authority/README.md` plus link from `docs/reference/schemas-and-contracts.md` | keep and link | Local README may remain near data; canonical docs should summarize and link rather than duplicate. |

## Canonical Merge Targets

| Duplicate/scattered area | Canonical target | Sources to merge/archive |
|---|---|---|
| Live PR publishing | `docs/operations/live-publishing.md` for runbook, `docs/reference/publishing-and-github.md` for exhaustive behavior | `docs/publishing/agent-operated-live-pr-runbook.md`, existing live publishing page |
| Post-merge verification | `docs/operations/post-merge-verification.md` for runbook, `docs/reference/publishing-and-github.md` for low-level checks | `docs/publishing/post-merge-verification-runbook.md`, existing post-merge page |
| Environment variables | `docs/reference/environment-variables.md` | `docs/ci/environment-variables.md`, env sections copied in guides/runbooks |
| Metrics | `docs/reference/metrics.md` for reference, `docs/operations/telemetry.md` for operations | Any metrics tables in CLI/guides/runbooks |
| Validation/reviewer | `docs/reference/validation-and-reviewer.md` | `docs/discovery/example-reviewer-fixture-system.md`, guide-level validation sections |
| File/evidence contracts | `docs/reference/file-contracts.md` | Path tables repeated in guides/runbooks |
| CLI | `docs/reference/cli.md` | Command/flag lists repeated in guides/runbooks |
| Config/schema/contracts | `docs/reference/config.md`, `docs/reference/schemas-and-contracts.md` | Config tables repeated in add-family guide |

## ROOT ORPHANS Mapping

Source: `docs/_audit/root_orphans.md`.

The root-orphan sweep found no direct files under `docs/` besides `docs/README.md`.

| orphan_path | new_path or merge target | action | rationale |
|---|---|---|---|
| `None` | N/A | no action | The audit row explicitly records that no root orphans exist. Root hygiene currently passes. |

P0 decision-needed check: none. There are no unmapped root orphan paths.

Future rule: if a real orphan appears, it must be mapped in this section with one of:

- `move` to an allowed folder.
- `merge` into a canonical page.
- `archive` under `docs/_archive/`.
- `delete` only if content is generated/transient and no unique information is retained.
- `Decision Needed` only with exact missing criteria and owner.

## Migration Order

1. Refresh canonical references first: CLI, config, env vars, file contracts, gates, validation/reviewer, publishing/GitHub, metrics, schemas/contracts.
2. Refresh guides and runbooks to link to references instead of repeating tables.
3. Merge duplicated publishing/post-merge docs.
4. Split and archive discovery/reviewer fixture doc after unique content is moved.
5. Update `docs/README.md` navigation.
6. Update archive index notes.
7. Run a root sweep and verify `docs/` contains only `README.md` plus folders.

## Top 15 Pages We Must End Up With

| Title | Target path |
|---|---|
| Documentation Home | `docs/README.md` |
| Product Overview | `docs/overview/product.md` |
| Core Concepts | `docs/overview/concepts.md` |
| Operator Quickstart | `docs/getting-started/operator-quickstart.md` |
| Contributor Quickstart | `docs/getting-started/contributor-quickstart.md` |
| Run a Family Pipeline | `docs/guides/run-family-pipeline.md` |
| Add or Update a Family | `docs/guides/add-or-update-family.md` |
| CLI Reference | `docs/reference/cli.md` |
| Configuration Reference | `docs/reference/config.md` |
| Environment Variables | `docs/reference/environment-variables.md` |
| File and Evidence Contracts | `docs/reference/file-contracts.md` |
| Gates and Verdicts | `docs/reference/gates-and-verdicts.md` |
| Validation and Reviewer Reference | `docs/reference/validation-and-reviewer.md` |
| Publishing and GitHub Reference | `docs/reference/publishing-and-github.md` |
| Live Publishing Runbook | `docs/operations/live-publishing.md` |
