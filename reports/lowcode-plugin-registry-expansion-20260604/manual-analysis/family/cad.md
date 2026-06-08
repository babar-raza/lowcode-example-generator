# Manual Family Analysis: cad
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/cad/ + GitHub repo aspose-cad/Aspose.CAD-for-.NET

### Implementation Model: LOAD_SAVE_OPTIONS
CAD uses `Image.Load()` → `image.Save()` pattern with CAD-specific save options.
Same LOAD_SAVE_OPTIONS as Imaging, but input is a CAD file (DWG/DXF/DGN).

### API Pattern
```csharp
// CAD to PDF
using (var image = Image.Load(inputCadFile)) {
    var pdfOptions = new PdfOptions();
    image.Save(outputPdf, pdfOptions);
}

// CAD to Image (PNG/JPEG/BMP)
using (var image = Image.Load(inputDwgFile)) {
    var rasterOptions = new CadRasterizationOptions {
        PageWidth = 1200,
        PageHeight = 1200
    };
    var pngOptions = new PngOptions { VectorRasterizationOptions = rasterOptions };
    image.Save(outputPng, pngOptions);
}
```

### 5 Plugin Entries
- convert-cad-to-pdf — CAD/DGN → PDF (LOAD_SAVE_OPTIONS, Image.Load + PdfOptions)
- convert-dwg-to-pdf — DWG → PDF (LOAD_SAVE_OPTIONS)
- convert-dxf-to-pdf — DXF → PDF (LOAD_SAVE_OPTIONS)
- convert-cad-to-image — CAD/DWG → PNG/JPEG/BMP (LOAD_SAVE_OPTIONS, CadRasterizationOptions)
- convert-dwg-to-jpg — DWG → JPEG (LOAD_SAVE_OPTIONS, NEEDS_MANUAL_MAPPING)

### Fixture Requirements
- All entries require a CAD file fixture (DWG/DXF/DGN)
- CAD files CANNOT be generated programmatically without the library itself
- Fixture dependency is the primary blocker for dry-run packages in this family
- Mitigation: bundle a minimal test DWG/DXF from the official GitHub examples repo

### Transformation Priority: LOW
- Fixture dependency (CAD file) is unavoidable
- No canonical URL confirmed for most entries — still at CODE_HARVESTED
- Recommend deferring dry-run packages until a bundled minimal test DWG fixture is available
- convert-cad-to-pdf is the simplest candidate once fixture is available
