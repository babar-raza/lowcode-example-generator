# README Correction Preview — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Coverage:** 42/42 scenarios, 6/6 repos
**Special Cases Resolved:** 4 (upgraded from Sprint 61 partial state)

---

## Coverage Summary

| Family | Scenarios | Standard | Special Case | All Resolved |
|--------|-----------|----------|--------------|--------------|
| Cells | 9 | 9 | 0 | YES |
| Words | 8 | 6 | 2 (mail-merger, report-builder) | YES |
| PDF | 19 | 17 | 2 (pdf-aconverter, text-extractor) | YES |
| Diagram | 2 | 2 | 0 | YES |
| Email | 1 | 1 | 0 | YES |
| Slides | 3 | 3 | 0 | YES |
| **Total** | **42** | **38** | **4** | **YES** |

---

## Special Case Upgrades (Sprint 61 → Sprint 62)

### words-mail-merger
**Before (Sprint 61):** `**Output:** .docx file` (input missing)
**After (Sprint 62):**
```markdown
## Input and Output

The example takes a Word template file (`template.docx`) and in-memory merge field data as input.
The merged document is saved as `result.docx`.
```

### words-report-builder
**Before (Sprint 61):** `**Output:** .docx file` (input missing)
**After (Sprint 62):**
```markdown
## Input and Output

The example takes a Word template file (`template.docx`) and an in-memory data source object as input.
The generated report is saved as `report.docx`.
```

### pdf-pdf-aconverter
**Before (Sprint 61):** No correction package (was classified no-local-package)
**After (Sprint 62):**
```markdown
## Input and Output

The example takes a PDF file (`input.pdf`) as input.
The converted PDF/A-compliant document is saved as `output.pdf`.
```

### pdf-text-extractor
**Before (Sprint 61):** `**Output:** Text extracted to stdout` (input missing)
**After (Sprint 62):**
```markdown
## Input and Output

The example takes a PDF file (`input.pdf`) as input.
The extracted text is printed to standard output (no output file is created).
```

---

## Sample Corrections — Standard Cases

### cells-html-converter
```markdown
## Input and Output

The example takes a spreadsheet file (`input.xlsx`) as input.
The converted HTML page is saved as `output.html`.
```

### pdf-merger
```markdown
## Input and Output

The example takes multiple PDF files (`.pdf`) as input.
The merged PDF document is saved as `output.pdf`.
```

### email-converter
```markdown
## Input and Output

The example takes an email file (`input.eml`) as input.
The converted HTML files are written to an output directory.
```

### diagram-pdf-converter
```markdown
## Input and Output

The example takes a Visio diagram file (`input.vsdx`) as input.
The converted PDF document is saved as `output.pdf`.
```

---

## Publication Requirements

All 42 corrections require:
1. `APPROVE_README_PUSH` approval token
2. README audit gate to pass in publish-pr pipeline
3. Version drift resolution for Words/Diagram before push (Phase 5)

The 4 special-case corrections also require:
- `io-special/special-case-authority.json` to be PRESENT as authority source
