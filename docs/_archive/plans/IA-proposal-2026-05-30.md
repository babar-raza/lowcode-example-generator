# Documentation IA Proposal

Source inputs:

- `docs/_audit/system_audit.md`
- `docs/_audit/docs_inventory.md`
- `docs/_audit/traceability.md`
- `docs/_audit/root_orphans.md`

Design goal: fewer, stronger documents with centralized references and scenario guides that link to references instead of repeating long tables.

## Proposed Tree

```text
docs/
  README.md
  overview/
    product.md
    concepts.md
  getting-started/
    operator-quickstart.md
    contributor-quickstart.md
  guides/
    run-family-pipeline.md
    discovery-sweep.md
    add-or-update-family.md
    generate-and-validate-examples.md
  reference/
    cli.md
    config.md
    environment-variables.md
    file-contracts.md
    gates-and-verdicts.md
    validation-and-reviewer.md
    publishing-and-github.md
    metrics.md
    schemas-and-contracts.md
  architecture/
    decisions.md
    system-design.md
    pipeline-stages.md
  operations/
    monthly-maintenance.md
    live-publishing.md
    readme-publishing.md
    post-merge-verification.md
    telemetry.md
    troubleshooting.md
  development/
    contributing.md
    testing.md
    repo-structure.md
    taskcards.md
  _audit/
    system_audit.md
    docs_inventory.md
    traceability.md
    root_orphans.md
    README_IA_PROPOSAL.md
    docs_migration_plan.md
    style_guide.md
  _archive/
    README.md
    ...
```

## Navigation Model

`docs/README.md` is the only navigation front door. It should expose:

- Start paths by persona.
- Task paths by scenario.
- Canonical reference pages.
- Architecture/development links.
- Archive warning: archived docs are historical evidence, not current procedure.

## Personas

| Persona | Needs | Primary docs |
|---|---|---|
| User | Understand what this system does, what it produces, and what it does not contain | `overview/product.md`, `overview/concepts.md` |
| Operator | Run families, inspect evidence, publish PRs, troubleshoot, maintain monthly/delta runs | `getting-started/operator-quickstart.md`, `guides/run-family-pipeline.md`, `operations/*`, `reference/cli.md`, `reference/file-contracts.md` |
| Contributor | Change code, configs, schemas, tests, docs, or pipeline behavior safely | `getting-started/contributor-quickstart.md`, `development/*`, `architecture/*`, `reference/config.md`, `reference/schemas-and-contracts.md` |

## Category Rules

### `overview/`

Use for stable conceptual pages:

- What the pipeline is.
- What it is not.
- Main concepts: family, scenario, contract, catalog, gate, evidence, publish package.

Do not put CLI flags, full config tables, or runbook steps here. Link to references and guides.

### `getting-started/`

Use for shortest successful path by persona:

- Operator quickstart: run one family, find evidence, know what pass/fail means.
- Contributor quickstart: setup, tests, code map, where to read decisions.

Do not duplicate full CLI/config/env tables. Link to `reference/cli.md`, `reference/config.md`, and `reference/environment-variables.md`.

### `guides/`

Use for scenario-driven, step-by-step tasks:

- Run a family pipeline.
- Run discovery.
- Add or update a family.
- Generate and validate examples.

Guides should include only the flags needed for the scenario. For exhaustive flags, link to `reference/cli.md`.

### `reference/`

Use for canonical, exhaustive material:

- CLI commands, flags, defaults.
- Config keys, defaults, schema boundaries.
- Environment variables.
- File/evidence contracts.
- Gates/verdicts.
- Validation and reviewer behavior.
- Publishing/GitHub behavior.
- Metrics.
- Schemas/contracts.

References are the single source for long tables. Guides and runbooks link here instead of copying.

### `architecture/`

Use for design and durable technical decisions:

- System design.
- Pipeline stage architecture.
- Architecture decisions.

Architecture pages should explain why the system is shaped this way. They should not become operational runbooks.

### `operations/`

Use for operator runbooks:

- Monthly maintenance.
- Live publishing.
- README publishing.
- Post-merge verification.
- Telemetry operations.
- Troubleshooting.

Runbooks may include commands, but only the path-specific commands needed to complete the procedure. Link to reference pages for exhaustive CLI/env/config material.

### `development/`

Use for contributor workflows:

- Contributing rules.
- Testing and CI.
- Repository structure.
- Taskcards.

Development docs should point to code-owned references where possible.

### `_audit/`

Use only for audit outputs and planning artifacts:

- System audit.
- Docs inventory.
- Traceability.
- Root orphan sweep.
- IA proposal.
- Migration plan.
- Style guide.

Do not treat `_audit/` as user/operator documentation.

### `_archive/`

Use for historical docs, old plans, previous reviews, sprint evidence summaries, and duplicate docs after consolidation.

Archived docs must not be linked as canonical procedure from `docs/README.md`, except from an archive index with clear historical labeling.

## Where Does This Go?

| Content type | Destination | Rule |
|---|---|---|
| “What is this?” | `overview/` | Explain concepts, no exhaustive tables. |
| “I am new, what do I run first?” | `getting-started/` | Short path only. |
| “How do I complete this task?” | `guides/` or `operations/` | Use `guides/` for normal scenarios, `operations/` for runbooks with checks/rollback/troubleshooting. |
| “What flags exist?” | `reference/cli.md` | Exhaustive CLI source of truth. |
| “What config keys exist?” | `reference/config.md` | Exhaustive config source of truth. |
| “What files are read/written?” | `reference/file-contracts.md` | Exhaustive file/evidence contracts. |
| “What does this gate/verdict mean?” | `reference/gates-and-verdicts.md` | Centralize gate semantics. |
| “Why is the system designed this way?” | `architecture/` | Design and decisions. |
| “How do I test/change the repo?” | `development/` | Contributor workflow. |
| “This was true for sprint N” | `_archive/` | Historical only. |
| “This is an audit/planning artifact” | `_audit/` | Not canonical runtime docs. |

## Docs Root Allowed Items

The `docs/` root may contain:

- `docs/README.md`
- Folders listed in the proposed tree
- Meta folders: `docs/_audit/`, `docs/_archive/`

The `docs/` root must not contain any other files. Any new direct file under `docs/` is a ROOT ORPHAN and must be moved, merged, archived, or deleted in the same change that creates it.

## Deduplication Principles

1. One canonical page per reference surface.
2. Guides link to references for full tables.
3. Runbooks link to references for full flag/env/config detail.
4. Archive old duplicate pages after their unique content is merged.
5. Keep generated/historical evidence out of canonical docs navigation.

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
