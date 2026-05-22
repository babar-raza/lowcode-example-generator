# Sprint 65 — Special-Case Publication Placement Proof

Generated: 2026-05-22
Sprint: sprint65-publication-truth-repair-root-readme-strict-audit-handoff

## Overview

Two PDF scenarios require special-case handling because they were generated during
PDF pilot runs rather than the standard dry-run pipeline. Both have verified package
artifacts in `reports/sprint64/destination-packages/special-cases/`.

---

## Case 1: pdf-pdfa-converter

### Canonical Scenario ID
`pdf-pdfa-converter`

### Why Special Case
Generated during `workspace/runs/pilot-pdf-20260514-211320/`. Not part of standard
`workspace/pr-dry-run/` pipeline due to Sprint 57 naming discrepancy:
scenario_id=`pdf-pdfa-converter` but directory was named `pdf-pdf-aconverter`.

### Destination Repo
`aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples`

### Destination Path
`examples/pdf/lowcode/pdfa-converter`

**Proof**: `DestinationIdMapper.scenario_id_to_dir_name('pdf-pdfa-converter', 'pdf')` → `pdfa-converter`
Resolved path: `examples/{family}/lowcode/{dir_name}` = `examples/pdf/lowcode/pdfa-converter`

### Package Artifact Path
`reports/sprint64/destination-packages/special-cases/pdf-pdf-aconverter/`

### Files Present
| File | SHA256 (first 16) | Size |
|------|-------------------|------|
| Program.cs | `516ba44c470ff8ff...` | 1639 bytes |
| README.md | `2480ee6f814e5464...` | 250 bytes |
| pdf-pdf-aconverter.csproj | `c5c97f3bfc9e2984...` | 329 bytes |

### Package Version
`26.4.0` — Status: `POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED`
(Policy: Aspose.PDF calendar version bump 26.4.0→26.5.0; not regenerated per Sprint 65 Phase 4 decision)

### README I/O Section Proof
README.md contains section `## Input and Output`:
> "The example takes a PDF file (`input.pdf`) as input.
> The converted PDF/A-compliant document is saved as `output.pdf`."
Status: `IO_DOC` ✓

### Program.cs I/O Semantics Proof
```csharp
// Input: AddInput(new FileDataSource(inputPath))   — .pdf
// API:   new PdfAConverter().Process(options)
// Output: AddOutput(new FileDataSource(outputPath)) — .pdf (PDF/A-compliant)
```
Using statement present: `using Aspose.Pdf.LowCode;`
Type: `Aspose.Pdf.LowCode.PdfAConverter` ✓

### Root README Index Entry
Expected entry in destination repo root README:
```
| PdfAConverter | [pdfa-converter](examples/pdf/lowcode/pdfa-converter/README.md) | PDF to PDF/A conversion | Aspose.PDF 26.5.0 |
```

### Publication Placement Verdict
`SPECIAL_CASE_READY` — All files present, I/O documented, placement path verified.

---

## Case 2: pdf-text-extractor

### Canonical Scenario ID
`pdf-text-extractor`

### Why Special Case
`TextExtractor` uses `ResultCollection` output pattern — no `AddOutput()` call.
Output is extracted text read from `ResultCollection[0]` as `StringResult`. No output
file is produced. This violates the standard `AddInput/AddOutput` pattern used by all
other 40 scenarios.

### Destination Repo
`aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples`

### Destination Path
`examples/pdf/lowcode/text-extractor`

**Proof**: `DestinationIdMapper.scenario_id_to_dir_name('pdf-text-extractor', 'pdf')` → `text-extractor`
`DestinationIdMapper.is_result_collection_output('pdf-text-extractor')` → `True`
Resolved path: `examples/{family}/lowcode/{dir_name}` = `examples/pdf/lowcode/text-extractor`

### Package Artifact Path
`reports/sprint64/destination-packages/special-cases/pdf-text-extractor/`

### Files Present
| File | SHA256 (first 16) | Size |
|------|-------------------|------|
| Program.cs | `c3164aad41c1bad1...` | 1205 bytes |
| README.md | `2fd996a147057877...` | 206 bytes |
| pdf-text-extractor.csproj | `c5c97f3bfc9e2984...` | 329 bytes |

### Package Version
`26.4.0` — Status: `POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED`

### README I/O Section Proof
README.md contains section `## Input and Output`:
> "The example takes a PDF file (`input.pdf`) as input.
> The extracted text is printed to standard output (no output file is created)."
Status: `IO_DOC` ✓

### Program.cs I/O Semantics Proof
```csharp
// Input:  options.AddInput(new FileDataSource(inputPath))  — .pdf
// API:    var result = new TextExtractor().Process(options)
// Output: result[0] read as ResultType.Text (StringResult) — stdout
// NOTE:   No AddOutput() — ResultCollection pattern
```
Using statement present: `using Aspose.Pdf.LowCode;`
Type: `Aspose.Pdf.LowCode.TextExtractor` ✓
`is_result_collection_output` flag: `True` ✓

### Root README Index Entry
Expected entry in destination repo root README:
```
| TextExtractor | [text-extractor](examples/pdf/lowcode/text-extractor/README.md) | PDF Text Extraction | Aspose.PDF 26.5.0 |
```

### Publication Placement Verdict
`SPECIAL_CASE_READY` — All files present, I/O documented, placement path verified, ResultCollection pattern confirmed.

---

## Summary

| Scenario ID | Destination Path | Files | README I/O | Program.cs | Placement |
|-------------|-----------------|-------|-----------|-----------|---------|
| pdf-pdfa-converter | examples/pdf/lowcode/pdfa-converter | 3/3 | IO_DOC | MATCH | VERIFIED |
| pdf-text-extractor | examples/pdf/lowcode/text-extractor | 3/3 | IO_DOC | MATCH (ResultCollection) | VERIFIED |

Both special cases: `SPECIAL_CASE_READY`

Sprint 64 defect S64-D6 (special cases lack destination repo path/placement proof): **CLOSED**
