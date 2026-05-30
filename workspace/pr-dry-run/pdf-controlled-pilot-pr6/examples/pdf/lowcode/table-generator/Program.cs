using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

var document = new Document();
document.Pages.Add();
document.Save("input.pdf");

// Build TableOptions separately so AddInput/AddOutput are called on the
// TableOptions instance, not on the TableCellBuilder chain end.
var options = new TableOptions();
options.InsertPageBefore(1);
options.AddTable()
    .AddRow()
        .AddCell().AddParagraph(new TextFragment("Header 1"))
        .AddCell().AddParagraph(new TextFragment("Header 2"));
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new TableGenerator().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Table added" : "No output");
