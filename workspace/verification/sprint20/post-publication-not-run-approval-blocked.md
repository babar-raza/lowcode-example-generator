# Post-Publication Status — Sprint 20

**Date:** 2026-05-16
**Status:** NOT RUN — APPROVAL BLOCKED

## Summary

All three PDF PR groups (PR#3, PR#5, PR#6) are `DRY_RUN_READY_APPROVAL_BLOCKED`.

Live publication was not executed this sprint because `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` was not set.

## Post-Publication Actions (to be run when approval is granted)

| Step | Action | Command |
|------|--------|---------|
| 1 | Publish PR#3 (DocConverter/Html/XlsConverter) | `publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot` |
| 2 | Merge PR#3 after maintainer review | `merge-pr --family pdf --approval-token APPROVE_MERGE_PR` |
| 3 | Publish PR#5 (Jpeg/Png/Tiff) | `publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5` |
| 4 | Merge PR#5 | `merge-pr --family pdf --approval-token APPROVE_MERGE_PR` |
| 5 | Publish PR#6 (ImageExtractor/TableGenerator/TocGenerator) | `publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6` |
| 6 | Merge PR#6 | `merge-pr --family pdf --approval-token APPROVE_MERGE_PR` |
| 7 | Update release status | `release-status --promote-latest` |
| 8 | Update pdf.json published_count 5→14 | Edit pipeline/configs/denominators/pdf.json |

## Token Requirements

```powershell
# Map GH_TOKEN (classic PAT, repo scope) -> GITHUB_TOKEN before each publish step
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
```

## After All Merges

Coverage after PR#3+PR#5+PR#6 merged:
- **Pilot coverage:** 14/14 = 100%
- **Workflow root coverage:** 14/24 = 58.3%
- **Total types coverage:** 14/101 = 13.9%
