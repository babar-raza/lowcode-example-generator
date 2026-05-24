Sprint 84 — Words Version Status
===================================
Date: 2026-05-24
Author: Lane F

## Current State
- Remote Directory.Packages.props: 26.4.0 (on main branch)
- Handoff Directory.Packages.props: 26.5.0 (sprint72 handoff)
- Drift: YES — remote behind by one minor version

## Drift Type
MINOR_VERSION_DRIFT (same calendar month, minor increment)
Not MAJOR drift (Aspose calendar: month change = major).

## Resolution Status
APPROVAL_BLOCKED

The version fix (26.4.0 → 26.5.0) is bundled into root README PR #7 for words.
PR #7 is open but unmerged (PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=NOT_SET).

## Carry-Forward Policy
This drift has been documented since Sprint 75 and classified as NEEDS_REPAIR_APPROVAL_BLOCKED.
No action taken this sprint — not a source-code blocker.
Sprint 84 batch PR for words EXCLUDES Directory.Packages.props (that change lives in PR #7).

## When Resolved
After PR #7 is merged: remote = 26.5.0 = handoff. Drift = NONE.
