# Next Sprint Ready Prompt

## Sprint: lowcode-plugin-code-registry-20260604
## Prepared: 2026-06-04

---

## Context for Next Sprint Agent

You are starting the **example transformation sprint** for non-LowCode Aspose plugin families.

The previous sprint (`lowcode-plugin-code-registry-20260604`) completed:
1. Plugin-code registry created with 65 entries (18 families)
2. Official GitHub code harvested for 53/65 plugins
3. 3 snippets validated (barcode-generate-barcode, barcode-recognize-barcode, imaging-convert-image)
4. First 10 transformation candidates identified with full evidence

## Do NOT Redo

Do NOT redo:
- Sitemap crawl (CRAWL_BLOCKED, already documented)
- GitHub repo tree fetch (already in .local/code-cache/repo-trees/)
- Code harvest (already in .local/code-cache/{family}/{plugin}/)
- Manual family analysis (already in reports/.../manual-analysis/family/{family}.md)
- Registry population (already in pipeline/plugin-code-registry/family/{family}.yaml)

## Your Task

Transform the first 10 plugins into runnable examples. Use:

1. **Code authority**: `.local/code-cache/{family}/{plugin_slug}/*.cs`
2. **Registry**: `pipeline/plugin-code-registry/family/{family}.yaml`
3. **Transformation plan**: `reports/lowcode-plugin-code-registry-20260604/transformation/first-10-plugin-candidate-matrix.json`
4. **Transformation skill**: `skills/plugin-code-to-example-transformation.md`

## First 3 (No Fixture Required)

Start with these — no input fixtures needed:

1. **barcode/generate-barcode** — `BarcodeGenerator gen = new BarcodeGenerator(EncodeTypes.Code128, "12345678"); gen.Save("output.png", BarCodeImageFormat.Png);`
2. **barcode/generate-qr-code** — same pattern, EncodeTypes.QR
3. **drawing/create-drawing** — `new Bitmap(800, 600)` + `Graphics.FromImage(bmp)` + `g.DrawArc(...)` + `bmp.Save()`

## Next 4 (Simple Fixture)

4. **imaging/convert-image** — needs input.jpg
5. **imaging/resize-image** — needs input.jpg
6. **zip/compress-files** — needs file1.txt, file2.txt
7. **tasks/convert-mpp-to-pdf** — programmatic `new Project()` works (no MPP needed)

## Hard Constraints

1. No publication PRs
2. No external repo mutations
3. Do not modify existing 44 LowCode examples
4. Do not modify protected family YAMLs
5. If official API fails, record failure — do NOT substitute silently

## Evidence Required

For each transformed example:
- validation/snippets/{family}-{plugin}/original-code.cs
- validation/snippets/{family}-{plugin}/diff-from-official-snippet.md
- validation/snippets/{family}-{plugin}/build.log
- validation/snippets/{family}-{plugin}/run.log
- validation/snippets/{family}-{plugin}/final-verdict.md

Update registry entry to TRANSFORMED_TO_EXAMPLE when done.
