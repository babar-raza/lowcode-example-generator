using System;
using System.IO;
using Aspose.Pdf.LowCode;

File.WriteAllText("input.html", "<html><body><h1>Hello LowCode</h1><p>HTML to PDF.</p></body></html>");

var options = new HtmlToPdfOptions();
options.AddInput(new FileDataSource("input.html"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new Html().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "HTML converted to PDF" : "No output");
