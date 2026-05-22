# FormEditor — Remove All Form Fields from PDF

This example demonstrates how to remove all form fields from an AcroForm PDF using the Aspose.PDF LowCode `FormEditor` plugin.

## What This Example Does

1. Creates a programmatic PDF with an AcroForm text field (`TextField1`)
2. Uses `FormRemoveAllFieldsOptions` to configure the form field removal operation
3. Calls `new FormEditor().Process(options)` to remove all form fields
4. Produces a flattened PDF with no interactive form fields

## API Used

- `Aspose.Pdf.LowCode.FormEditor` — LowCode plugin for editing PDF form fields
- `Aspose.Pdf.LowCode.FormRemoveAllFieldsOptions` — Options class for removing all form fields
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
