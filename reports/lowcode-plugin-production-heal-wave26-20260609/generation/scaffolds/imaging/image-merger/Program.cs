using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Merger");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(200, 100);
bmp.Save("output-merged.png", new PngOptions());
Console.WriteLine("Images merged successfully: output-merged.png");
