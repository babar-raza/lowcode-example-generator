# Documentation

This is the documentation home for the Aspose .NET Plugin Example Generation Pipeline.

Code and schemas are the source of truth. Reference pages in `docs/reference/` are the canonical documentation for commands, config keys, environment variables, file contracts, gates, validation, publishing, metrics, and schemas.

## Start By Persona

| Persona | Start here | Common work |
|---|---|---|
| User | [Product Overview](overview/product.md) | Understand what the pipeline does and what it does not publish directly. |
| Operator | [Operator Quickstart](getting-started/operator-quickstart.md) | Run families, inspect evidence, publish PRs, verify releases. |
| Contributor | [Contributor Quickstart](getting-started/contributor-quickstart.md) | Change code, configs, schemas, tests, or docs. |

## Common Scenarios

| Scenario | Guide or runbook | Canonical references |
|---|---|---|
| Run a family pipeline | [Run a Family Pipeline](guides/run-family-pipeline.md) | [CLI](reference/cli.md), [File Contracts](reference/file-contracts.md), [Gates and Verdicts](reference/gates-and-verdicts.md) |
| Run source-of-truth discovery | [Discovery Sweep](guides/discovery-sweep.md) | [CLI](reference/cli.md), [File Contracts](reference/file-contracts.md) |
| Add or update a family | [Add or Update a Family](guides/add-or-update-family.md) | [Config](reference/config.md), [Schemas and Contracts](reference/schemas-and-contracts.md) |
| Generate and validate examples | [Generate and Validate Examples](guides/generate-and-validate-examples.md) | [Validation and Reviewer](reference/validation-and-reviewer.md), [File Contracts](reference/file-contracts.md) |
| Publish live PRs | [Live Publishing](operations/live-publishing.md) | [Publishing and GitHub](reference/publishing-and-github.md), [Environment Variables](reference/environment-variables.md) |
| Publish README updates | [README Publishing](operations/readme-publishing.md) | [Publishing and GitHub](reference/publishing-and-github.md), [File Contracts](reference/file-contracts.md) |
| Verify after merge | [Post-Merge Verification](operations/post-merge-verification.md) | [Publishing and GitHub](reference/publishing-and-github.md), [File Contracts](reference/file-contracts.md) |
| Monthly maintenance | [Monthly Maintenance](operations/monthly-maintenance.md) | [CLI](reference/cli.md), [Config](reference/config.md), [File Contracts](reference/file-contracts.md) |
| Troubleshoot a run | [Troubleshooting](operations/troubleshooting.md) | [CLI](reference/cli.md), [Gates and Verdicts](reference/gates-and-verdicts.md) |

## Canonical References

- [CLI Reference](reference/cli.md)
- [Configuration Reference](reference/config.md)
- [Environment Variables](reference/environment-variables.md)
- [File and Evidence Contracts](reference/file-contracts.md)
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

## Archive and Audits

- [Audit Artifacts](_audit/)
- [Archive](_archive/)

Archived docs are historical evidence, not current operating procedure.

## Docs Root Hygiene

Do not add files directly under `docs/` except this `README.md`. New docs must go in one of the folders above, or in `_audit/` / `_archive/` for audit and historical material.
