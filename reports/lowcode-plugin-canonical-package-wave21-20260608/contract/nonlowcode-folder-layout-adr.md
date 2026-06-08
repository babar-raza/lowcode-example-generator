# ADR-001: Non-LowCode Plugin Example Folder Convention

**Date**: 2026-06-08
**Status**: ACCEPTED
**Deciders**: pipeline maintainers (Wave 21 sprint)

## Context
Non-LowCode plugin examples are published to dedicated plugin repos (e.g. Aspose.BarCode.Plugins-for-.NET-Examples).
LowCode examples use `examples/<family>/lowcode/<slug>/` in LowCode repos.

## Decision
For plugin-only repos, use `examples/<family>/<slug>/` without a namespace segment.

## Rationale
1. The repo name itself provides disambiguation (`.Plugins-for-.NET-Examples`).
2. The canonical URL slug is unique per product and already encodes the operation.
3. Adding `/plugins/` would create redundant nesting in single-purpose repos.
4. Matches current PR structure already reviewed by team.

## Consequences
- New PRs must use `examples/<family>/<slug>/`.
- LowCode repos continue to use `examples/<family>/lowcode/<slug>/`.
- Combined repos would use both `lowcode/` and `plugins/` segments.

## Validation
LCV-01 and PPV-01 validators enforce this convention.
