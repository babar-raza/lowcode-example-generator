# Sprint 81 -- Words Version Drift Decision (Phase 4)

## Carry-Forward Context

Sprint 75 memory recorded: Remote=26.4.0, handoff=26.5.0 (version drift, approval-blocked repair).

## Sprint 81 Finding

Fresh verification of remote Words repo on 2026-05-24:

```
gh api repos/aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples/contents/Directory.Packages.props
→ <PackageVersion Include="Aspose.Words" Version="26.5.0" />
```

**Remote Words version: 26.5.0**
**Handoff Words version: 26.5.0** (reports/sprint72/handoff/per-family/words/Directory.Packages.props)

## Decision

**WORDS_VERSION_DRIFT_RESOLVED**

The remote Words repo is already at 26.5.0, matching the accepted handoff target.
No version bump is needed in the Sprint 81 README I/O PR for Words.

## Likely Cause

The version was updated when Words examples were first published (Sprint 72/73 period).
The Sprint 75 tracking of "Remote=26.4.0" was either stale or reflected a per-example props file
that no longer exists (examples use the root Directory.Packages.props).

## Sprint 81 Action

- Words README I/O PR: include example READMEs only, no version change
- No separate version-bump PR needed

---
*Phase 4 -- Sprint 81 -- 2026-05-24*
