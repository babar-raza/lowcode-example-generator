# Documentation Style Guide

Purpose: keep documentation clear, code-aligned, and non-duplicative.

This is a planning artifact under `_audit/`. It should be promoted into contributor docs only after the IA migration is accepted.

## Core Rules

1. Code is the source of truth for behavior.
2. References are canonical and exhaustive.
3. Guides and runbooks link to reference pages instead of copying long tables.
4. Archived docs are historical evidence, not current instructions.
5. Every factual claim about commands, flags, config keys, env vars, file paths, gates, or outputs should cite the owning code path or canonical reference.
6. Do not create new direct files under `docs/` except `docs/README.md`.

## Root Hygiene Rule

Allowed under `docs/` root:

- `README.md`
- Folders only, including `_audit/` and `_archive/`

Not allowed:

- `docs/*.md` files other than `docs/README.md`
- Temporary planning files under `docs/`
- One-off reports under `docs/`

If a root file is accidentally created, triage it immediately:

- Move to the correct folder.
- Merge into a canonical page.
- Archive under `_archive/`.
- Delete only if transient/generated and no unique content is needed.

## Duplication Prevention

### Do

- Link to `reference/cli.md` for full command and flag lists.
- Link to `reference/config.md` for config keys/defaults.
- Link to `reference/environment-variables.md` for env var details.
- Link to `reference/file-contracts.md` for input/output/evidence paths.
- Link to `reference/gates-and-verdicts.md` for gate semantics.
- Link to `reference/validation-and-reviewer.md` for validation and reviewer details.
- Link to `reference/publishing-and-github.md` for approval, token, repo, and PR behavior.
- Link to `reference/metrics.md` for metrics config/payload/ledger details.

### Do Not

- Copy full CLI tables into guides.
- Copy full config tables into quickstarts.
- Copy env var tables into runbooks.
- Copy gate/verdict tables into scenario guides.
- Treat archived sprint reports as current procedure.
- Create a new page when an existing canonical page can absorb the content.

## Status Labels

Use these labels when auditing or refreshing docs:

- `Current`: checked against code in the same change.
- `Partial`: useful but missing code surfaces.
- `Blocked`: cannot be made current because code behavior is unclear or conflicting.
- `Historical`: retained for archive/evidence only.

## Guide Template

```markdown
# Guide Title

Audience: Operator | Contributor
Scenario: One sentence describing the task.
Canonical references: [CLI](../reference/cli.md), [File Contracts](../reference/file-contracts.md)

## Before You Start

- Required repo state.
- Required credentials or env vars, with links to references.
- Required prior evidence or artifacts.

## Steps

1. Do the first action.
2. Inspect the expected evidence.
3. Continue or stop based on the stated condition.

## Expected Result

- Files written.
- Verdict/status expected.
- Where to inspect details.

## Troubleshooting

Link to `../operations/troubleshooting.md` and mention only scenario-specific symptoms.
```

Guide rules:

- Keep steps scenario-specific.
- Include only the exact commands needed.
- Link to references for exhaustive flags/config/env paths.
- Do not include long schema or evidence tables.

## Reference Template

```markdown
# Reference Title

Audience: Operator, Contributor
Source of truth: `path/to/code.py`, `path/to/schema.json`
Last verified: YYYY-MM-DD

## Scope

What this reference owns.

## Canonical Table

| Item | Meaning | Default/required | Source |
|---|---|---|---|
| `name` | Description | Default | `code:path` |

## Related Guides

- [Guide](../guides/example.md)

## Change Checklist

- Update this page when the owning code/schema changes.
- Update related guides only if scenario steps changed.
```

Reference rules:

- Be exhaustive for the owned surface.
- Prefer tables.
- Include code/schema source paths.
- Do not include step-by-step operator runbooks unless they clarify a reference behavior.

## Runbook Template

```markdown
# Runbook Title

Audience: Operator
Purpose: Operational outcome.
Canonical references: [CLI](../reference/cli.md), [Environment Variables](../reference/environment-variables.md)

## Preconditions

- Required credentials.
- Required evidence.
- Required branch/repo state.

## Procedure

1. Run the command.
2. Check the evidence.
3. Stop or continue based on explicit criteria.

## Stop Conditions

- Condition that blocks continuing.
- Evidence to record.

## Recovery

- How to retry safely.
- What must not be retried.

## Evidence

- Paths written/read.
- Links to file contracts for complete details.
```

Runbook rules:

- Include decision points and stop conditions.
- Keep full env var and CLI details in reference pages.
- Always state whether a command performs remote mutation or dry-run simulation.

## Architecture Note Template

```markdown
# Architecture Note Title

Audience: Contributor
Status: Proposed | Accepted | Superseded
Related decisions: [decisions.md](decisions.md)

## Context

What problem or constraint exists.

## Decision

What design is selected.

## Consequences

- Positive consequence.
- Tradeoff or maintenance cost.

## Code Pointers

- `src/path.py`
- `pipeline/schema.json`

## Operational Impact

What operators need to know, with links to runbooks or references.
```

Architecture rules:

- Explain why, not just how.
- Link to code and references.
- Do not duplicate operational procedures.

## Link Policy

Use relative links between docs pages. Prefer canonical links:

- Guide to CLI: `../reference/cli.md`
- Guide to config: `../reference/config.md`
- Guide to evidence: `../reference/file-contracts.md`
- Runbook to env vars: `../reference/environment-variables.md`
- Architecture to decisions: `decisions.md`

## Archive Policy

Archive when:

- A doc is superseded by a canonical page.
- A doc describes a historical sprint/review/preflight.
- A doc is a duplicate after unique content is merged.

Archived docs should include or inherit an archive note saying they are historical and not current procedure.

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
