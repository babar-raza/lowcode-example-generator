# Lane 7: Test Suite and Validator Hardening

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## Regression Test Results

```
tests/unit/test_durable_fixes.py - 35 passed in 0.98s
```

### New Tests Added (10 tests)

| Test Class | Test Name | Purpose |
|------------|-----------|---------|
| TestTemplateFirstConfig | test_slides_yml_has_template_first_for_convert | Verify slides.yml Convert has template_first |
| TestPdfTableGeneratorFix | test_uses_new_table_options | new TableOptions() not TableOptions.Create() |
| TestPdfTableGeneratorFix | test_no_table_options_create_fluent_chain | No broken chain pattern |
| TestPdfTableGeneratorFix | test_calls_add_input | options.AddInput present |
| TestPdfTableGeneratorFix | test_calls_add_output | options.AddOutput present |
| TestPdfTableGeneratorFix | test_calls_table_generator_process | new TableGenerator().Process(options) |
| TestSlidesConvertFix | test_uses_fully_qualified_convert | Aspose.Slides.LowCode.Convert.ToPdf( |
| TestSlidesConvertFix | test_no_bare_convert_call | No bare Convert.ToPdf( (CS0104 prevention) |
| TestSlidesConvertFix | test_creates_input_pptx | new Presentation() for fixture |
| TestSlidesConvertFix | test_uses_save_format_pptx | SaveFormat.Pptx for PPTX output |

### Previously Existing Tests (25 tests) - All Still Pass

- TestDiagramDeterministicTemplate (9 tests) - DiagramConverter, PdfConverter
- TestCellsDeterministicTemplate (3 tests) - SpreadsheetMerger File.Copy
- TestWordsDeterministicTemplate (7 tests) - Merger, Watermarker
- TestTemplateFirstConfig (6 tests) - YAML config verification

## Fixes Covered by New Tests

### DEF-008: pdf-table-generator TableOptions chain fix
- **Root cause**: `var options = TableOptions.Create()...chain...AddParagraph(...)` returned `TableCellBuilder`,
  not `TableOptions`, causing CS1061 on `AddInput`/`AddOutput`
- **Fix**: `new TableOptions()` + call methods separately without reassigning from chain
- **Tests**: 5 new tests verify correct pattern

### DEF-009: slides-convert System.Convert ambiguity fix
- **Root cause**: Bare `Convert.ToPdf()` was ambiguous with `System.Convert` (CS0104)
- **Fix**: Fully-qualified `Aspose.Slides.LowCode.Convert.ToPdf()`
- **Tests**: 4 new tests verify no bare calls and correct namespace usage

## Full Test Suite Status

- `tests/unit/test_durable_fixes.py`: 35/35 PASS
- pytest available via `.venv/Scripts/python.exe -m pytest`
- C:/Python313/python.exe: pytest not installed (use .venv for tests)
