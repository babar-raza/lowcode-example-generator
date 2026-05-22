# PDF Conflict Recovery Strategy — Sprint 45

## Strategy: CLOSE_AND_RECREATE

All 6 PRs (#5-#10) have README.md conflicts against target main. Recreating from fresh branches is cleaner than rebasing.

## Execution Plan (when APPROVE_LIVE_PR is set)

1. Close existing PRs #5-#10
2. Regenerate README against current target main HEAD
3. Create fresh branches with updated content
4. Open new PRs (same grouping or consolidated)
5. Verify mergeable state

## Current Action
DRY_RUN_ONLY — local packages exist, remote action blocked by absent approval.

## Dry-Run Package Inventory

| Package | Examples |
|---------|----------|
| pr5 | DocConverter, Html, XlsConverter |
| pr6 | Jpeg, Png, Tiff |
| pr7 | ImageExtractor, TableGenerator, TocGenerator |
| pr8 | Security, FormFlattener |
| pr9 | FormEditor, FormExporter |
| (pr10) | Signature (in main package) |
