# Manual Family Analysis: psd
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/psd/ (4 canonical pages) + ConvertPsdToJpg.cs

### Implementation Model: LOAD_SAVE_OPTIONS
PSD uses `Image.Load()` → `PsdImage.Save()` pattern. Same LOAD_SAVE_OPTIONS as Imaging.

### API Pattern
```csharp
using (var psdImage = (PsdImage)Image.Load(inputFile)) {
    psdImage.Save(outputFile, new JpegOptions() { Quality = 80 });
}
// OR for PNG:
    psdImage.Save(outputFile, new PngOptions());
```

### 4 Canonical Pages
- image-converter — PSD → PNG/JPEG/PDF (LOAD_SAVE_OPTIONS)
- graphics-editor — edit PSD layers, add text, shapes (DOCUMENT_OBJECT_MODEL_WORKFLOW)
- animation-maker — PSD TimeLine → GIF (LOAD_SAVE_OPTIONS, fixture-heavy)
- photo-processor — batch PSD processing (LOAD_SAVE_OPTIONS)

### Fixture Requirements
- image-converter: requires a .psd file fixture
- animation-maker: requires PSD with TimeLine layers
- photo-processor: requires .psd files

### Transformation Priority: MEDIUM
- image-converter is simplest; can create minimal PSD programmatically or use bundled test PSD
- Official source confirmed: ConvertPsdToJpg.cs
