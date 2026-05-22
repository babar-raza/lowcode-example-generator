# Lane B — PDF PR Recovery Report

**Status:** PRS_REOPENED_MERGE_GATE_BLOCKED

## PR State Before Recovery

All 6 PRs (#5-#10) were CLOSED without merge (closedAt: 2026-05-19T05:53:19Z-34Z, mergedAt: null).

## Recovery Action

Reopened all 6 PRs using `gh pr reopen`:

| PR | Title | Previous State | New State |
|----|-------|---------------|-----------|
| #5 | Add verified Aspose.Pdf LowCode examples (doc-converter, html, xls-converter) | CLOSED | OPEN |
| #6 | Add verified Aspose.Pdf LowCode examples (jpeg, png, tiff) | CLOSED | OPEN |
| #7 | Add verified Aspose.Pdf LowCode examples (image-extractor, table-generator, toc-generator) | CLOSED | OPEN |
| #8 | Add verified Aspose.Pdf LowCode examples (security, form-flattener) | CLOSED | OPEN |
| #9 | Add verified Aspose.Pdf LowCode examples (form-editor, form-exporter) | CLOSED | OPEN |
| #10 | Add verified Aspose.Pdf LowCode examples (signature) | CLOSED | OPEN |

## Merge Gate Assessment

- `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`: NOT SET (empty)
- `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`: NOT SET (empty)

**Safest governed strategy:** PRs reopened to OPEN state. Merge requires operator to set `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`. No destructive action taken.

## 14 Examples Awaiting Merge

PR#5: pdf-doc-converter, pdf-html-converter, pdf-xls-converter
PR#6: pdf-jpeg, pdf-png, pdf-tiff
PR#7: pdf-image-extractor, pdf-table-generator, pdf-toc-generator
PR#8: pdf-security, pdf-form-flattener
PR#9: pdf-form-editor, pdf-form-exporter
PR#10: pdf-signature
