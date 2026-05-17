# FormExporter — Export PDF Form Fields to JSON

This example demonstrates how to export AcroForm field data from a PDF to JSON format using the Aspose.PDF LowCode `FormExporter` plugin.

## What This Example Does

1. Creates a programmatic PDF with an AcroForm text field (`TextField1`) with value `ExportedValue`
2. Uses `FormExporterToJsonOptions` to configure the JSON export operation
3. Calls `new FormExporter().Process(options)` to export form field data to a JSON file
4. Produces an `output.json` file containing the field names and values

## API Used

- `Aspose.Pdf.LowCode.FormExporter` — LowCode plugin for exporting PDF form field data
- `Aspose.Pdf.LowCode.FormExporterToJsonOptions` — Options class for JSON export
- `Aspose.Pdf.LowCode.FileDataSource` — File-based input/output data source
- `Aspose.Pdf.Forms.TextBoxField` — Used to create the AcroForm fixture

## Run

```bash
dotnet restore
dotnet build
dotnet run
```

## More Information

- [Aspose.PDF for .NET](https://products.aspose.net/pdf)
- [LowCode API Reference](https://reference.aspose.com/pdf/net/)
