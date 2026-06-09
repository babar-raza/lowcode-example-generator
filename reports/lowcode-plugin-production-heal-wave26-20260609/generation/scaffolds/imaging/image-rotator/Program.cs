using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

Console.WriteLine("Aspose.Imaging - Image Rotator");
using var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(100, 100);
bmp.RotateFlip(RotateFlipType.Rotate90FlipNone);
bmp.Save("output-rotated.png", new PngOptions());
Console.WriteLine("Image rotated successfully: output-rotated.png");
