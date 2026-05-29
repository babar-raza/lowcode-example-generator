# Lane 3: Clean Regeneration Proof

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## Summary

All 6 families regenerated cleanly from scratch (via --replay-from generation) with durable fixes applied.
42 examples generated, 42 built, 42 runtime passed.

## Per-Family Results

| Family | Run ID | Generated | Built | Runtime | Verdict |
|--------|--------|-----------|-------|---------|---------|
| cells | pilot-cells-20260529-221017 | 9 | 9 | 9 | DATA_FLOW_PROTOTYPE_ONLY |
| diagram | pilot-diagram-20260529-221021 | 2 | 2 | 2 | DATA_FLOW_PROTOTYPE_ONLY |
| words | pilot-words-20260529-221024 | 8 | 8 | 8 | DATA_FLOW_PROTOTYPE_ONLY |
| pdf | pilot-pdf-20260529-222233 | 19 | 19 | 19 | DATA_FLOW_PROTOTYPE_ONLY |
| email | pilot-email-20260529-220716 | 1 | 1 | 1 | DATA_FLOW_PROTOTYPE_ONLY |
| slides | pilot-slides-20260529-221814 | 3 | 3 | 3 | DATA_FLOW_PROTOTYPE_ONLY |
| **TOTAL** | | **42** | **42** | **42** | |

## Durable Fixes Applied Per Family

### cells: SpreadsheetMerger
- Fix: `template_first: true` + deterministic template using `File.Copy` from fixture
- Pattern: `File.Copy(inputPath, input1Path, overwrite: true)` before `SpreadsheetMerger.Process()`
- BEFORE: `new Workbook()` direct construction for merger inputs
- AFTER: File.Copy from fixture -- eliminates runtime path errors

### diagram: DiagramConverter, PdfConverter
- Fix: `template_first: true` + deterministic template using `page.DrawEllipse()`
- Pattern: `long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0)` + `page.Shapes.GetShape(shapeId)`
- BEFORE: `new Shape() + TypeValue.Shape` -- CS0117 (TypeValue.Shape does not exist)
- AFTER: DrawEllipse API -- 0 build errors, 1 obsolete warning

### words: Merger, Watermarker
- Merger fix: `File.Copy` pattern (same as cells SpreadsheetMerger)
- Watermarker fix: Programmatic 1x1 BMP byte array instead of passing "sample" (nonexistent file)
- BEFORE: Watermarker.SetImage(inputPath, output, "sample") -- FileNotFoundException
- AFTER: File.WriteAllBytes(imagePath, bmpBytes) + Watermarker.SetImage(inputPath, output, imagePath)

### pdf: TableGenerator
- Fix: Changed from broken `TableOptions.Create()` fluent chain to `new TableOptions()` instance pattern
- Root cause: `TableOptions.Create()...chain...` ends at `TableCellBuilder`, not `TableOptions`
  -- CS1061: 'TableCellBuilder' does not contain a definition for 'AddInput'
- AFTER: `var options = new TableOptions(); options.InsertPageBefore(1); options.AddTable()...`
  -- 0 build errors, runtime "Table added" confirmed

### slides: Convert
- Fix: Fully-qualified `Aspose.Slides.LowCode.Convert.ToPdf()` instead of bare `Convert.ToPdf()`
- Root cause: CS0104: 'Convert' is ambiguous between 'Aspose.Slides.LowCode.Convert' and 'System.Convert'
- AFTER: `Aspose.Slides.LowCode.Convert.ToPdf(inputPath, outputPath)` -- 0 build errors

### email: (no new fixes)
- email had no broken template patterns -- existing template_mode was sufficient

## Replay Mode Justification

All families used `--replay-from generation --reuse-run <base-run>` to:
1. Avoid redundant NuGet re-downloads (packages verified in prior runs)
2. Ensure fresh code generation with the durable fixes applied from Lane 2
3. Run the full downstream pipeline (validation, reviewer, publisher, gates)

This is NOT a --replay-from validation shortcut. The generation stage ran fresh for all families,
confirming that the template_first templates produce correct, compiling, running code on every clean run.
