# PDF Maximum Achievable Coverage Report

**Sprint:** 28 | **Date:** 2026-05-17 | **Package:** Aspose.PDF 26.5.0

## Summary

| Metric | Value |
|--------|-------|
| Total LowCode types in namespace | 101 |
| Workflow root (runnable) types | 22 |
| Non-runnable types | 79 |
| Pilot-allowed types | 19 |
| Currently published | 5 |
| PR_DRY_RUN_READY (pending approval) | 14 |
| Permanently blocked | 2 |
| Library-defect deferred | 1 |

## Maximum Achievable Coverage

With Aspose.PDF 26.5.0, the maximum achievable published coverage is:

**19 / 22 workflow_root types = 86.4%**

### Composition

| Type | Wave | Status |
|------|------|--------|
| Merger | A | PUBLISHED (PR#1) |
| TextExtractor | A | PUBLISHED (PR#1) |
| PdfAConverter | A | PUBLISHED (PR#2) |
| Splitter | A | PUBLISHED (PR#2) |
| Optimizer | A | PUBLISHED (PR#4) |
| DocConverter | A | PR_DRY_RUN_READY (PR#3) |
| XlsConverter | A | PR_DRY_RUN_READY (PR#3) |
| Html | A | PR_DRY_RUN_READY (PR#3) |
| Jpeg | B | PR_DRY_RUN_READY (PR#5) |
| Tiff | B | PR_DRY_RUN_READY (PR#5) |
| Png | B | PR_DRY_RUN_READY (PR#5) |
| TocGenerator | C/D | PR_DRY_RUN_READY (PR#6) |
| TableGenerator | C/D | PR_DRY_RUN_READY (PR#6) |
| ImageExtractor | C/D | PR_DRY_RUN_READY (PR#6) |
| Security | E | PR_DRY_RUN_READY (PR#7) |
| FormFlattener | E | PR_DRY_RUN_READY (PR#7) |
| FormEditor | F | PR_DRY_RUN_READY (PR#8) |
| FormExporter | F | PR_DRY_RUN_READY (PR#8) |
| Signature | G | PR_DRY_RUN_READY (PR#9) |
| **Timestamp** | - | **PERMANENTLY_BLOCKED** — external TSA required |
| **Ofd** | - | **PERMANENTLY_BLOCKED** — OFD format, no fixture API |
| **FormImporter** | H | **LIBRARY_DEFECT** — NullReferenceException Aspose.PDF 26.5.0 |

## Blocked Items — Will Not Change Without External Action

- **Timestamp**: Requires RFC 3161 TSA server URL. No self-signed alternative exists.
- **Ofd**: OFD is a Chinese national PDF-variant format. No programmatic OFD creation in .NET.
- **FormImporter**: Aspose.PDF internal bug. Retest when package version > 26.5.0.

## Conclusion

Upon setting `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`, publishing PR#3 through PR#9 will achieve the **maximum possible coverage** of 19/22 workflow root types with Aspose.PDF 26.5.0.
