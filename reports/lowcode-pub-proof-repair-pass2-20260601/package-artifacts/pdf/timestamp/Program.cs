using System;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

// Create a sample PDF
var document = new Document();
var page = document.Pages.Add();
page.Paragraphs.Add(new TextFragment("Sample PDF for timestamp demonstration"));
document.Save("input.pdf");

// Apply a trusted timestamp using Timestamp LowCode API
// Requires an accessible TSA (Timestamp Authority) server
var options = new TimestampOptions
{
    ServerUrl = "http://timestamp.digicert.com",
    PageNumber = 1
};
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output_timestamped.pdf"));

try
{
    var result = new Timestamp().Process(options);
    bool outputExists = System.IO.File.Exists("output_timestamped.pdf");
    long size = outputExists ? new System.IO.FileInfo("output_timestamped.pdf").Length : 0;
    Console.WriteLine($"Output: output_timestamped.pdf (exists={outputExists}, size={size} bytes)");
    Console.WriteLine(result.ResultCollection.Count > 0 ? "Timestamp applied successfully" : "No result");
}
catch (Exception ex)
{
    Console.WriteLine($"Timestamp requires TSA server connectivity: {ex.GetType().Name}: {ex.Message}");
}
Console.WriteLine("Done.");
