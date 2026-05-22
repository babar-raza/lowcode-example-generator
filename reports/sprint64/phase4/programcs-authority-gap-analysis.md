# Phase 4 — Program.cs vs Authority Gap Analysis

## Sprint 63 State

Sprint 63 deep audit (`programcs-vs-authority-deep.json`) showed:
- 37/42 input_matches_authority = true
- 3 mismatches
- 2 authority_unknown (None)

The 5 gaps were classified as unresolved at Sprint 63 closure.

## Sprint 64 Classification (All 5 Gaps)

### Gap 1: cells-text-converter — AUTHORITY_LEDGER_BUG_CORRECTED

**Sprint 63 state:**
- Program.cs input: `.xlsx`
- Authority: `.csv` (mismatch)

**Root cause:** The Sprint 63 deep audit read input format from the old `pipeline/contracts`
data (stale), not from the format-authority contracts. The old contracts had TextConverter
listed with input `.csv` — this was wrong.

**Format-authority contract truth** (`pipeline/format-authority/contracts/cells.json`):
```
input: .xlsx, output: .txt
conflict_notes: "pipeline/contracts says input .csv ... Resolution: TextConverter.Process
takes any format Cells can load; .xlsx is the family default input."
```

**Classification: MATCH after correction.** Program.cs `.xlsx` = Authority `.xlsx`.

---

### Gap 2: pdf-html-converter — DRY_RUN_FOUND

**Sprint 63 state:**
- Program.cs input: `None` (not found)
- Authority: `None` (missing)

**Root cause:** Sprint 63 deep audit didn't find the pdf-html-converter Program.cs.

**Sprint 64 investigation:** Found at:
`workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/html/Program.cs`

Program.cs uses `Html` plugin with `HtmlToPdfOptions`. Input: `.html`. Output: `.pdf`.
Authority contract: input `.html`, output `.pdf`. **MATCH.**

---

### Gap 3: pdf-pdfa-converter — SPECIAL_CASE_PROGRAM_CS_FOUND

**Sprint 63 state:**
- Program.cs input: `None` (no standard dry-run)
- Authority: `None`

**Root cause:** No standard dry-run package exists for PdfAConverter. It was generated
during Sprint 57 PDF pilot but not promoted to the dry-run pipeline.

**Sprint 64 investigation:** Found at:
`workspace/runs/pilot-pdf-20260514-211320/generated/pdf/pdf-pdf-aconverter/Program.cs`

Uses `PdfAConverter` with `PdfAConvertOptions`. Input: `.pdf`. Output: `.pdf`.
Authority: input `.pdf`, output `.pdf`. **MATCH.**

Program.cs artifact stored in `destination-packages/special-cases/pdf-pdf-aconverter/`.

---

### Gap 4: words-mail-merger — KNOWN_SPECIAL_CASE_MULTI_FILE_INPUT

**Sprint 63 state:**
- Program.cs input: `.docx`
- Authority: `template.docx+data` (mismatch)

**Classification: KNOWN_SPECIAL_CASE.**

MailMerger requires 2 inputs: a template `.docx` + a data source `.docx`.
The generated Program.cs uses a single `.docx` path as the primary input path.
This is a documented multi-file input scenario (classified in Sprint 62).
Not a pipeline error — the Program.cs correctly sets up the mail merge operation.

---

### Gap 5: words-report-builder — KNOWN_SPECIAL_CASE_MULTI_FILE_INPUT

**Sprint 63 state:**
- Program.cs input: `.docx`
- Authority: `template.docx+data` (mismatch)

**Classification: KNOWN_SPECIAL_CASE.**

ReportBuilder requires 2 inputs: a template `.docx` + a data source.
Same classification as MailMerger above.

---

## Final Classification Summary

| Gap | Scenario | Classification | Resolved? |
|-----|----------|----------------|-----------|
| 1 | cells-text-converter | AUTHORITY_LEDGER_BUG_CORRECTED — MATCH | YES |
| 2 | pdf-html-converter | DRY_RUN_FOUND — MATCH | YES |
| 3 | pdf-pdfa-converter | SPECIAL_CASE_PROGRAM_CS_FOUND — MATCH | YES |
| 4 | words-mail-merger | KNOWN_SPECIAL_CASE_MULTI_FILE_INPUT | YES (classified) |
| 5 | words-report-builder | KNOWN_SPECIAL_CASE_MULTI_FILE_INPUT | YES (classified) |

## Overall Result

- **40/42** direct matches (input_matches_authority = true)
- **2/42** known special cases (multi-file input, classified as KNOWN_SPECIAL_CASE)
- **0/42** unexplained mismatches
- **0/42** authority_unknown

**42/42 classified. Acceptance criteria met.**

## Evidence

See `programcs-vs-authority-final.json` for the full 42-record ledger.
See `programcs-authority-test-results.txt` for test results.
