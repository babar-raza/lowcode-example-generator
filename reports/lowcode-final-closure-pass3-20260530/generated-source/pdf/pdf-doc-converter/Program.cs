using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
var page = document.Pages.Add();
page.Paragraphs.Add(new TextFragment("LowCode DocConverter Test"));
document.Save("input.pdf");

var options = new PdfToDocOptions();
options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX;
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.docx"));
var result = new DocConverter().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to DOCX" : "No output");
