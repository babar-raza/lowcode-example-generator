using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Compressor");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(100, 100);
var opts = new JpegOptions { Quality = 50 };
bmp.Save("output-compressed.jpg", opts);
Console.WriteLine("Image compressed successfully: output-compressed.jpg");
