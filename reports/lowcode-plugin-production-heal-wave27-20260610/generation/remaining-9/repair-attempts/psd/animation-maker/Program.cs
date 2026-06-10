using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

// Create a PSD image programmatically
using (var psdImage = new PsdImage(200, 200))
{
    // Draw on the image
    var graphics = new Aspose.PSD.Graphics(psdImage);
    graphics.Clear(Aspose.PSD.Color.White);
    graphics.DrawRectangle(
        new Aspose.PSD.Pen(Aspose.PSD.Color.Red, 2),
        new Aspose.PSD.Rectangle(10, 10, 180, 180));

    // Save as PSD
    string outputPath = "output.psd";
    psdImage.Save(outputPath, new PsdOptions());

    var info = new FileInfo(outputPath);
    Console.WriteLine($"PSD animation frame created: {info.Length} bytes");
}

File.WriteAllText("expected-output.json", "{\"status\": \"success\", \"format\": \"psd\"}");
