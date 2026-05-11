# Documentation Style Guide

Status: design-only guidance for the future docs migration.

## Core Rules

1. Code and schemas are the source of truth for technical claims.
2. Guides explain how to complete a scenario; references define all options and contracts.
3. Do not duplicate config tables, CLI flag tables, evidence file lists, or verdict matrices across docs.
4. Link to canonical reference pages instead of copying reference material into guides.
5. Archive historical reports instead of rewriting them as current instructions.
6. Every page must name its audience and scope near the top.

## Root Hygiene Rule

Never create new files directly under `docs/` except `docs/README.md`.

Allowed:

- `docs/README.md`
- Files under approved top-level folders such as `docs/guides/`, `docs/reference/`, `docs/operations/`, `docs/development/`, `docs/architecture/`, `docs/overview/`, `docs/getting-started/`
- Meta content under `docs/_audit/` and `docs/_archive/`

Not allowed:

- `docs/monthly-runbook.md`
- `docs/verifier-integration.md`
- Any new ad hoc root-level markdown file

## Guide Template

```markdown
# Guide Title

Audience: Operator | Contributor | User
Scenario: One concrete task this guide completes
Canonical references: [CLI](../reference/cli.md), [Config](../reference/configuration.md)

## When To Use This

Use this guide when...

## Prerequisites

- Required local tools
- Required credentials
- Required existing evidence or config

## Steps

1. Do the first action.
2. Run the command.
3. Verify the output.

## Expected Evidence

- `workspace/...`
- Link to [Evidence and File Contracts](../reference/evidence-and-file-contracts.md)

## Troubleshooting

Short pointers only. Link to [Troubleshooting](../operations/troubleshooting.md) for expanded handling.
```

Guide rules:

- Include only the flags needed for the scenario.
- Link to `reference/cli.md` for full flag lists.
- Link to `reference/configuration.md` for config key details.
- Link to `reference/evidence-and-file-contracts.md` for output file contracts.
- Do not include historical sprint result details.

## Reference Template

```markdown
# Reference Title

Audience: Operator | Contributor
Source of truth: code/schema paths this page is generated or refreshed from
Last verified: YYYY-MM-DD

## Scope

This reference defines...

## Canonical Tables

| Name | Type | Default | Required | Source | Notes |
|---|---|---|---|---|---|

## Behavior

Precise rules and edge cases.

## Related Guides

- [Guide](../guides/example.md)
```

Reference rules:

- Be exhaustive.
- Cite code/schema paths for every table.
- Be the only place that owns a command/config/evidence/verdict table.
- If a guide needs the same material, link to the reference instead.

## Runbook Template

```markdown
# Runbook Title

Audience: Operator
Frequency: ad hoc | monthly | release | incident
Canonical references: [CLI](../reference/cli.md), [Evidence](../reference/evidence-and-file-contracts.md)

## Purpose

What this runbook operates.

## Required Access

- Tokens
- Repo permissions
- External services

## Procedure

1. Preflight.
2. Execute.
3. Validate.
4. Record evidence.

## Rollback or Stop Conditions

- Stop if...
- Do not proceed if...

## Evidence Checklist

- Required files
- Expected verdicts

## Troubleshooting

Common failures and links.
```

Runbook rules:

- State stop conditions clearly.
- Never repeat full CLI/config reference.
- Include evidence checklist with links to canonical file contracts.
- Keep historical run reports out of runbooks.

## Architecture Note Template

```markdown
# Architecture Note Title

Audience: Contributor
Status: proposed | accepted | superseded
Date: YYYY-MM-DD
Code evidence: `src/...`, `pipeline/...`

## Context

What problem or design area this note covers.

## Current Design

Components, data flow, boundaries.

## Decisions

- Decision 1 and rationale.
- Decision 2 and rationale.

## Consequences

Operational and development implications.

## Related References

- [Configuration](../reference/configuration.md)
- [Evidence](../reference/evidence-and-file-contracts.md)
```

Architecture rules:

- Describe stable design, not step-by-step operation.
- Keep historical plans in `_archive/` unless they are still active decisions.
- Link to references for precise schemas, flags, and file contracts.

## Anti-Duplication Rules

- One CLI table only: `docs/reference/cli.md`.
- One config/env reference only: `docs/reference/configuration.md` and `docs/reference/environment-variables.md`.
- One evidence contract only: `docs/reference/evidence-and-file-contracts.md`.
- One gate/verdict matrix only: `docs/reference/gates-and-verdicts.md`.
- One validation/reviewer reference only: `docs/reference/validation-and-reviewer.md`.
- One live publishing runbook only: `docs/operations/live-publishing.md`.
- One monthly runbook only: `docs/operations/monthly-maintenance.md`.

When adding or changing a guide, ask:

- Does this repeat a canonical table?
- Can this be a short scenario plus a link?
- Is this historical evidence that belongs in `_archive/`?
- Is this file being created directly under `docs/`? If yes, stop unless it is `docs/README.md`.
