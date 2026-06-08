# First 10 Plugin Transformation Plan

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Selection Criteria (Applied)

Priority order:
1. Real product page ✓ (all 65 have URLs)
2. Official code/gist/snippet harvested ✓
3. Symbols extracted ✓
4. Family manually analyzed ✓
5. Reflection validation available ✓ (via prior sprint DllReflector)
6. Fixture plan clear ✓
7. Output plan clear ✓
8. Low license/runtime risk ✓ (prefer no-fixture or simple-fixture)

---

## Candidate 1: barcode/generate-barcode

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/barcode/net/generate-barcode |
| Source code | StoreBarcodeOutputAsFile.cs (GitHub) |
| Classes | BarcodeGenerator, EncodeTypes, BarCodeImageFormat |
| Methods | new BarcodeGenerator(EncodeTypes.Code128, "12345678"); gen.Save(path, BarCodeImageFormat.Png) |
| Fixture plan | NO INPUT FIXTURE NEEDED — code generates from string |
| Output plan | output-barcode.png |
| Example folder | barcode/generate-barcode |
| Validation command | dotnet run |
| Expected output | PNG file >500 bytes |
| Blocker status | NONE |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 2: barcode/generate-qr-code

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/barcode/net/generate-qr-code |
| Source code | SwissQRCodeGenRec.cs (GitHub) |
| Classes | BarcodeGenerator |
| Methods | new BarcodeGenerator(EncodeTypes.QR, "Hello World"); gen.Save() |
| Fixture plan | NO INPUT FIXTURE NEEDED |
| Output plan | output-qrcode.png |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 3: imaging/convert-image

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/imaging/net/convert-image |
| Source code | ConvertImageWithGrayscale.cs (GitHub, GIST-ID: 7850a7dd) |
| Classes | Image, JpegOptions, PngOptions |
| Methods | Image.Load(inputPath); image.Save(outputPath, new PngOptions()) |
| Fixture plan | input JPEG file (e.g., test.jpg) |
| Output plan | output.png |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 4: imaging/resize-image

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/imaging/net/resize-image |
| Classes | Image |
| Methods | image.Resize(width, height, ResizeType.LanczosResample) |
| Fixture plan | input image file |
| Output plan | resized output image |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 5: tasks/convert-mpp-to-pdf

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/tasks/net/convert-mpp-to-pdf |
| Source code | ExXlsxOptions.cs (confirmed by prior probe) |
| Classes | Project, SaveFileFormat |
| Methods | new Project(mppPath); project.Save(pdfPath, SaveFileFormat.Pdf) |
| Fixture plan | Test MPP file or programmatically created Project() |
| Output plan | output.pdf |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 6: tasks/convert-mpp-to-excel

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/tasks/net/convert-mpp-to-excel |
| Source code | ExXlsxOptions.cs |
| Classes | Project, XlsxOptions, SaveFileFormat |
| Methods | project.Save(outputPath, SaveFileFormat.Xlsx) |
| Fixture plan | same MPP file as candidate 5 |
| Output plan | output.xlsx |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 7: html/convert-html-to-pdf

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/html/net/convert-html-to-pdf |
| Source code | FlattenPDFExample.cs |
| Classes | HTMLDocument, PdfSaveOptions, Converter |
| Methods | new HTMLDocument(htmlPath); Converter.ConvertHTML(doc, opts, outputPath) |
| Fixture plan | input HTML file (or inline HTML string) |
| Output plan | output.pdf |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 8: zip/compress-files

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/zip/net/compress-files |
| Source code | CompressToTarBz2.cs (confirmed by prior probe) |
| Classes | Archive |
| Methods | new Archive(); archive.CreateEntry(name, filePath); archive.Save(outputPath) |
| Fixture plan | one or two text files to compress |
| Output plan | output.zip |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 9: drawing/create-drawing

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/drawing/net/create-drawing |
| Source code | DrawArc.cs |
| Classes | Bitmap, Graphics, Pen |
| Methods | new Bitmap(800,600); Graphics.FromImage(bmp); g.DrawArc(pen, x, y, w, h, startAngle, sweep); bmp.Save() |
| Fixture plan | NO INPUT FIXTURE NEEDED — creates from scratch |
| Output plan | output-drawing.png |
| Readiness | READY_NEXT_SPRINT |

---

## Candidate 10: note/convert-one-to-pdf

| Field | Value |
|-------|-------|
| Product page | https://products.aspose.net/note/net/convert-one-to-pdf |
| Source code | PdfConversion.cs |
| Classes | Document, PdfSaveOptions |
| Methods | new Document(onePath); document.Save(pdfPath, new PdfSaveOptions()) |
| Fixture plan | .ONE (OneNote) file |
| Output plan | output.pdf |
| Readiness | READY_NEXT_SPRINT |

---

## Summary

| # | Family | Plugin | Fixture | Readiness |
|---|--------|--------|---------|-----------|
| 1 | barcode | generate-barcode | NONE | READY_NEXT_SPRINT |
| 2 | barcode | generate-qr-code | NONE | READY_NEXT_SPRINT |
| 3 | imaging | convert-image | image file | READY_NEXT_SPRINT |
| 4 | imaging | resize-image | image file | READY_NEXT_SPRINT |
| 5 | tasks | convert-mpp-to-pdf | MPP or empty Project() | READY_NEXT_SPRINT |
| 6 | tasks | convert-mpp-to-excel | MPP or empty Project() | READY_NEXT_SPRINT |
| 7 | html | convert-html-to-pdf | HTML file | READY_NEXT_SPRINT |
| 8 | zip | compress-files | text files | READY_NEXT_SPRINT |
| 9 | drawing | create-drawing | NONE | READY_NEXT_SPRINT |
| 10 | note | convert-one-to-pdf | .ONE file | READY_NEXT_SPRINT |
