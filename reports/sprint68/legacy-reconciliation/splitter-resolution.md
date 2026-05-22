# Splitter Output Cardinality Resolution — Sprint 68

Date: 2026-05-22

## Background

Sprint 67 defect S67-D2: Three splitter types have `output_cardinality=multi` in format authority
contracts but Program.cs examples use single-output patterns.

## API Investigation

### Cells — SpreadsheetSplitter

Contract: `output_cardinality: "multi"`
Program.cs: `SpreadsheetSplitter.Process(inputPath, outputPath)` — single output path

The two-string overload `Process(string inputFile, string outputFile)` is a valid API method
that processes the input and writes to a single output file. This is single-file extraction.
Multi-file splitting requires `Process(LowCodeLoadOptions, LowCodeSaveOptions)` with multiple
output targets configured in `LowCodeSaveOptions`.

**Resolution**: SINGLE_OUTPUT_VALID. The Program.cs demonstrates the simplest valid API usage.

### Words — Splitter

Contract: `output_cardinality: "multi"`
Program.cs: `Splitter.ExtractPages(inputPath, outputPath, startPageIndex: 0, pageCount: 1)`

`ExtractPages` is a page-range extraction method. It extracts `pageCount` pages starting at
`startPageIndex` and writes them to a single output file. This is not a full document split;
it is page extraction — a fundamentally single-output operation regardless of contract capability.

The `output_cardinality=multi` in the contract describes the Splitter class's maximum capability
(splitting each page into a separate file). `ExtractPages` with one output is canonical for
demonstrating page extraction functionality.

**Resolution**: SINGLE_OUTPUT_VALID. `ExtractPages` is single-output by API design.

### PDF — Splitter

Contract: `output_cardinality: "multi"`
Program.cs: `options.AddOutput(new FileDataSource(outputPath))` — one AddOutput call

The PDF `Splitter` plugin accepts multiple `AddOutput` calls for full multi-file splitting.
The Program.cs calls `AddOutput` once, producing a single output file (first-page extraction).
This is valid — `SplitOptions` does not require multiple outputs.

**Resolution**: SINGLE_OUTPUT_VALID. Single `AddOutput` produces valid single-file output.

## Contract Field Semantics

`output_cardinality` in the format authority contracts describes **maximum API capability**,
not a minimum or required output count for examples. All three splitter APIs can produce
multiple output files, but single-output usage is valid and demonstrable.

This is consistent with how `input_artifacts[0].cardinality=single` is used — it describes
the typical/minimum input, not the only possible input.

## Decision

**No Program.cs regeneration required.**

All three splitter examples are correct. The sprint67 handoff Program.cs files are carried
forward to sprint68 unchanged. The sprint67 reconciliation-index.md omitted this per-type
analysis — this document closes that gap explicitly.

## Cardinality Contract Notes Added

Per-type notes added to `cardinality-reconciliation-final.json`:
- cells/SpreadsheetSplitter: single-output extraction valid, contract multi = capability
- words/Splitter: ExtractPages is single-output by API design
- pdf/Splitter: single AddOutput is valid, contract multi = capability
