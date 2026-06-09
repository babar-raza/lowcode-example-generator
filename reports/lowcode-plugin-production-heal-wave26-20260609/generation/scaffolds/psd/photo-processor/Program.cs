using Aspose.PSD;
using Aspose.PSD.ImageOptions;

Console.WriteLine("Aspose.PSD - Photo Processor");
using var img = new PsdImage(200, 200);
img.Save("output.png", new PngOptions());
Console.WriteLine("Photo processed: output.png");
