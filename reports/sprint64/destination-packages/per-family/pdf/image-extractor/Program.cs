using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

// Minimal 1x1 red pixel BMP (58 bytes) as fixture image
var bmpBytes = new byte[] {
    66, 77, 58, 0, 0, 0, 0, 0, 0, 0, 54, 0, 0, 0,
    40, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 24, 0,
    0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 255, 0
};
var document = new Document();
var page = document.Pages.Add();
page.Resources.Images.Add(new MemoryStream(bmpBytes));
document.Save("input.pdf");

var options = new ImageExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
var result = new ImageExtractor().Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Images extracted" : "No images found");
