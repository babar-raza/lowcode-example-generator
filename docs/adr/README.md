# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the LowCode Example Generator pipeline.

ADRs document significant technical and governance decisions: the context that prompted them, the options considered, the decision made, and the consequences.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](ADR-001-nuget-as-source-of-truth.md) | NuGet Package as Primary API Source of Truth | Accepted | 2026-06-01 |
| [ADR-002](ADR-002-gate-isolation-determinism.md) | Gate Isolation — No AI/LLM Imports in Gate Modules | Accepted | 2026-06-01 |
| [ADR-003](ADR-003-evidence-first-pipeline.md) | Evidence-First Pipeline Architecture | Accepted | 2026-06-01 |
| [ADR-004](ADR-004-approval-token-model.md) | Dual Approval Token Model for Live Operations | Accepted | 2026-06-04 |
| [ADR-005](ADR-005-evidence-protocol-v3.md) | Evidence Authority Protocol v3 | Accepted | 2026-06-10 |
| [ADR-006](ADR-006-non-lowcode-fallback-strategy.md) | Non-LowCode Fallback Strategy | Accepted | 2026-06-13 |
| [ADR-007](ADR-007-wave-based-versioning.md) | Wave-Based Versioning | Accepted | 2026-06-14 |
| [ADR-008](ADR-008-pip-audit-advisory-policy.md) | pip-audit Advisory-Only Policy | Accepted | 2026-06-16 |
| [ADR-009](ADR-009-documentation-governance.md) | Documentation Governance — Docs-as-Code Synchronization Policy | Accepted | 2026-06-17 |

## Format

Each ADR follows the [MADR](https://adr.github.io/madr/) lightweight format:

```
# Title
Status, Date
## Context
## Decision
## Consequences
## Alternatives Considered
```

## Adding a New ADR

1. Copy any existing ADR as a template.
2. Number sequentially: `ADR-NNN-short-title.md`.
3. Set status to `Proposed` until reviewed; change to `Accepted` or `Rejected` after review.
4. Add a row to the index table above.
5. Reference the ADR in `docs/architecture/decisions.md`.
