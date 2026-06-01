using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

var options = new TocOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new TocGenerator().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "TOC added" : "No output");
