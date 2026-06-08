# FormImporter Upstream Bug Packet

## Bug Summary
Aspose.Pdf.LowCode.FormImporter.Process() throws NullReferenceException
when calling internal Form.ImportJson(Stream) method.

## Reproduction
1. Create AcroForm PDF with text field programmatically
2. Create JSON import data in any supported format
3. Call `new FormImporter().Process(options)` with FormImporterJsonOptions
4. Crash: `System.NullReferenceException` at `Aspose.Pdf.Forms.Form.[internal]`

## Package Version: 26.5.0
## Latest Available: 26.5.0
## Retry Condition: New Aspose.PDF version > 26.5.0
## Classification: UPSTREAM_BUG (confirmed, no workaround)
