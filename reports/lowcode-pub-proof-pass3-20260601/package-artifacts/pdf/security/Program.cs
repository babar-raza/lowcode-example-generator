using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Facades;

var doc = new Document();
doc.Pages.Add();
doc.Save("input.pdf");

DocumentPrivilege privilege = DocumentPrivilege.ForbidAll;
privilege.AllowPrint = true;

var encOptions = new EncryptionOptions("owner123", "user123", privilege);
encOptions.AddInput(new FileDataSource("input.pdf"));
encOptions.AddOutput(new FileDataSource("output.pdf"));
var result = new Security().Process(encOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "PDF encrypted" : "No output");
