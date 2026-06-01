using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
var page = document.Pages.Add();
page.Paragraphs.Add(new TextFragment("LowCode PDF/A Converter Test"));
document.Save("input.pdf");

var options = new PdfAConvertOptions();
options.PdfAVersion = PdfAStandardVersion.PDF_A_1B;
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new PdfAConverter().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to PDF/A-1B" : "No output");
