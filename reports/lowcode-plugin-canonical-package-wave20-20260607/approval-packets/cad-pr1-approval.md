# CAD PR #1 — Approval Packet

**PR URL:** https://github.com/aspose-cad-net/Aspose.CAD.Plugins-for-.NET-Examples/pull/1
**Branch:** lowcode/wave19/cad-plugin-examples
**Status:** OPEN, MERGEABLE, no CI failures

## What Changed
5 Aspose.CAD plugin example packages added:
- `cad/convert-cad-to-image` — converts CAD file to image using CadRasterizationOptions + JpegOptions
- `cad/convert-cad-to-pdf` — converts CAD file to PDF using PdfOptions
- `cad/convert-dxf-to-pdf` — converts ASCII DXF R12 to PDF (hand-crafted test fixture)
- `cad/convert-dwg-to-pdf` — converts DWG to PDF (Drawing11.dwg, 43288B output)
- `cad/convert-dwg-to-jpg` — converts DWG to JPG (Drawing11.dwg, 77073B output)

## Validation Summary
- All 5 packages: EXIT=0, output files produced, output-validation.json present
- NuGet: Aspose.CAD 24.12.0
- Target framework: net8.0
- DWG fixture: Drawing11.dwg (19378B) from github.com/aspose-cad/Aspose.CAD-for-.NET (official Aspose repo, public sample)
- Provenance: documented in dwg-fixture-provenance.json (W19 evidence)

## Known Risks
- Evaluation watermark appears in output images/PDFs in unlicensed builds (expected)
- DWG fixture is a public Aspose sample (safe to include in examples repo)

## Merge Recommendation
**APPROVE AND MERGE** — All 5 examples are buildable, correct, and documented.
