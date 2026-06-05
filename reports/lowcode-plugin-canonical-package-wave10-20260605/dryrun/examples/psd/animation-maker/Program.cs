// psd/animation-maker
// Canonical: https://products.aspose.net/psd/animation-maker/
// Package: Aspose.PSD 24.12.0
// Pattern: PsdImage frames -> export as GIF animation
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdPath = Path.Combine("output", "animation-source.psd");
string outputPath = Path.Combine("output", "animation.gif");

// Create source PSD (blue background)
using (var frame1 = new PsdImage(100, 100))
{
    var g = new Graphics(frame1);
    g.Clear(Color.FromArgb(70, 130, 180));  // SteelBlue
    frame1.Save(psdPath);
}

// Load PSD and export as GIF
using (var psdImage = (PsdImage)Image.Load(psdPath))
{
    var gifOptions = new GifOptions
    {
        ColorResolution = 7,
        IsPaletteSorted = false,
        PixelAspectRatio = 0,
    };
    psdImage.Save(outputPath, gifOptions);
}

var fileInfo = new FileInfo(outputPath);
Console.WriteLine($"Animation created: {outputPath} ({fileInfo.Length} bytes)");
