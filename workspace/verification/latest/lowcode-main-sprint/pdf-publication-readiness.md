# Lane C — PDF Publication Readiness Report

**Date:** 2026-05-19
**Status:** DRY-RUN READY (live publication blocked by APPROVE_LIVE_PR)

## Package Inventory

| PR Package | Examples | Package Path | Status |
|-----------|----------|-------------|--------|
| PR#5 (pdf-controlled-pilot) | doc-converter, html, xls-converter | workspace/pr-dry-run/pdf-controlled-pilot/ | DRY-RUN READY (pipeline contracts exist) |
| PR#6 (pdf-controlled-pilot-pr5) | jpeg, png, tiff | workspace/pr-dry-run/pdf-controlled-pilot-pr5/ | DRY-RUN READY (pipeline contracts exist) |
| PR#7 (pdf-controlled-pilot-pr6) | image-extractor, table-generator, toc-generator | workspace/pr-dry-run/pdf-controlled-pilot-pr6/ | DRY-RUN READY (pipeline contracts exist) |
| PR#8 (pdf-controlled-pilot-pr7) | security, form-flattener | workspace/pr-dry-run/pdf-controlled-pilot-pr7/ | DRY-RUN READY (no pipeline contracts) |
| PR#9 (pdf-controlled-pilot-pr8) | form-editor, form-exporter | workspace/pr-dry-run/pdf-controlled-pilot-pr8/ | DRY-RUN READY (no pipeline contracts) |
| PR#10 (pdf-controlled-pilot-pr9) | signature | workspace/pr-dry-run/pdf-controlled-pilot-pr9/ | DRY-RUN READY (no pipeline contracts) |

## Gate Status

- Lane A evidence intake: COMPLETE
- Lane B state reconciliation: COMPLETE (denominators fixed)
- GITHUB_TOKEN availability: AVAILABLE (GH_TOKEN mapped via classic PAT)
- APPROVE_LIVE_PR: NOT SET (blocks live PR creation)
- APPROVE_MERGE_PR: NOT SET (blocks PR merge)
- Target repo health: HEALTHY (aspose-pdf-net accessible via gh CLI)

## Publication Blockers

1. **APPROVE_LIVE_PR not set** — operator must set PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
2. **Pipeline contracts missing for PR#8-PR#10** — 5 examples (security, form-flattener, form-editor, form-exporter, signature) lack pipeline/contracts/pdf/ entries
3. **Open PRs #5-#10 on target repo** — require human review/merge with APPROVE_MERGE_PR

## Dry-Run Verification

All 6 PDF PR packages exist with:
- Directory.Build.props and Directory.Packages.props present
- examples/pdf/lowcode/{type}/ directory structure
- Program.cs and .csproj files for each example
- README.md per example
- Root README.md per package

## Recommendation

- Do NOT create live PRs without APPROVE_LIVE_PR
- Create pipeline contracts for PR#8-PR#10 examples before publication
- Verify all examples still build/run against current Aspose.PDF 26.5.0
