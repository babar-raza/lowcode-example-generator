using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Forms;

var doc = new Document();
var page = doc.Pages.Add();
var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
textBox.PartialName = "TextField1";
textBox.Value = "Hello AcroForm";
doc.Form.Add(textBox, 1);
doc.Save("input.pdf");

var removeOptions = new FormRemoveAllFieldsOptions();
removeOptions.AddInput(new FileDataSource("input.pdf"));
removeOptions.AddOutput(new FileDataSource("output.pdf"));
var result = new FormEditor().Process(removeOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Form fields removed" : "No output");
