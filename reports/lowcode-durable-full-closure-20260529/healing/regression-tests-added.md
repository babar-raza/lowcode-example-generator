# Regression Tests Added

## Tests Added in Lane 7

The following regression tests are added in `tests/` in Lane 7:

### `test_durable_fixes.py` (new file)
- `TestDiagramDeterministicTemplate::test_diagram_converter_uses_draw_ellipse`
- `TestDiagramDeterministicTemplate::test_pdf_converter_uses_draw_ellipse`
- `TestDiagramDeterministicTemplate::test_diagram_converter_no_typeval_shape`
- `TestDiagramDeterministicTemplate::test_xform_uses_value_property`
- `TestCellsDeterministicTemplate::test_spreadsheet_merger_uses_file_copy`
- `TestCellsDeterministicTemplate::test_spreadsheet_merger_no_workbook_create`
- `TestWordsDeterministicTemplate::test_merger_uses_file_copy`
- `TestWordsDeterministicTemplate::test_merger_no_merger_create`
- `TestWordsDeterministicTemplate::test_watermarker_uses_bmp_bytes`
- `TestWordsDeterministicTemplate::test_watermarker_no_sample_path`
- `TestTemplateFirstConfig::test_diagram_yml_has_template_first_for_diagramconverter`
- `TestTemplateFirstConfig::test_diagram_yml_has_template_first_for_pdfconverter`
- `TestTemplateFirstConfig::test_cells_yml_has_template_first_for_spreadsheetmerger`
- `TestTemplateFirstConfig::test_words_yml_has_template_first_for_merger`
- `TestTemplateFirstConfig::test_words_yml_has_template_first_for_watermarker`

### `test_gate_semantics.py` (new/updated)
- Tests for gate_generation must be passed before PR_DRY_RUN_READY
- Tests for all_required_passed must be true before acceptance
