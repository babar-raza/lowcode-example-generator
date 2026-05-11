# Documentation

This is the documentation home for the Aspose .NET Plugin Example Generation Pipeline.

The codebase is the source of truth. Canonical reference pages in `docs/reference/` are derived from `src/plugin_examples/`, `pipeline/schemas/`, `pipeline/configs/`, `.github/workflows/`, and the system audit.

## Start Here

| Persona | Start page | Common tasks |
|---|---|---|
| User | [Product Overview](overview/product.md) | Understand what the pipeline does and what it does not do. |
| Operator | [Operator Quickstart](getting-started/operator-quickstart.md) | Run a family, inspect evidence, publish PRs, perform monthly maintenance. |
| Contributor | [Contributor Quickstart](getting-started/contributor-quickstart.md) | Change code, configs, schemas, tests, or docs. |

## Scenario Guides

- [Run a Family Pipeline](guides/run-family-pipeline.md)
- [Run a Discovery Sweep](guides/discovery-sweep.md)
- [Add or Update a Family](guides/add-or-update-family.md)
- [Generate and Validate Examples](guides/generate-and-validate-examples.md)

## Operations

- [Monthly Maintenance](operations/monthly-maintenance.md)
- [Live Publishing](operations/live-publishing.md)
- [README Publishing](operations/readme-publishing.md)
- [Post-Merge Verification](operations/post-merge-verification.md)
- [Troubleshooting](operations/troubleshooting.md)
- [Telemetry](operations/telemetry.md)

## Canonical References

- [CLI Reference](reference/cli.md)
- [Configuration Reference](reference/config.md)
- [Environment Variables](reference/environment-variables.md)
- [File Contracts](reference/file-contracts.md)
- [Gates and Verdicts](reference/gates-and-verdicts.md)
- [Validation and Reviewer](reference/validation-and-reviewer.md)
- [Publishing and GitHub](reference/publishing-and-github.md)
- [Metrics](reference/metrics.md)
- [Schemas and Contracts](reference/schemas-and-contracts.md)

## Architecture and Development

- [System Design](architecture/system-design.md)
- [Pipeline Stages](architecture/pipeline-stages.md)
- [Architecture Decisions](architecture/decisions.md)
- [Contributing](development/contributing.md)
- [Testing and CI](development/testing.md)
- [Repository Structure](development/repo-structure.md)
- [Taskcards](development/taskcards.md)

## Archive

Historical preflight reviews, dated reports, old plans, and merged source docs live under [`_archive/`](_archive/). Archived docs are not canonical instructions and may be stale.

## Root Hygiene

Do not add markdown files directly under `docs/` except this `README.md`. New docs must go in the appropriate folder above, or in `_audit/` / `_archive/` for audit and historical material.
