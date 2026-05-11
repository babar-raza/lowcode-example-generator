# Core Concepts

Audience: User, Operator, Contributor

## Family

A family is an Aspose product configuration such as `cells`, `words`, or `pdf`. Family YAML files live under `pipeline/configs/families/` and are validated by `pipeline/schemas/family-config.schema.json`.

## Source-of-Truth Proof

The pipeline writes source-of-truth evidence after NuGet fetch, extraction, reflection, and plugin namespace detection. Generation must not proceed unless the reflected catalog proves eligible plugin namespaces.

## Scenario

A scenario is a planned example target derived from reflected API types and methods. Scenario planning classifies types, scores entry points, handles fixture strategy, and preserves blocked scenarios.

## Evidence

Every run writes structured evidence under `workspace/runs/{run_id}/evidence/latest/`. Promoted family evidence goes under `workspace/verification/latest/families/{family}/`.

## Gates

Gates turn stage and per-example results into verdicts such as `PR_READY`, `PARTIAL_PR_READY`, or `BLOCKED_BUILD_FAILED`.

## Publishing

Publishing is PR-based. Live publishing requires `GITHUB_TOKEN`, a publishable gate verdict, repo access/permission readiness, and an explicit approval token. Merge uses a separate approval token.

See:

- [File Contracts](../reference/file-contracts.md)
- [Gates and Verdicts](../reference/gates-and-verdicts.md)
- [Publishing and GitHub](../reference/publishing-and-github.md)
