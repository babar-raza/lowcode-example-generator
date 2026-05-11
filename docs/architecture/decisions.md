# Architecture Decisions

Audience: Contributor

This page is the active governance summary extracted from the historical execution plan and current code-derived audit. Historical plans are archived under `docs/_archive/plans/`.

## Active Decisions

1. The official NuGet package is the primary source of truth for API symbols.
2. DocFX markdown and existing example repos are supporting inputs only.
3. Generated examples must pass compiler, runtime, output, and reviewer gates before publishing.
4. Publishing is PR-based; no direct push to `main`.
5. Blocked scenarios must be preserved with explicit reasons.
6. Monthly runs must be delta-aware and avoid regenerating unchanged examples.
7. Live PR creation and live merge use separate approval tokens.
8. Evidence must be written even for partial failure.
9. Family-specific promoted evidence should use `workspace/verification/latest/families/{family}/`.

## Historical Source

The previous long-form execution plan was moved to `docs/_archive/plans/plugin-example-generation-execution-plan.md`. Treat it as historical unless a decision is restated on this page or in current code.
