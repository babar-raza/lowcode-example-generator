using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
var page = document.Pages.Add();
page.Paragraphs.Add(new TextFragment("LowCode Optimizer Test"));
document.Save("input.pdf");

var options = new OptimizeOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new Optimizer().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Optimized successfully" : "No output");
