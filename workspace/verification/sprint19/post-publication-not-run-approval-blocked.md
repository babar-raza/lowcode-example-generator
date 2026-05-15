# Post-Publication Verification — Not Run (Approval Blocked)

**Sprint:** sprint19
**Date:** 2026-05-15
**Reason:** No live PRs were created. All publication attempts were dry-run only.

## Blocker

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` was not set to `APPROVE_LIVE_PR` during this sprint execution.

`GH_TOKEN` (classic PAT, `repo` scope) is present and verified to have access to the target repo.
The approval gate is the sole blocker.

## Dry-Run Results

| PR | Types | Package Path | Dry-Run Verdict |
|----|-------|-------------|----------------|
| PR#3 | DocConverter, XlsConverter, Html | `workspace/pr-dry-run/pdf-controlled-pilot` | SIMULATION_PASSED |
| PR#5 | Jpeg, Tiff, Png | `workspace/pr-dry-run/pdf-controlled-pilot-pr5` | PACKAGE_ASSEMBLED |
| PR#6 | TableGenerator, TocGenerator, ImageExtractor | `workspace/pr-dry-run/pdf-controlled-pilot-pr6` | PACKAGE_ASSEMBLED |

## Action Required to Enable Live Publication

```bash
# Set the approval token
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'
# Map classic PAT
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User')

# PR#3 (pdf-controlled-pilot already updated: doc-converter + html + xls-converter)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --promote-latest

# PR#5 (update pdf-controlled-pilot contents: jpeg + tiff + png, then publish)
# PR#6 (update pdf-controlled-pilot contents: table-generator + toc-generator + image-extractor, then publish)
```

## Post-Publication Verification Protocol (when live PRs created)

For each created PR:
1. `gh pr view {number} --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples --json number,title,files,state`
2. Verify: only intended examples, no bin/obj, no secrets, correct csproj
3. Verify README is present and correct
4. After merge: run `plugin_examples release-status --promote-latest` to confirm post-merge validation
