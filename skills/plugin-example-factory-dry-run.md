# Skill: plugin-example-factory-dry-run

## Purpose
Build dry-run example packages for Aspose plugin APIs from registry entries.

## When to Use
- A plugin has `READY_FOR_TRANSFORMATION` or `CODE_HARVESTED` registry status
- A canonical URL is confirmed
- A NuGet package + version is known

## Core Steps

### 1. Identify Target Packages
```python
# Registry loader
from plugin_examples.plugin_code_registry.loader import PluginCodeRegistryLoader
loader = PluginCodeRegistryLoader("pipeline/plugin-code-registry/family")
ready = loader.active_entries()  # READY + TRANSFORMED + CANDIDATE
```

### 2. Probe API if Needed
For unknown APIs, use dotnet reflection:
```bash
dotnet new console -n probe --no-restore
# Add PackageReference in .csproj, then:
dotnet restore && dotnet run
```
Key probes:
- Check constructor signatures
- Check method signatures (especially `Save()` overloads)
- Check SaveFormat enum values
- Check correct namespace (e.g., Aspose.Drawing uses System.Drawing namespace)

### 3. Write Program.cs
Pattern: Inline fixture → API call → output file

Key patterns by family:
- **ZIP**: `new Archive() -> CreateEntry(name, memoryStream) -> Save(path)`
- **OCR**: `new AsposeOcr() -> OcrInput(SingleImage) -> input.Add(path) -> Recognize(input) -> RecognitionText`
- **Drawing**: Uses `System.Drawing` namespace (not `Aspose.Drawing`)
- **Note**: `new Document() -> new Page() -> new Outline() -> new RichText { Text=..., ParagraphStyle=ParagraphStyle.Default }`
- **GIS**: `VectorLayer.Open(path, Drivers.GeoJson) -> feature.GetValue<T>(attr)` (wrap in try-catch)
- **Finance**: `new XbrlDocument(path) -> Save(out, new SaveOptions { SaveFormat = SaveFormat.IXBRL })`
- **Page XPS**: `new XpsDocument() -> AddPath -> SaveAsPdf(path, PdfSaveOptions)`
- **Page PS**: `new PsDocument(psStream) -> SaveAsPdf(pdfStream, PdfSaveOptions)`
- **HTML→PDF**: `Converter.ConvertHTML(content, ".", PdfSaveOptions, path)`
- **SVG→Image**: `SVGDocument(svg, ".") -> Converter.ConvertSVG(doc, ImageSaveOptions(PNG), path)`
- **Barcode gen**: `new BarcodeGenerator(EncodeTypes.Code128, value) -> Save(path, BarCodeImageFormat.Png)`
- **Barcode read**: Generate first, then `new BarCodeReader(path, DecodeType.Code128) -> ReadBarCodes()`
- **Tasks (MPP)**: `new Project() -> task.Set(Tsk.Name, ...) -> Save(path, SaveFileFormat.Pdf)`
- **Tasks Excel**: `new Project() -> Save(path, new XlsxOptions())`
- **Tasks HTML**: `new Project() -> Save(path, new HtmlSaveOptions())`
- **Tasks PNG**: `new Project() -> Save(path, new ImageSaveOptions(SaveFileFormat.Png))` (PascalCase `Png`)
- **HTML→Word**: `Converter.ConvertHTML(content, ".", new DocSaveOptions(), path)`
- **HTML→Image**: `Converter.ConvertHTML(content, ".", new ImageSaveOptions(ImageFormat.Jpeg), path)`
- **Page EPS→PDF**: Same as PS — `new PsDocument(epsStream) -> SaveAsPdf(pdfStream, PdfSaveOptions)`
- **PSD create**: `new PsdImage(w,h) -> graphics.Clear(Color.X) -> Save(path)` + explicit `Aspose.Drawing 24.12.0` dep
- **PSD→JPEG**: `(PsdImage)Image.Load(psdPath) -> Save(outPath, new JpegOptions { Quality = 90 })`
- **PSD→PDF**: `Image.Load(psdPath) -> Save(outPath, new PdfOptions())`
- **SVG vectorizer**: `new ImageVectorizer { Configuration = new ImageVectorizerConfiguration { ColorsLimit=4, LineWidth=1.0f } } -> Vectorize(pngPath) -> Save(svgPath)`
- **TeX→XPS**: `TeXOptions.ConsoleAppOptions(TeXConfig.ObjectLaTeX) + TeXJob("job", new XpsDevice(), opts).Run()` — PdfDevice throws XpsSaveOptions cast in 24.12.0
- **Imaging**: `new BmpImage(w, h) -> Draw(shapes) -> Save(path, PngOptions)`

### 4. Required Package Files
```
{family}/{slug}/
  Program.cs
  {family}-{slug}.csproj
  README.md
  source-provenance.json    (with canonical_url)
  package-manifest.json
  output-validation.json
  restore.log               (in root, not logs/ subdirectory)
  build.log
  run.log
  output/
    {output_file}
```

### 5. Validate
```python
from plugin_examples.fixture_factory.package_invariants import check_package
from plugin_examples.fixture_factory.validators import validate_package_outputs

violations = check_package(pkg_dir)
real_v = [v for v in violations if 'INV-11' not in v]  # INV-11 (bin/) is expected
pub_result = validate_package_outputs(pkg_dir, key)
```

### 6. Common Errors and Fixes

| Error | Fix |
|-------|-----|
| `using Aspose.Drawing;` not found | Use `using System.Drawing;` — Aspose.Drawing IS System.Drawing |
| Note `Page(doc)` constructor not found | Use `new Page()` (parameterless) |
| Note `RichText` NullReferenceException on Save | Add `ParagraphStyle = ParagraphStyle.Default` |
| Finance `SaveOptions.IXbrlSaveOptions` not found | Use `new SaveOptions { SaveFormat = SaveFormat.IXBRL }` |
| GIS `GetValue<T>` throws InvalidOperationException | Wrap in try-catch; attribute may not be set |
| source-provenance.json has `{{` and `}}` | Use `.replace()` properly; `{{` in Python f-strings = literal `{` |
| `INV-08/09/10` logs missing | Logs must be in package ROOT, not `logs/` subdirectory |
| JPEG signature check fails | Check 3 bytes `b"\xff\xd8\xff"` not 2 bytes |
| `SaveFormat.Docx` CS0117 in Aspose.Note | Note has no Word format; use `SaveFormat.Html` (Word-compatible) |
| `SaveFileFormat.PNG` CS0117 in Aspose.Tasks | Use `SaveFileFormat.Png` (PascalCase, not acronym) |
| Aspose.PSD `Could not load Aspose.Drawing` | Add `<PackageReference Include="Aspose.Drawing" Version="24.12.0" />` explicitly |
| Aspose.TeX PdfDevice `InvalidCastException XpsSaveOptions→PdfSaveOptions` | Use `new XpsDevice()` instead of `new PdfDevice()` (bug in 24.12.0) |
| EPS string `CS1010 Newline in constant` | Use `string[] epsLines = {...}; string.Join("\\n", epsLines)` |
| SVG `LineWidth = 1.0` CS0664 | Use `LineWidth = 1.0f` (float literal) |

### 7. Advance Registry Entry
```python
plugin['registry_status'] = 'TRANSFORMED_TO_EXAMPLE_DRYRUN'
plugin['canonical_url'] = 'https://products.aspose.net/...'
plugin['history'].append({'date': DATE, 'status': 'TRANSFORMED_TO_EXAMPLE_DRYRUN', 'analyst_notes': '...'})
```

## Fixture Generators Available
```python
from plugin_examples.fixture_factory.generators import (
    generate_minimal_png,      # PNG
    generate_bmp_fixture,      # BMP
    generate_svg_fixture,      # SVG
    generate_html_fixture,     # HTML
    generate_zip_fixture,      # ZIP
    generate_geojson_fixture,  # GeoJSON FeatureCollection
    generate_obj_fixture,      # Wavefront OBJ (3D cube)
    generate_xbrl_fixture,     # XBRL instance document
    generate_ps_fixture,       # PostScript document
    generate_note_xml_fixture, # OneNote XML
    generate_drawing_xml_fixture,  # Visio XML
    # Wave 6 additions:
    generate_eps_fixture,          # EPS (Encapsulated PostScript)
    generate_psd_fixture,          # PSD binary (Photoshop, minimal)
    generate_rich_geojson_fixture, # GeoJSON with 5 features, mixed geometry
    generate_latex_fixture,        # LaTeX source (.tex file)
)
```

## Evidence Requirements
Each wave must produce:
- `wave{N}-build-results.json` — all verdicts PASS
- `invariant-results.json` — 0 real violations (INV-11 bin/ expected)
- Updated cumulative-dryrun-ledger.json
- Publication matrix JSON

## Closeout Consistency Check
```python
from plugin_examples.fixture_factory.closeout_validators import run_all_consistency_checks
result = run_all_consistency_checks(report_root, registry_transformed_count=30)
assert result.passed, [v.description for v in result.violations]
```
