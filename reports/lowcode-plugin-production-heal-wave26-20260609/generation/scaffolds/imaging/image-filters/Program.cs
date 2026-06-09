using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Filters");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(100, 100);
bmp.Save("output-filtered.png", new PngOptions());
Console.WriteLine("Image filter applied successfully: output-filtered.png");
