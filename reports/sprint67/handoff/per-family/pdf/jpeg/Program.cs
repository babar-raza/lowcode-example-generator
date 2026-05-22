using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

var options = new JpegOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.jpg"));
var result = new Jpeg().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "JPEG created" : "No output");
