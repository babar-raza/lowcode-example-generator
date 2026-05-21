# README Update Matrix — Sprint 57

**Sprint 57 Lane G**
**Date:** 2026-05-21

## Destination Repo State

All 6 destination repos confirmed via GitHub API:
- README.md present: YES (all 6)
- examples/ directory: YES (all 6)
- examples/{family}/lowcode/ content: VERIFIED (all 42 examples present)

## Version Drift Status

| Family | Repo NuGet Version | Latest NuGet | Drift? | Action |
|--------|------------------|-------------|--------|--------|
| Cells | 26.5.1 | 26.5.1 | NO | None needed |
| Words | 26.4.0 | 26.5.0 | YES | Directory.Packages.props update needed |
| PDF | 26.5.0 | 26.5.0 | NO | None needed |
| Diagram | 26.4.0 | 26.5.0 | YES | Directory.Packages.props update needed |
| Email | 26.4.0 | 26.4.0 | NO | None needed |
| Slides | 26.5.0 | 26.5.0 | NO | None needed |

## README Audit Status

README audit requires APPROVE_README_PUSH to push changes to destination repos.
Current README status for each family:
- Content review: NOT DONE (requires per-example generation run with readme auditor)
- Sprint 56 attempted README audit but deferred (LaneI)
- Sprint 57: README generation via `release-status` confirms README content is managed by the pipeline

## Required README Updates

| Family | README Status | Update Needed? | Blocker |
|--------|-------------|----------------|---------|
| Cells | Managed by pipeline | Verify content | None (APPROVE_README_PUSH needed) |
| Words | Managed by pipeline | Version drift note | Words at 26.4.0 in repo |
| PDF | Managed by pipeline | Verify content | None |
| Diagram | Managed by pipeline | Version drift note | Diagram at 26.4.0 in repo |
| Email | Managed by pipeline | Verify content | None |
| Slides | Managed by pipeline | Verify content | None |

## Branch Auto-Delete Policy

See branch-deletion-policy.md for implementation details.

## Next Actions for Full README Verification

1. Run `release-status --family words --promote-latest` to get README render result
2. Run `release-status --family diagram --promote-latest`
3. For version drift families: need APPROVE_README_PUSH + APPROVE_LIVE_PR to push updates
4. Full README push: `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH` environment variable
