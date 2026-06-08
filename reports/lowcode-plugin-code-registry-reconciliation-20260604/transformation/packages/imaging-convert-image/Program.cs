// Aspose.Imaging — Convert image to JPEG with options
// Canonical product page: https://products.aspose.net/imaging/image-converter/
// Source authority: https://github.com/aspose-imaging/Aspose.Imaging-for-.NET
// Source file: Examples/CSharp/ModifyingAndConvertingImages/ConvertImageWithGrayscale.cs
//
// Pattern: LOAD_SAVE_OPTIONS
//   Image.Load(inputPath) → image.Save(outputPath, options)

using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

string outputDir = Path.Combine(Directory.GetCurrentDirectory(), "output");
Directory.CreateDirectory(outputDir);

// Create a minimal test image (BMP) to convert
string inputPath = Path.Combine(outputDir, "input_test.bmp");
string outputPath = Path.Combine(outputDir, "output_converted.jpg");

// Write a minimal 10x10 BMP file programmatically for testing
using (var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(10, 10))
{
    var graphics = new Aspose.Imaging.Graphics(bmp);
    graphics.FillRectangle(new Aspose.Imaging.Brushes.SolidBrush(Aspose.Imaging.Color.Blue),
        new Aspose.Imaging.Rectangle(0, 0, 10, 10));
    bmp.Save(inputPath);
}

// Load and convert the image
using (Image image = Image.Load(inputPath))
{
    JpegOptions jpegOptions = new JpegOptions
    {
        Quality = 85
    };
    image.Save(outputPath, jpegOptions);
}

Console.WriteLine($"Converted image saved to: {outputPath}");
Console.WriteLine($"File exists: {File.Exists(outputPath)}");
Console.WriteLine($"File size: {new FileInfo(outputPath).Length} bytes");
Console.WriteLine("SNIPPET_RUN: PASS");
