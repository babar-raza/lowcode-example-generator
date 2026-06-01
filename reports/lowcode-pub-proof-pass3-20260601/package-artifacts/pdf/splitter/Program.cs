using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
for (int i = 1; i <= 3; i++)
{
    var pg = document.Pages.Add();
    pg.Paragraphs.Add(new TextFragment($"Page {i}"));
}
document.Save("input.pdf");

var options = new SplitOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output_page1.pdf"));
options.AddOutput(new FileDataSource("output_page2.pdf"));
options.AddOutput(new FileDataSource("output_page3.pdf"));
var result = new Splitter().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0
    ? $"Split into {result.ResultCollection.Count} file(s)"
    : "No output");
