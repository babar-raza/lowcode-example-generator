# Manual Family Analysis: svg
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/svg/ (5 canonical pages) + ConvertSVGToImage.cs

### Implementation Model: STATIC_CONVERTER_CLASS
SVG uses `Converter.ConvertSVG()` static method pattern. Same STATIC_CONVERTER_CLASS as HTML.

### API Pattern
```csharp
// SVG to Image (PNG/JPEG/BMP)
using (var document = new SVGDocument(inputFile)) {
    var saveOptions = new ImageSaveOptions(ImageFormat.Png);
    Converter.ConvertSVG(document, saveOptions, outputFile);
}

// SVG to PDF
using (var document = new SVGDocument(inputFile)) {
    var saveOptions = new PdfSaveOptions();
    Converter.ConvertSVG(document, saveOptions, outputFile);
}

// Image to SVG (Vectorizer)
Converter.ConvertImageToSVG(inputFile, new ImageVectorizerConfiguration(), outputFile);
```

### 5 Canonical Pages
- svg-to-image-converter — SVG → PNG/JPEG/BMP/TIFF (STATIC_CONVERTER_CLASS, Converter.ConvertSVG + ImageSaveOptions)
- svg-to-pdf-converter — SVG → PDF (STATIC_CONVERTER_CLASS, Converter.ConvertSVG + PdfSaveOptions)
- vectorizer — image → SVG (STATIC_CONVERTER_CLASS, Converter.ConvertImageToSVG)
- convert-svg-to-png — old-slug entry, maps to svg-to-image-converter canonical
- convert-svg-to-jpg — old-slug entry, maps to svg-to-image-converter canonical

### Fixture Requirements
- svg-to-image-converter: requires an .svg file — can create minimal inline SVG string or embed in code
- svg-to-pdf-converter: same minimal .svg fixture
- vectorizer: requires a raster image (PNG/JPEG) as input

### Transformation Priority: HIGH
- svg-to-image-converter and svg-to-pdf-converter are trivial: inline SVG string, no external file needed
- Converter.ConvertSVG() is a one-liner; ideal for dry-run
- Official source confirmed: ConvertSVGToImage.cs in aspose-svg/Aspose.SVG-for-.NET
