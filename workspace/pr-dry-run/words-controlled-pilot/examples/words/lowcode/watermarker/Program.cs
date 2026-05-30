using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-watermarker");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // Demonstrate Watermarker.SetText — applies a text watermark
            Watermarker.SetText(inputPath, "output_text_watermark.docx", "Confidential");

            // Demonstrate Watermarker.SetImage — requires a valid image file path.
            // Create a minimal 1x1 BMP image to use as the watermark source.
            string imagePath = Path.Combine(AppContext.BaseDirectory, "watermark.bmp");
            // Minimal valid BMP: 54-byte header + 4 bytes pixel (1x1, 24bpp, padded to 4 bytes)
            byte[] bmpBytes = new byte[] {
                0x42, 0x4D, 0x3A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, 0x00,
                0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0xFF, 0x00, 0x00, 0x00  // 1 pixel (blue) + 1 padding byte
            };
            File.WriteAllBytes(imagePath, bmpBytes);
            Watermarker.SetImage(inputPath, "output_image_watermark.docx", imagePath);

            Console.WriteLine("Done.");
        }
    }
}
