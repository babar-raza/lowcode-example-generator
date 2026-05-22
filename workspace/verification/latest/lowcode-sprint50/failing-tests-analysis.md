# Failing Tests Analysis — Sprint 50

## Sprint 49 Failures: 6 → Current: 0

All 6 failures were fixed by commit `5e66c8b` (format-authority work).

| Test | Classification | Fixed In |
|------|---------------|----------|
| test_output_format_correct[cells:SpreadsheetConverter] | pre_existing_fixed | 5e66c8b |
| test_output_format_correct[pdf:FormExporter] | pre_existing_fixed | 5e66c8b |
| test_output_format_correct[email:Converter] | pre_existing_fixed | 5e66c8b |
| test_input_format_correct[cells:TextConverter] | pre_existing_fixed | 5e66c8b |
| test_cells_spreadsheet_converter | pre_existing_fixed | 5e66c8b |
| test_text_converter_scenario_uses_csv | renamed/replaced | 5e66c8b |

Proof: 85/85 format tests pass (see failing-tests-rerun-log.txt)
