Sprint 88 — Fixture Readiness Plan
=====================================
Date: 2026-05-25

## Current Fixture State

All 42 active examples have verified fixtures in `pipeline/fixtures/{family}/{example}/`:
- cells: 9 examples — all fixtures present
- words: 8 examples — all fixtures present
- pdf: 19 examples — all fixtures present (FormImporter BLOCKED_EXTERNAL)
- diagram: 2 examples — all fixtures present
- email: 1 example — fixture present
- slides: 3 examples — all fixtures present

## Next-Family Fixture Readiness

| Family | Status | Fixture Path | Blocker |
|--------|--------|-------------|---------|
| OCR | NOT_READY | pipeline/fixtures/ocr/ (not created) | Aspose.AI.LLM missing from NuGet |
| PSD | NOT_READY | pipeline/fixtures/psd/ (not created) | Aspose.JavaAttributes missing from NuGet |
| HTML | NOT_READY | pipeline/fixtures/html/ (not created) | DllReflector assembly resolution |
| SVG | NOT_READY | pipeline/fixtures/svg/ (not created) | DllReflector assembly resolution |

## Trigger Conditions

Fixture creation for next-family candidates will proceed when:
1. **OCR**: Aspose.AI.LLM appears on NuGet → DllReflector can resolve all deps → reflection identifies LowCode APIs → fixtures generated
2. **PSD**: Aspose.JavaAttributes appears on NuGet → same pipeline as OCR
3. **HTML/SVG**: DllReflector assembly resolution fixed → reflection proceeds → fixtures generated

## FormImporter Special Case

- **Family**: PDF
- **Example**: form-importer
- **Status**: BLOCKED_EXTERNAL
- **Blocker**: Aspose.PDF 26.5.0 NullRef bug (carry-forward from Sprint 75)
- **Trigger**: TRG-01 fires when Aspose.PDF NuGet version > 26.5.0
- **Repro**: `workspace/defect-repros/pdf-formimporter-nullref/`
