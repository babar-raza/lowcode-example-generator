# PdfAConverter Fix Proof — Sprint 58 Lane D

**Date:** 2026-05-21
**Fix:** Add `using Aspose.Pdf.Text;` to `per_type_constraints.PdfAConverter.REQUIRED` in pdf.yml
**Root Cause:** LLM generated code that used `TextFragment` without `using Aspose.Pdf.Text;` directive, causing CS0246 compile error

---

## Defect

Sprint 57 reported: `pdf-pdf-aconverter` generation failed. LLM output contained `TextFragment` usage but omitted the required `using Aspose.Pdf.Text;` directive.

**Error class:** CS0246 — The type or namespace name 'TextFragment' could not be found

**Known constraint already present for DocConverter and other types** (`using Aspose.Pdf.Text;`) — was missing from PdfAConverter.

---

## Fix Applied

**File:** `pipeline/configs/families/pdf.yml`
**Change:** Added entry to `per_type_constraints.PdfAConverter.required`:
```
- "REQUIRED: using Aspose.Pdf.Text; (for TextFragment in fixture creation)"
```

---

## Regression Tests Added

**File:** `tests/unit/test_llm_generation.py`
**Class:** `TestPdfAConverterConstraint` (3 tests)

| Test | Description | Result |
|------|-------------|--------|
| `test_pdfaconverter_config_requires_using_aspose_pdf_text` | Loads pdf.yml and verifies PdfAConverter.required contains Aspose.Pdf.Text entry | PASS |
| `test_pdfaconverter_code_missing_using_pdf_text_fails_validation` | Code without `using Aspose.Pdf.Text;` is flagged by `_validate_code_from_constraints` | PASS |
| `test_pdfaconverter_code_with_using_pdf_text_passes_validation` | Code with `using Aspose.Pdf.Text;` passes validation | PASS |

---

## Full Test Suite After Fix

**Result:** 2819 passed, 3 skipped, 0 failed (81.22s)
**Delta vs Sprint 57:** +3 tests (3 new PdfAConverter regression tests)

---

## Regeneration Status

- **Before fix:** pdf-pdf-aconverter generation failed (1/42 fail)
- **After fix:** Constraint now enforces `using Aspose.Pdf.Text;` — LLM will be required to include it or repaired to include it
- **Regeneration:** Will be executed in Phase 5 (Lane E) as part of full 42/42 regeneration

---

## Evidence Reference

- pdf.yml modification: `pipeline/configs/families/pdf.yml` (line ~208)
- Test file: `tests/unit/test_llm_generation.py` (class `TestPdfAConverterConstraint`)
- Test run: Full suite 2819/2819 PASS
