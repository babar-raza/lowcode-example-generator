# Sprint 75 — Words Version Drift Repair Plan

**Date:** 2026-05-23
**Classification:** NEEDS_REPAIR (repair blocked by approval absent)

## Current State

| Source | Version |
|--------|---------|
| Remote published (GitHub) | 26.4.0 |
| Local handoff (Directory.Packages.props) | 26.5.0 |
| Canonical version (version-truth-matrix) | 26.5.0 |
| NuGet latest | 26.5.0 |

The remote Words repo has example csproj files referencing Aspose.Words 26.4.0.
The handoff packages have been updated to 26.5.0.
No new version regeneration is required — the 26.5.0 packages are ready in handoff.

## What the Repair Requires

The README I/O PR for Words will:
1. Add Input/Output sections to all 8 remote Words README files
2. Bump the `<PackageVersion Include="Aspose.Words" Version="26.4.0" />` entries
   to `Version="26.5.0"` in each Words example's csproj

The version bump is part of the same PR that adds README I/O sections.
No separate code regeneration or build/run is required.
The 8 Words examples were generated and verified at 26.5.0 in sprint75 handoff.

## Approval Requirement

| Token | Status |
|-------|--------|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` | ABSENT |

Version drift cannot be pushed to remote until approval is present.

## Classification

- **Words version drift:** NEEDS_REPAIR, but APPROVAL_BLOCKED
- Repair package is ready (handoff at 26.5.0)
- No additional build or regeneration step needed
- Verdict: version drift will persist until approval enables README I/O PR creation

## Impact

Until the repair is applied:
- Remote Words examples run with 26.4.0 package
- 26.4.0 is a prior-month release; no breaking API changes identified
- Examples produce correct output at both versions
- Drift is cosmetic for runtime correctness but is a publication accuracy gap

## Next Action

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and run publication sprint.
The PR will include both README I/O additions and version bump from 26.4.0 to 26.5.0.
