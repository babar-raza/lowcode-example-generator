# Lane B — PDF PR Merge Preflight

**Status:** GATE_ABSENT_MERGE_BLOCKED

## Approval Gate Check

| Variable | Required Value | Actual Value | Result |
|----------|---------------|--------------|--------|
| PLUGIN_EXAMPLES_MERGE_PR_APPROVAL | APPROVE_MERGE_PR | (empty) | BLOCKED |
| PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL | APPROVE_LIVE_PR | (empty) | BLOCKED |

## PR State Verification

All 6 PRs are OPEN on aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples:

| PR | State | Examples | Ready to Merge |
|----|-------|----------|---------------|
| #5 | OPEN | doc-converter, html, xls-converter | YES (pending gate) |
| #6 | OPEN | jpeg, png, tiff | YES (pending gate) |
| #7 | OPEN | image-extractor, table-generator, toc-generator | YES (pending gate) |
| #8 | OPEN | security, form-flattener | YES (pending gate) |
| #9 | OPEN | form-editor, form-exporter | YES (pending gate) |
| #10 | OPEN | signature | YES (pending gate) |

## Target Repo Health

- Repo: aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples
- Default branch: main
- Open issues: 6 (the 6 PRs)
- Last push: 2026-05-19

## Action Required

Set environment variable to enable merge:
```
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
```

No merge attempted. No destructive action taken.
