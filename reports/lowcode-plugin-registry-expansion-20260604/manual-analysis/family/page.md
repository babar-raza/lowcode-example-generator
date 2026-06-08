# Manual Family Analysis: page
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/page/ (3 canonical pages) + GitHub repo

### Implementation Model: DEDICATED_PLUGIN_CLASS
Page uses dedicated converter plugin classes: `PsConverter`, `XpsConverter`, `EpsConverter`.
Pattern: instantiate plugin → configure options → call `.Process()`.

### API Pattern
```csharp
// PS to PDF
var converter = new PsConverter();
var options = new PsConverterToPdfOptions();
options.AddInputDataSource(new FileDataSource(inputPs));
options.AddOutputDataTarget(new FileDataTarget(outputPdf));
converter.Process(options);

// XPS to PDF
var converter = new XpsConverter();
var options = new XpsConverterToPdfOptions();
options.AddInputDataSource(new FileDataSource(inputXps));
options.AddOutputDataTarget(new FileDataTarget(outputPdf));
converter.Process(options);
```

### 3 Canonical Pages
- ps-converter — PS → PDF/Image (DEDICATED_PLUGIN_CLASS, PsConverter.Process())
- xps-converter — XPS → PDF/Image (DEDICATED_PLUGIN_CLASS, XpsConverter.Process())
- convert-eps-to-pdf — EPS → PDF (DEDICATED_PLUGIN_CLASS, PsDocument or EpsConverter)

### Fixture Requirements
- ps-converter: requires a .ps file — minimal PostScript can be embedded as a literal string or generated
- xps-converter: requires a .xps file — can generate minimal XPS programmatically via XpsDocument
- convert-eps-to-pdf: requires a .eps file

### Transformation Priority: MEDIUM
- PS and XPS converters both confirmed DEDICATED_PLUGIN_CLASS with Process() pattern
- Fixture complexity: .ps and .xps files are harder to generate programmatically vs. imaging families
- Recommended approach: bundle minimal test fixtures (even a 1-page blank .xps)
- READY_FOR_TRANSFORMATION entries: ps-converter, xps-converter
