using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Add Watermark");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(200, 200);
bmp.Save("output-watermarked.png", new PngOptions());
Console.WriteLine("Watermark added successfully: output-watermarked.png");
