using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
var page = document.Pages.Add();
page.Paragraphs.Add(new TextFragment("Hello, LowCode TextExtractor!"));
document.Save("input.pdf");

var options = new TextExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
var result = new TextExtractor().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0
    ? $"Extracted text from {result.ResultCollection.Count} page(s)"
    : "No text extracted");
