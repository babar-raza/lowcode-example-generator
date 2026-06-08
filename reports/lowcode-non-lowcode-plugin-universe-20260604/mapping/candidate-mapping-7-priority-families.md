# Candidate Mapping — 7 Priority Families

Generated: 2026-06-04T00:00:00Z
Reflection source: reports/lowcode-non-lowcode-plugin-universe-20260604/reflection/public-api-inventory/

This document maps plugin operations to confirmed API types and methods for the 7 priority families.

---

## Mapping Status Legend

| symbol | meaning |
|--------|---------|
| ✓ PROBE_CONFIRMED | Full probe completed; output validated |
| ◎ REFLECTION_CANDIDATE | DllReflector confirmed; probe not yet run |
| ○ WEBSITE_DISCOVERED | Package available; reflection deferred |
| ✗ BLOCKED | External blocker; classified |

---

## Family 1: Aspose.BarCode (barcode)

**Package**: Aspose.BarCode v26.5.0 | **Reflection**: COMPLETE (165 types)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| generate-barcode | `BarcodeGenerator` | `.Save(path, BarCodeImageFormat)` | ✓ PROBE_CONFIRMED | output-validation.json |
| generate-qr-code | `BarcodeGenerator` | `.Save(path, BarCodeImageFormat.Png)` | ◎ REFLECTION_CANDIDATE | BarcodeGenerator confirmed |
| recognize-barcode | `BarCodeReader` | `.ReadBarCodes()` | ◎ REFLECTION_CANDIDATE | BarCodeReader confirmed |
| read-barcode | `BarCodeReader` | `.ReadBarCodes()` | ◎ REFLECTION_CANDIDATE | synonym of recognize |
| scan-barcode | `BarCodeReader` | `.ReadBarCodes()` | ◎ REFLECTION_CANDIDATE | synonym of read |

**Primary example selected**: `generate-barcode` → `BarcodeGenerator(EncodeTypes.Code128, text).Save(path, BarCodeImageFormat.Png)`

---

## Family 2: Aspose.Imaging (imaging)

**Package**: Aspose.Imaging v26.6.0 | **Reflection**: COMPLETE (prior sprint)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| convert-image | `Image` | `.Load(path).Save(path, options)` | ✓ PROBE_CONFIRMED | output-validation.json |
| resize-image | `Image` | `.Resize(w, h, ResizeType)` | ◎ REFLECTION_CANDIDATE | Image confirmed |
| compress-image | `Image` | `.Save(path, JpegOptions{Quality})` | ◎ REFLECTION_CANDIDATE | — |
| crop-image | `Image` | `.Crop(Rectangle)` | ◎ REFLECTION_CANDIDATE | — |
| rotate-image | `Image` | `.Rotate(degrees)` | ◎ REFLECTION_CANDIDATE | — |
| watermark-image | `Graphics` | `.DrawString(text, ...)` | ◎ REFLECTION_CANDIDATE | — |
| merge-images | `Image.Create()` | multiple sources → save | ◎ REFLECTION_CANDIDATE | — |
| filter-image | `Image` | custom filter pipeline | ◎ REFLECTION_CANDIDATE | — |

**Primary example selected**: `convert-image` → `Image.Load(src).Save(dest, JpegOptions())`

---

## Family 3: Aspose.ZIP (zip)

**Package**: Aspose.ZIP v26.5.0 | **Reflection**: COMPLETE (151 types)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| compress-files | `Archive` | `.CreateEntry(name, data).Save(path)` | ✓ PROBE_CONFIRMED | output-validation.json |
| extract-files | `Archive` | `.ExtractToDirectory(path)` | ◎ REFLECTION_CANDIDATE | Archive confirmed |
| create-archive | `Archive` | `.Save(stream)` | ◎ REFLECTION_CANDIDATE | — |
| compress-folder | `Archive` | `.CreateEntries(dirPath).Save()` | ◎ REFLECTION_CANDIDATE | — |

**Primary example selected**: `compress-files` → `Archive a = new(); a.CreateEntry("file.txt", data); a.Save(dest)`

### ZIP API Details (from DllReflector)

```
Aspose.Zip.Archive:
  CreateEntry(string, Stream), CreateEntry(string, FileInfo), CreateEntry(string, byte[])
  CreateEntries(string directoryPath), CreateEntries(DirectoryInfo)
  ExtractToDirectory(string), Save(Stream), Save(string)
```

---

## Family 4: Aspose.Tasks (tasks)

**Package**: Aspose.Tasks v26.5.0 | **Reflection**: COMPLETE (367 types)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| convert-mpp-to-pdf | `Project` | `.Save(path, SaveFileFormat.Pdf)` | ◎ REFLECTION_CANDIDATE | Project.Save confirmed |
| convert-mpp-to-excel | `Project` | `.Save(path, SaveFileFormat.Xlsx)` | ◎ REFLECTION_CANDIDATE | — |
| convert-mpp-to-html | `Project` | `.Save(path, SaveFileFormat.Html)` | ◎ REFLECTION_CANDIDATE | — |
| convert-mpp-to-image | `Project` | `.Save(path, ImageSaveOptions)` | ◎ REFLECTION_CANDIDATE | — |
| read-project-data | `Project` | `new Project(filePath)` → iterate | ◎ REFLECTION_CANDIDATE | — |

**Primary example selected**: `convert-mpp-to-pdf` → `new Project(mppFile).Save(pdfPath, SaveFileFormat.Pdf)`

### Tasks API Details (from DllReflector)

```
Aspose.Tasks.Project:
  Project(string filePath)
  Save(string filename, SaveFileFormat format)
  Save(string filename, SaveOptions options)
  Save(Stream stream, SaveFileFormat format)
Aspose.Tasks namespace: 367 types across 10 namespaces
```

---

## Family 5: Aspose.CAD (cad)

**Package**: Aspose.CAD v26.1.0 | **Reflection**: COMPLETE (5028 types)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| convert-cad-to-pdf | `Image` | `.Load(dwgPath).Save(pdfPath, PdfOptions)` | ◎ REFLECTION_CANDIDATE | Image.Load+Save confirmed |
| convert-dwg-to-pdf | `Image` | `.Load(dwgPath).Save(pdfPath, PdfOptions)` | ◎ REFLECTION_CANDIDATE | — |
| convert-dxf-to-pdf | `Image` | `.Load(dxfPath).Save(pdfPath, PdfOptions)` | ◎ REFLECTION_CANDIDATE | — |
| convert-cad-to-image | `Image` | `.Load(path).Save(imgPath, PngOptions)` | ◎ REFLECTION_CANDIDATE | — |
| convert-dwg-to-jpg | `Image` | `.Load(dwgPath).Save(jpgPath, JpegOptions)` | ◎ REFLECTION_CANDIDATE | — |

**Primary example selected**: `convert-cad-to-pdf`

### CAD API Details (from DllReflector)

```
Aspose.CAD.Image:
  Load(string filePath) → static, returns CadImage
  Save(string path) — no-arg
  Save(string path, ImageOptionsBase options)
  CanSave(ImageOptionsBase) → bool
Aspose.CAD namespace: 5028 types across 42 namespaces
```

---

## Family 6: Aspose.OCR (ocr)

**Package**: Aspose.OCR v26.5.0 | **Reflection**: DEFERRED (35.9MB DLL)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| recognize-text | `AsposeOcr` | `.RecognizeImage(filePath)` | ○ WEBSITE_DISCOVERED | AI_DRAFT — needs reflection |
| extract-text | `AsposeOcr` | `.RecognizeImage(filePath)` | ○ WEBSITE_DISCOVERED | — |
| scan-document | `AsposeOcr` | `.RecognizePage(filePath)` | ○ WEBSITE_DISCOVERED | — |

**Primary example**: deferred pending DllReflector with OCR-specific dependencies

---

## Family 7: Aspose.SVG (svg)

**Package**: Aspose.SVG v26.5.0 | **Reflection**: COMPLETE (591 types)

| plugin_slug | type | method | status | evidence |
|------------|------|--------|--------|---------|
| convert-svg-to-pdf | `Converter` | `.ConvertSVG(url, options, output)` | ◎ REFLECTION_CANDIDATE | Converter confirmed |
| convert-svg-to-png | `Converter` | `.ConvertSVG(url, ImageRenderingOptions, output)` | ◎ REFLECTION_CANDIDATE | — |
| convert-svg-to-jpg | `Converter` | `.ConvertSVG(url, ImageRenderingOptions, output)` | ◎ REFLECTION_CANDIDATE | — |
| merge-svg | `SVGDocument` | merge + renderer | ◎ REFLECTION_CANDIDATE | — |

**Primary example selected**: `convert-svg-to-pdf` or `convert-svg-to-png` (pending probe)

---

## Summary

| family | package | reflection | plugins_mapped | primary_status |
|--------|---------|-----------|---------------|---------------|
| barcode | Aspose.BarCode | COMPLETE | 5/5 | PROBE_CONFIRMED |
| imaging | Aspose.Imaging | COMPLETE (prior) | 8/8 | PROBE_CONFIRMED |
| zip | Aspose.ZIP | COMPLETE | 4/4 | PROBE_CONFIRMED |
| tasks | Aspose.Tasks | COMPLETE | 5/5 | REFLECTION_CANDIDATE |
| cad | Aspose.CAD | COMPLETE | 5/5 | REFLECTION_CANDIDATE |
| ocr | Aspose.OCR | DEFERRED | 3/3 | WEBSITE_DISCOVERED |
| svg | Aspose.SVG | COMPLETE | 4/4 | REFLECTION_CANDIDATE |

**Wave 1 ready (PROBE_CONFIRMED)**: 3 families (17 plugins)
**Wave 2 probe-needed (REFLECTION_CANDIDATE)**: 3 families (14 plugins)
**Wave 3 deferred**: 1 family (3 plugins)
