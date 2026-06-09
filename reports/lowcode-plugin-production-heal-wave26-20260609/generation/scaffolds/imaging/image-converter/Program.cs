using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Converter");
// Create a minimal test image programmatically
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(100, 100);
bmp.Save("output.png", new PngOptions());
Console.WriteLine("Image converted successfully: output.png");
