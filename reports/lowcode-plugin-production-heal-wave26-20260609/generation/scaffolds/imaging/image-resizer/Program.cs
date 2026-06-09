using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Resizer");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(200, 200);
bmp.Resize(100, 100);
bmp.Save("output-resized.png", new PngOptions());
Console.WriteLine("Image resized successfully: output-resized.png");
