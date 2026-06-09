using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Cropper");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(200, 200);
bmp.Crop(new Aspose.Imaging.Rectangle(10, 10, 100, 100));
bmp.Save("output-cropped.png", new PngOptions());
Console.WriteLine("Image cropped successfully: output-cropped.png");
