# README Special-Case Text — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Purpose:** Authoritative README I/O documentation text for 4 special-case scenarios.
**Status:** ALL 4 RESOLVED

These 4 scenarios cannot use the standard file extension templates because their input or output
does not follow the standard single-file-to-single-file pattern. The text below is the authority
for README I/O sections.

---

## pdf-pdf-aconverter

**Special case type:** Standard file-to-file, but PDF → PDF (non-obvious without context)

**Input description:**
```
The example takes a PDF file (`input.pdf`) as input.
```

**Output description:**
```
The converted PDF/A-compliant document is saved as `output.pdf`.
```

**Full I/O section for README:**
```markdown
## Input and Output

The example takes a PDF file (`input.pdf`) as input.
The converted PDF/A-compliant document is saved as `output.pdf`.
```

**Authority:** PdfAConverter with FileDataSource("input.pdf") and AddOutput(new FileDataSource("output.pdf"))
confirmed in workspace/runs/pilot-pdf-20260514-211320/generated/pdf/pdf-pdf-aconverter/Program.cs

---

## pdf-text-extractor

**Special case type:** File input → stdout (no output file)

**Input description:**
```
The example takes a PDF file (`input.pdf`) as input.
```

**Output description:**
```
The extracted text is printed to standard output (no output file is created).
```

**Full I/O section for README:**
```markdown
## Input and Output

The example takes a PDF file (`input.pdf`) as input.
The extracted text is printed to standard output (no output file is created).
```

**Authority:** TextExtractor with FileDataSource("input.pdf") and StringResult from
ResultCollection[0] printed to Console. No AddOutput() call.

---

## words-mail-merger

**Special case type:** Template file + in-memory data → output file

**Input description:**
```
The example takes a Word template file (`template.docx`) and in-memory merge field data as input.
```

**Output description:**
```
The merged document is saved as `result.docx`.
```

**Full I/O section for README:**
```markdown
## Input and Output

The example takes a Word template file (`template.docx`) and in-memory merge field data as input.
The merged document is saved as `result.docx`.
```

**Authority:** MailMerger.Execute(document, fieldNames, fieldValues) where document is a programmatically
created template.docx and fieldNames/fieldValues are in-memory arrays.

---

## words-report-builder

**Special case type:** Template file + in-memory data object → output file

**Input description:**
```
The example takes a Word template file (`template.docx`) and an in-memory data source object as input.
```

**Output description:**
```
The generated report is saved as `report.docx`.
```

**Full I/O section for README:**
```markdown
## Input and Output

The example takes a Word template file (`template.docx`) and an in-memory data source object as input.
The generated report is saved as `report.docx`.
```

**Authority:** ReportBuilder.BuildReport(document, dataSource) where document is a programmatically
created template.docx and dataSource is a Person object containing nested Manager and Order collections.

---

## Usage in README Correction Packages

These texts are the authority source for the readme-corrections/ Phase 3 packages.
Phase 3 must incorporate these exact descriptions for the 4 special-case scenarios.
All other 38 scenarios use standard file extension templates derived from Program.cs patterns.
