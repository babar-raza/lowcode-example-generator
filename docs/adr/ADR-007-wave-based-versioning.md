# ADR-007: Wave-Based Versioning and Sprint Model

**Status:** Accepted
**Date:** 2026-06-01
**Context:** The pipeline evolves through focused implementation sprints. Each sprint targets a specific capability improvement (e.g., new families, package repair, evidence protocol fixes). Tracking changes required a model that maps cleanly to both semver releases and auditable sprint evidence.

## Decision

Use **wave-based versioning** where each sprint increments the minor version.

- Version format: `0.WAVE.PATCH` (e.g., `0.31.0` = Wave 31).
- Each wave produces a commit with `feat(waveN):` prefix and an evidence bundle.
- The CHANGELOG records wave-level summaries, not individual commits.
- Evidence bundles are named with the sprint identifier: `lowcode-plugin-*-waveN-YYYYMMDD`.
- Sprint reports under `reports/` are gitignored but referenced by evidence bundles.

## Consequences

- Every version bump maps to a specific sprint with traceable evidence.
- CHANGELOG entries are auditable against evidence bundles.
- Pre-1.0 semver signals the project is in active development.
- Wave numbering provides chronological ordering across sprint types.
