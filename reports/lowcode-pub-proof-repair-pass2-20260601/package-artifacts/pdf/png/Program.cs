using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

var options = new PngOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.png"));
var result = new Png().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "PNG created" : "No output");
