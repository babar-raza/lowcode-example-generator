using System;
using System.IO;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-watermarker");

            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            Watermarker.SetText(inputPath, "output_text_watermark.docx", "Confidential");

            string imagePath = Path.Combine(AppContext.BaseDirectory, "watermark.bmp");
            byte[] bmpBytes = new byte[] {
                0x42, 0x4D, 0x3A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, 0x00,
                0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0xFF, 0x00, 0x00, 0x00
            };
            File.WriteAllBytes(imagePath, bmpBytes);
            Watermarker.SetImage(inputPath, "output_image_watermark.docx", imagePath);

            Console.WriteLine("Done.");
        }
    }
}
