using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document1 = new Document();
var page1 = document1.Pages.Add();
page1.Paragraphs.Add(new TextFragment("Document 1 - Page 1"));
document1.Save("input1.pdf");

var document2 = new Document();
var page2 = document2.Pages.Add();
page2.Paragraphs.Add(new TextFragment("Document 2 - Page 1"));
document2.Save("input2.pdf");

var options = new MergeOptions();
options.AddInput(new FileDataSource("input1.pdf"));
options.AddInput(new FileDataSource("input2.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new Merger().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Merged successfully" : "No output");
