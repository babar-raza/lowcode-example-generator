# Documentation IA Proposal

Status: design only. Do not move or edit existing docs as part of this proposal.

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
    add-or-update-family.md
    discovery-sweep.md
    generate-and-validate-examples.md
  reference/
    cli.md
    configuration.md
    environment-variables.md
    evidence-and-file-contracts.md
    gates-and-verdicts.md
    validation-and-reviewer.md
    publishing-and-github.md
    metrics.md
    schemas-and-contracts.md
  architecture/
    system-design.md
    pipeline-stages.md
    decisions.md
  operations/
    monthly-maintenance.md
    live-publishing.md
    readme-publishing.md
    post-merge-verification.md
    troubleshooting.md
    telemetry.md
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
    discovery/
    plans/
    publishing/
```

## Docs Root Allowed Items

`docs/` root may contain only:

- `docs/README.md`
- Meta folders: `docs/_audit/`, `docs/_archive/`
- The approved top-level IA folders listed above

No other markdown files may be created directly under `docs/`. Any future direct root file other than `README.md` is a ROOT ORPHAN and must be triaged before merge.

## Personas

### User

Definition: someone trying to understand what the system does and whether it fits their need.

Needs:

- Product purpose and boundaries.
- Core concepts: NuGet source of truth, reflected API catalog, scenarios, gates, evidence, PR-based publishing.
- A short path to the right operator or contributor quickstart.

Primary docs:

- `docs/README.md`
- `docs/overview/product.md`
- `docs/overview/concepts.md`

### Operator

Definition: someone running the pipeline, interpreting evidence, publishing PRs, or maintaining monthly runs.

Needs:

- Fast run commands.
- Required credentials and environment variables.
- Monthly workflow.
- Live PR and merge procedures.
- Evidence locations and gate interpretation.
- Troubleshooting and telemetry.

Primary docs:

- `docs/getting-started/operator-quickstart.md`
- `docs/operations/monthly-maintenance.md`
- `docs/operations/live-publishing.md`
- `docs/operations/post-merge-verification.md`
- `docs/operations/troubleshooting.md`
- References under `docs/reference/`

### Contributor

Definition: someone changing code, tests, schemas, family configs, or docs.

Needs:

- Repository layout.
- How to run tests and CI-equivalent checks.
- How to add/update family configs.
- How schemas/contracts fit together.
- Architecture and component responsibilities.
- Documentation rules.

Primary docs:

- `docs/getting-started/contributor-quickstart.md`
- `docs/development/contributing.md`
- `docs/development/testing.md`
- `docs/development/repo-structure.md`
- `docs/architecture/system-design.md`
- `docs/reference/configuration.md`
- `docs/reference/schemas-and-contracts.md`

## Where Does This Go?

### `overview/`

Use for stable conceptual explanation:

- What the pipeline is.
- What it does not do.
- Source-of-truth model.
- Definitions of common terms.

Do not put command tables, config key matrices, or runbook steps here. Link to references and guides.

### `getting-started/`

Use for short first-run paths by persona:

- Minimal setup.
- One happy-path command.
- How to verify success.
- Where to go next.

Do not duplicate exhaustive CLI flags or environment variable tables. Link to `reference/cli.md` and `reference/environment-variables.md`.

### `guides/`

Use for scenario-driven procedures that have a beginning and an end:

- Run one family pipeline.
- Add a new family config.
- Run a discovery sweep.
- Generate and validate examples.

Guides may show a small command snippet, but all option details must link to canonical reference pages.

### `reference/`

Use for exhaustive, canonical source-of-truth documentation:

- CLI commands and flags.
- Config keys and defaults.
- Environment variables.
- Evidence files and workspace contracts.
- Gate verdicts.
- Validation/reviewer behavior.
- Publishing and GitHub API requirements.
- Metrics config and payloads.
- Schemas and contracts.

References should be generated or refreshed from code/schemas whenever possible. Other docs must link here instead of copying tables.

### `architecture/`

Use for system design, component maps, data flow, and architecture decisions:

- End-to-end pipeline design.
- Stage ordering.
- Module responsibilities.
- Integration boundaries.
- Architecture decisions and constraints.

Do not store runbooks or historical sprint reports here.

### `operations/`

Use for recurring operational procedures:

- Monthly maintenance.
- Live publishing.
- README publishing.
- Post-merge verification.
- Troubleshooting.
- Telemetry/metrics operation.

Operations docs should be step-by-step and should link to reference pages for exhaustive command/config detail.

### `development/`

Use for contributor workflow:

- Repository structure.
- Local setup.
- Testing.
- CI-equivalent checks.
- Taskcard/doc generation.
- How to update docs without duplication.

### `_audit/`

Use only for audit outputs and planning artifacts. These are not end-user docs.

### `_archive/`

Use for historical, timestamped, duplicate, or superseded documents. Archived docs must not be linked as canonical instructions. `docs/_archive/README.md` should explain that archived files are historical and may be stale.

## Top 15 Pages We Must End Up With

1. Product Overview — `docs/overview/product.md`
2. Core Concepts — `docs/overview/concepts.md`
3. Operator Quickstart — `docs/getting-started/operator-quickstart.md`
4. Contributor Quickstart — `docs/getting-started/contributor-quickstart.md`
5. Run a Family Pipeline — `docs/guides/run-family-pipeline.md`
6. Add or Update a Family — `docs/guides/add-or-update-family.md`
7. CLI Reference — `docs/reference/cli.md`
8. Configuration Reference — `docs/reference/configuration.md`
9. Evidence and File Contracts — `docs/reference/evidence-and-file-contracts.md`
10. Gates and Verdicts — `docs/reference/gates-and-verdicts.md`
11. Validation and Reviewer Reference — `docs/reference/validation-and-reviewer.md`
12. System Design — `docs/architecture/system-design.md`
13. Monthly Maintenance Runbook — `docs/operations/monthly-maintenance.md`
14. Live Publishing Runbook — `docs/operations/live-publishing.md`
15. Testing and CI — `docs/development/testing.md`
