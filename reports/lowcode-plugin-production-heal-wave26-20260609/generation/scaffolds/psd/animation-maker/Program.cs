using Aspose.PSD;
using Aspose.PSD.ImageOptions;

Console.WriteLine("Aspose.PSD - Animation Maker");
using var img = new PsdImage(100, 100);
img.Save("output.png", new PngOptions());
Console.WriteLine("Animation frame created: output.png");
