using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Forms;

var doc = new Document();
var page = doc.Pages.Add();
var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
textBox.PartialName = "TextField1";
textBox.Value = "ExportedValue";
doc.Form.Add(textBox, 1);
doc.Save("input.pdf");

var exportOptions = new FormExporterToJsonOptions();
exportOptions.AddInput(new FileDataSource("input.pdf"));
exportOptions.AddOutput(new FileDataSource("output.json"));
var result = new FormExporter().Process(exportOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Form exported to JSON" : "No output");
