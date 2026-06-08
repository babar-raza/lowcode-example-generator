# PDF LowCode Namespace Map

## Namespace: Aspose.Pdf.LowCode

All PDF LowCode plugin classes live in `Aspose.Pdf.LowCode`, NOT `Aspose.Pdf.Plugins`.

### Confirmed Classes (21 total)
| Class | Status | In Format Authority |
|-------|--------|---------------------|
| DocConverter | WORKING | Yes |
| XlsConverter | WORKING | Yes |
| Html | WORKING | Yes |
| Jpeg | WORKING | Yes |
| Png | WORKING | Yes |
| Tiff | WORKING | Yes |
| TextExtractor | WORKING | Yes |
| Merger | WORKING | Yes |
| Splitter | WORKING | Yes |
| Optimizer | WORKING | Yes |
| PdfAConverter | WORKING | Yes |
| TocGenerator | WORKING | Yes |
| TableGenerator | WORKING | Yes |
| ImageExtractor | WORKING | Yes |
| Security | WORKING | Yes |
| FormFlattener | WORKING | Yes |
| FormEditor | WORKING | Yes |
| FormExporter | WORKING | Yes |
| Signature | WORKING | Yes |
| FormImporter | UPSTREAM_BUG | No (NullRef in Process()) |
| Timestamp | ENV_DEPENDENT | No (requires TSA server) |

### Abstract/Non-instantiable
- PdfExtractor: abstract base class
- PdfToImage: abstract base class

### Previous Misclassification
The previous sprint stated "PDF FormImporter and PDF Timestamp probes use an invalid namespace (Aspose.Pdf.LowCode)".
This was INCORRECT. `Aspose.Pdf.LowCode` IS the correct namespace.
The probes failed for different reasons:
- FormImporter: NullReferenceException in runtime (upstream bug)
- Timestamp: Works correctly when TSA server is available
