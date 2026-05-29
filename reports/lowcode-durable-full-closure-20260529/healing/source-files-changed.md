# Source Files Changed — Durable Fix Promotion

## Files Modified

### 1. `src/plugin_examples/generator/code_generator.py`
- Added 5 new deterministic templates to `_generate_deterministic_template_for_scenario`
- Added family-namespace-aware dispatch for diagram/cells/words families
- Templates added:
  - `aspose.diagram + diagramconverter` → DrawEllipse-based VSDX + DiagramConverter.Process
  - `aspose.diagram + pdfconverter` → DrawEllipse-based VSDX + PdfConverter.Process
  - `aspose.cells + spreadsheetmerger` → File.Copy fixture + SpreadsheetMerger.Process
  - `aspose.words + merger` → File.Copy fixture + Merger.Merge
  - `aspose.words + watermarker` → BMP bytes + Watermarker.SetText + SetImage

### 2. `src/plugin_examples/generator/packet_builder.py`
- Updated `_PROGRAMMATIC_FIXTURE_GUIDANCE["diagram"]["fixture_code"]`
- Changed from `new Shape() + TypeValue.Shape` to `page.DrawEllipse()` pattern
- Added FORBIDDEN patterns for TypeValue.Shape and direct DoubleValue assignment
- Updated required_patterns to reflect DrawEllipse approach

### 3. `pipeline/configs/families/diagram.yml`
- Added `template_first: true` to `per_type_constraints.DiagramConverter`
- Added `template_first: true` to `per_type_constraints.PdfConverter`
- Added API-correct REQUIRED and FORBIDDEN patterns for DrawEllipse and DoubleValue

### 4. `pipeline/configs/families/cells.yml`
- Added `SpreadsheetMerger` entry to `per_type_constraints`
- Added `template_first: true` with File.Copy fixture pattern

### 5. `pipeline/configs/families/words.yml`
- Added `template_first: true` to `per_type_constraints.Merger` with File.Copy fixture
- Added `template_first: true` to `per_type_constraints.Watermarker` with BMP creation

### 6. `pipeline/configs/families/pdf.yml` (Pass 2)
- Fixed `TableGenerator.required` constraint: changed from `TableOptions.Create()` to `new TableOptions()`
- Updated `mandatory_reference_example` to show correct non-chain pattern
- Fixed `forbidden`: removed incorrect "FORBIDDEN: new TableOptions()" entry
- Root cause: `TableOptions.Create()...chain...` ends at `TableCellBuilder` (CS1061 on AddInput)

### 7. `pipeline/configs/families/slides.yml` (Pass 2)
- Added `template_first: true` to `per_type_constraints.Convert`
- Changed REQUIRED patterns to code-matchable tokens
- Added FORBIDDEN for bare `Convert.ToPdf(` to prevent CS0104 (System.Convert ambiguity)

### Pass 2 additions to `src/plugin_examples/generator/code_generator.py`
- Added `aspose.slides + convert` deterministic template
  → `Aspose.Slides.LowCode.Convert.ToPdf()` fully-qualified (avoids CS0104)
- Fixed `pdf + tablegenerator` deterministic template
  → `new TableOptions()` pattern instead of broken `TableOptions.Create()` fluent chain

## Files NOT Changed
- `workspace/runs/*/generated/**/Program.cs` — workspace files remain as-is (used as reference)
- `pipeline/contracts/*.json` — contracts already correct

## Change Summary
All 7 durable fixes are in generator source code and family config files (5 from Pass 1, 2 new in Pass 2).
New test file: `tests/unit/test_durable_fixes.py` (35 tests total, new in this sprint).
A clean generation run with `template_first: true` per_type_constraints will produce
the correct code without any workspace-level patches.
