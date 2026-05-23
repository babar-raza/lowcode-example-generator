using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var doc = new Document();
doc.Pages.Add();
doc.Save("input.pdf");

var options = TableOptions.Create()
    .InsertPageBefore(1);

options.AddTable()
    .AddRow()
        .AddCell()
            .AddParagraph(new TextFragment("Header 1"))
        .AddCell()
            .AddParagraph(new TextFragment("Header 2"))
    .AddRow()
        .AddCell()
            .AddParagraph(new TextFragment("Cell 1"))
        .AddCell()
            .AddParagraph(new TextFragment("Cell 2"));

options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));

var plugin = new TableGenerator();
var result = plugin.Process(options);

Console.WriteLine(result.ResultCollection.Count > 0 ? "Table added" : "No output");