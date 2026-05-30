using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

var options = new PdfToXlsOptions();
options.Format = PdfToXlsOptions.ExcelFormat.XLSX;
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.xlsx"));
var result = new XlsConverter().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to XLSX" : "No output");
