using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

// Create a PSD image and process it
using (var psdImage = new PsdImage(100, 100))
{
    // Draw content
    var graphics = new Aspose.PSD.Graphics(psdImage);
    graphics.Clear(Aspose.PSD.Color.Blue);

    // Save as PNG (photo processing output)
    string outputPath = "output.png";
    psdImage.Save(outputPath, new PngOptions());

    var info = new FileInfo(outputPath);
    Console.WriteLine($"Processed photo saved: {info.Length} bytes");
}

File.WriteAllText("expected-output.json", "{\"status\": \"success\", \"format\": \"png\"}");
