using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

var options = new TiffOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.tiff"));
var result = new Tiff().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "TIFF created" : "No output");
