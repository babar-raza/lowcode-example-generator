# Fixture Copy Policy — Multi-Input Merger Examples

## Policy
For merger-type examples that require multiple input files:
- The pipeline provides one input fixture file (e.g. input.xlsx or input.docx)
- The generated Program.cs must copy this fixture to create input1/input2
- Use: `File.Copy(inputPath, input1Path, overwrite: true)`
- This is self-contained — no external fixture dependency

## Rationale
- The fixture file is copied to two distinct paths in AppContext.BaseDirectory
- The merger API then merges these two copies
- This pattern is valid because the merger's purpose is to combine multiple files
- Using File.Copy from an existing fixture avoids null-input errors and is build/runtime verified

## Families Applied
- cells: SpreadsheetMerger (SpreadsheetMerger.Process(new string[]{input1, input2}, output))
- words: Merger (Merger.Merge(output, new string[]{input1, input2}))

## Alternative (NOT used for merger)
For non-merger types, programmatic creation is used:
- cells: new Workbook(); workbook.Save("input.xlsx")
- words: new Document() + DocumentBuilder + doc.Save("input.docx")
