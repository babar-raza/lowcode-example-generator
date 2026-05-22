# Portfolio Family/Plugin Matrix — Sprint 42

Generated: 2026-05-19

## Active Families (6)

| Family | Pkg Version | Types | WF Roots | Pilot | Published | PR Ready | Contracts | Coverage | Status |
|--------|-------------|-------|----------|-------|-----------|----------|-----------|----------|--------|
| Cells | 26.5.1 | 22 | 9 | 9 | 9 | 0 | 9 | 100% | COMPLETE |
| Words | 26.5.0 | 25 | 9 | 8 | 8 | 0 | 8 | 100% | COMPLETE |
| PDF | 26.5.0 | 101 | 22 | 19 | 5 | 14 | 19 | 26.3% | PR_MERGE_BLOCKED |
| Diagram | 26.5.0 | 5 | 2 | 2 | 2 | 0 | 2 | 100% | COMPLETE |
| Email | 26.4.0 | 3 | 1 | 1 | 1 | 0 | 1 | 100% | COMPLETE |
| Slides | 26.5.0 | 5 | 3 | 3 | 3 | 0 | 3 | 100% | COMPLETE |

## Blocked Families (2)

| Family | Status | Blocker |
|--------|--------|---------|
| OCR | DEPENDENCY_BLOCKED | Aspose.AI.LLM internal assembly not on NuGet |
| PSD | DEPENDENCY_BLOCKED | Aspose.JavaAttributes internal assembly not on NuGet |

## Totals

- **Active families**: 6
- **Total LowCode types**: 161
- **Total workflow root types**: 46
- **Total pilot-allowed**: 42
- **Total published**: 28
- **Total PR dry-run ready**: 14
- **Total pipeline contracts**: 42
- **Total after all merges**: 42

## Permanently Blocked Workflow Roots

1. **words/Processor** — no public constructor, no static entrypoint (CS1729+CS0120)
2. **pdf/Timestamp** — external TSA ServerUrl required
3. **pdf/Ofd** — OFD input format, no programmatic fixture

## Deferred

1. **pdf/FormImporter** — Aspose.PDF 26.5.0 bug, Wave H candidate

## PDF PR Status

6 PRs open on aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples:
- PR#5: doc-converter, html, xls-converter
- PR#6: jpeg, png, tiff
- PR#7: image-extractor, table-generator, toc-generator
- PR#8: security, form-flattener
- PR#9: form-editor, form-exporter
- PR#10: signature

All require `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`.
