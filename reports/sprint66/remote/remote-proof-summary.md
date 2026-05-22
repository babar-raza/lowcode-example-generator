# Sprint 66 — Remote Proof Summary

Generated: 2026-05-22
Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof

## Remote Repository State

| Family | Repo | Examples Found | README I/O |
|--------|------|---------------|------------|
| cells | aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples | 9/9 | 0/9 (OLD_FORMAT) |
| words | aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples | 8/8 | 0/8 (OLD_FORMAT) |
| pdf | aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples | 19/19 | 0/19 (OLD_FORMAT) |
| diagram | aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples | 2/2 | 0/2 (OLD_FORMAT) |
| email | aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples | 1/1 | 0/1 (OLD_FORMAT) |
| slides | aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples | 3/3 | 0/3 (OLD_FORMAT) |
| **TOTAL** | | **42/42** | **0/42** |

## Per-PR Example Coverage

### Cells (9 examples, 5 PRs total, 2 with example content)
- PR#1 (2026-05-03): 9 examples — cells-html-converter, cells-image-converter, cells-json-converter, cells-pdf-converter, cells-spreadsheet-converter, cells-spreadsheet-locker, cells-spreadsheet-merger, cells-spreadsheet-splitter, cells-text-converter
- PR#6 (2026-05-20): 1 example — cells-spreadsheet-converter (republish/update)
- PR#2/3/4: root README updates only (0 examples)

### Words (8 examples, 6 PRs total, 3 with example content)
- PR#1 (2026-05-03): 4 examples — words-converter, words-replacer, words-splitter, words-watermarker
- PR#5 (2026-05-13): 3 examples — words-comparer, words-mail-merger, words-merger
- PR#6 (2026-05-14): 1 example — words-report-builder
- PR#2/3/4: root README updates only (0 examples)

### PDF (19 examples, 9 PRs)
- PR#1 (2026-05-06): 2 — pdf-merger, pdf-text-extractor
- PR#2 (2026-05-13): 2 — pdf-pdfa-converter, pdf-splitter
- PR#4 (2026-05-14): 1 — pdf-optimizer
- PR#11 (2026-05-19): 3 — pdf-doc-converter, pdf-html-converter (dir: html), pdf-xls-converter
- PR#17 (2026-05-19): 3 — pdf-jpeg, pdf-png, pdf-tiff
- PR#18 (2026-05-19): 3 — pdf-image-extractor, pdf-table-generator, pdf-toc-generator
- PR#19 (2026-05-19): 2 — pdf-form-flattener, pdf-security
- PR#20 (2026-05-19): 2 — pdf-form-editor, pdf-form-exporter
- PR#21 (2026-05-19): 1 — pdf-signature

### Diagram (2 examples, 1 PR)
- PR#1 (2026-05-12): 2 — diagram-diagram-converter, diagram-pdf-converter

### Email (1 example, 1 PR)
- PR#1 (2026-05-14): 1 — email-converter

### Slides (3 examples, 3 examples, 1 PR)
- PR#1 (2026-05-14): 3 — slides-compress, slides-convert, slides-merger

## Key Findings

1. **All 42 example paths are present in remote repos** — confirmed by GH API directory listing.
2. **0/42 remote READMEs have I/O sections** — all are old-format (API Symbols Used + Run only).
3. **Sprint 65 remote-proof-index.json was incorrect** — it cited 1 PR per family as proving all examples, but:
   - Words: PR#6 covered only 1 example (report-builder), not 8
   - PDF: PR#4 covered only 1 example (optimizer), not 19
   - Actual proof requires per-PR per-example coverage map (this file)
4. **pdf-html-converter note**: Remote dir is named `html` (not `html-converter`). Canonical scenario_id is `pdf-html-converter`.
5. **All examples have Program.cs and README.md** — no missing files in remote repos.

## Sprint 65 Corrections

| Sprint 65 Claim | Actual State |
|----------------|-------------|
| "6 PRs prove 42/42 published" | CONTRADICTED: 6 PRs would mean 1 PR per family; Words used 6 PRs, PDF used 9 PRs |
| Words PR#6 covers all 8 examples | CONTRADICTED: PR#6 covers 1 example (report-builder) only |
| PDF PR#4 covers all 19 examples | CONTRADICTED: PR#4 covers 1 example (optimizer) only |
| Remote README I/O published | CONTRADICTED: 0/42 remote READMEs have I/O sections |

## What IS Verified

- All 42 example directories exist in remote repos ✓
- Each example has Program.cs and README.md ✓
- All examples were introduced by merged PRs ✓
- Per-PR per-example coverage map is now complete ✓
