# ADR: Non-LowCode Plugin Repo Folder Layout

Date: 2026-06-08 | Status: ACCEPTED | Wave: 22

## Decision
Non-LowCode plugin example repos use: `examples/<family>/<slug>/`
(No `/plugins/` segment needed; repo name (`*.Plugins-for-.NET-Examples`) provides the context.)

## Rationale
- LowCode repos need `/lowcode/` segment because they may contain both LowCode and plain API examples.
- Plugin-only repos have no such ambiguity.
- Shorter paths are easier to maintain and navigate.

## Branch Naming Policy
- New branches (Wave 22+): `plugins/wave<N>/<family>-plugin-examples`
- Existing open PRs (Wave 19/20/21): `lowcode/wave19/` branches are grandfathered.
  These cannot be renamed without closing the PR. They will retain their names until merged.
- After merge: branches deleted per standard post-merge cleanup policy.

## Approved By
Wave 21 (initial ADR), Wave 22 (confirmed and extended).
