# Documentation Inventory

Audit mode: docs are inventory input only. Accuracy status is based on comparison against code surfaces found during this audit.

Last refreshed: 2026-05-26.

Root sweep result: no ROOT ORPHAN files. `docs/README.md` is the only direct file under `docs/`.

Status legend:

- Accurate: no material drift found in this audit.
- Partial: useful, but missing some current code surfaces or detail.
- Outdated: conflicts with current code or omits major behavior.
- Duplicate: overlaps substantially with another active doc.
- Unknown: not deeply verified against code in this pass.

| path | intended audience | purpose | status | action | notes |
|---|---|---|---|---|---|
| `README.md` | Operator, contributor | Repo overview and entry to docs | Accurate | Keep | Points to docs home and key workflows. |
| `AGENTS.md` | Agent, contributor | Governance/rules | Partial | Keep | LLM endpoint governance is stricter than current router code. |
| `docs/README.md` | All | Docs landing page by persona/scenario | Accurate | Keep | Root hygiene rule is present. |
| `docs/overview/product.md` | User, operator | Product overview | Partial | Keep | Should remain concept-level and link to references. |
| `docs/overview/concepts.md` | User, contributor | Concepts | Partial | Keep | Useful conceptual map; avoid reference-table duplication. |
| `docs/getting-started/operator-quickstart.md` | Operator | Short operator path | Partial | Keep | Should link to current CLI/env/file references. |
| `docs/getting-started/contributor-quickstart.md` | Contributor | Short contributor path | Partial | Keep | Should link to testing, decisions, config/schema references. |
| `docs/guides/run-family-pipeline.md` | Operator | Run one family pipeline | Accurate | Keep | Scenario guide now links to references. |
| `docs/guides/discovery-sweep.md` | Operator, contributor | Run discovery sweep | Partial | Keep | Needs periodic check against discovery CLI behavior. |
| `docs/guides/add-or-update-family.md` | Contributor | Family config workflow | Partial | Keep | Link to config/schema references; do not duplicate key tables. |
| `docs/guides/generate-and-validate-examples.md` | Operator, contributor | Generation/validation workflow | Accurate | Keep | Notes governed LLM endpoint and validation references. |
| `docs/operations/monthly-maintenance.md` | Operator | Monthly/delta runbook | Partial | Keep | Should be checked against version-drift/replay command surfaces. |
| `docs/operations/live-publishing.md` | Operator | Live PR publishing runbook | Accurate | Keep | Canonical runbook after duplicate publishing docs were archived. |
| `docs/operations/readme-publishing.md` | Operator | README publishing | Partial | Keep | Should periodically verify `render-root-readme`/`publish-readme` flags. |
| `docs/operations/post-merge-verification.md` | Operator | Post-merge verification | Accurate | Keep | Canonical post-merge runbook after duplicate docs were archived. |
| `docs/operations/telemetry.md` | Operator | Metrics operations | Partial | Keep | Should link to metrics reference for exhaustive config. |
| `docs/operations/troubleshooting.md` | Operator | Troubleshooting | Partial | Keep | Should include LLM/router governance gap and common gate failures. |
| `docs/architecture/decisions.md` | Contributor | Active architecture decisions | Accurate | Keep | Required pre-implementation doc. |
| `docs/architecture/pipeline-stages.md` | Contributor, operator | Stage architecture | Partial | Keep | Must stay aligned with `STAGE_DEFINITIONS`. |
| `docs/architecture/system-design.md` | Contributor | System design | Partial | Keep | Should stay code-derived. |
| `docs/development/contributing.md` | Contributor | Contribution rules | Partial | Keep | Should include docs root hygiene and canonical-reference rules. |
| `docs/development/repo-structure.md` | Contributor | Repo layout | Partial | Keep | Should reflect active docs folders and `pipeline/` contracts. |
| `docs/development/taskcards.md` | Contributor, operator | Taskcard workflow | Accurate | Keep | Documents JSON source and generated markdown location. |
| `docs/development/open-taskcard-closure-matrix.md` | Contributor, operator | Generated taskcard matrix | Accurate | Keep generated | Generated from `workspace/verification/latest/open-taskcard-closure-matrix.json`; do not edit manually. |
| `docs/development/testing.md` | Contributor | Testing and CI | Partial | Keep | Test command exists; keep CI workflow references current. |
| `docs/reference/cli.md` | Operator, contributor | Canonical CLI reference | Accurate | Keep | Covers current commands/flags from `__main__.py`. |
| `docs/reference/config.md` | Operator, contributor | Canonical config reference | Accurate | Keep | Covers family config model/defaults and config files. |
| `docs/reference/environment-variables.md` | Operator, contributor | Canonical env var reference | Accurate | Keep | Correctly marks non-governed LLM fallbacks as code-visible but not approved. |
| `docs/reference/file-contracts.md` | Operator, contributor | Canonical file/evidence contracts | Accurate | Keep | Covers run-local, promoted, taskcard, and evidence paths. |
| `docs/reference/gates-and-verdicts.md` | Operator, contributor | Gate/verdict semantics | Partial | Keep | Should be periodically regenerated from gates code. |
| `docs/reference/validation-and-reviewer.md` | Operator, contributor | Validation/reviewer reference | Accurate | Keep | Includes semantic output types and reviewer boundary. |
| `docs/reference/publishing-and-github.md` | Operator, contributor | Publishing/GitHub reference | Accurate | Keep | Canonical publishing behavior and approval tokens. |
| `docs/reference/metrics.md` | Operator, contributor | Metrics reference | Partial | Keep | Should include ledger and command-session details. |
| `docs/reference/schemas-and-contracts.md` | Contributor | Schema/contract reference | Partial | Keep | Should include generated schema/contract inventory. |
| `docs/_audit/system_audit.md` | Future LLM, contributor | Code-derived audit | Accurate | Keep | Refreshed by this audit. |
| `docs/_audit/docs_inventory.md` | Future LLM, contributor | Docs inventory | Accurate | Keep | Refreshed by this audit. |
| `docs/_audit/traceability.md` | Future LLM, contributor | Feature-to-doc traceability | Accurate | Keep | Refreshed by this audit. |
| `docs/_audit/root_orphans.md` | Future LLM, contributor | Root hygiene audit | Accurate | Keep | No root orphans. |
| `docs/_audit/README_IA_PROPOSAL.md` | Contributor | IA proposal | Accurate | Keep | Planning artifact, not operator docs. |
| `docs/_audit/docs_migration_plan.md` | Contributor | Migration plan | Accurate | Keep | Planning artifact, reflects completed taskcard move. |
| `docs/_audit/style_guide.md` | Contributor | Docs style guide | Accurate | Keep | Planning artifact; can be promoted into contributing later. |
| `docs/_archive/README.md` | Contributor | Archive index | Accurate | Keep | Archive boundary. |
| `docs/_archive/discovery/*.md` | Historical reviewer | Historical discovery/preflight reports | Unknown | Archive | Not canonical. |
| `docs/_archive/merged/*.md` | Historical reviewer | Docs merged into active docs | Duplicate | Archive | Historical only. |
| `docs/_archive/plans/*.md` | Historical reviewer | Historical plans | Outdated | Archive | Active decisions live in `architecture/decisions.md`. |
| `docs/_archive/publishing/*.md` | Historical reviewer | Historical publishing evidence/reviews | Unknown | Archive | Not canonical. |
| `docs/_archive/root-orphans/*.md` | Contributor | Previously triaged root orphans | Accurate | Archive | Historical root-cleanup evidence. |
| `reports/docs_refactor.md` | Contributor, reviewer | Docs refactor execution report | Accurate | Keep in reports | Useful evidence of last docs reorg. |
| `reports/` | Reviewer/operator | Sprint/generated evidence | Unknown | Keep outside docs | Not canonical docs. |
| `plans/` | Contributor | Planning notes outside docs IA | Unknown | Review later | Decide whether historical plans should move under archive. |
| `pipeline/format-authority/README.md` | Contributor | Local README for format authority data | Partial | Keep and link | Local data README can remain near data; canonical docs should summarize. |

## Root Orphan Entries

No root orphan files were found. There are no direct `docs/*.md` files except `docs/README.md`.

## Top Documentation Problems

1. LLM governance remains a code/docs tension: docs correctly state the policy, while router code still exposes non-governed fallbacks.
2. Historical `_archive/` docs contain stale paths and old procedures; this is expected but can confuse search-driven readers.
3. Some active architecture/reference pages are Partial and should be regenerated from code periodically.
4. Metrics content is split between operations and reference; current split is acceptable but needs periodic consistency checks.
5. Schema/contract reference should be kept machine-inventory driven to avoid drift.
6. `plans/` remains outside the docs IA and needs ownership/retention decision.
7. `reports/` is large and doc-like; it should stay evidence-only and not become canonical docs.
8. The generated taskcard markdown is active docs but must not be manually edited.
9. Root hygiene currently passes, but it should remain a required postflight check.
10. The `check` CLI command remains a placeholder and should be documented as such until implemented or removed.
