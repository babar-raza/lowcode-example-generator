using System;
using System.IO;
using Aspose.Slides;
using Aspose.Slides.LowCode;

class Program
{
    static void Main()
    {
        // 1. Create input PPTX file
        string inputPath = Path.Combine(Directory.GetCurrentDirectory(), "input.pptx");
        using (Presentation pres = new Presentation())
        {
            ISlide slide = pres.Slides[0];
            IAutoShape titleShape = slide.Shapes.AddAutoShape(ShapeType.Rectangle, 50, 50, 600, 100);
            titleShape.AddTextFrame("LowCode Convert Demo");
            pres.Save(inputPath, Aspose.Slides.Export.SaveFormat.Pptx);
        }

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.WriteLine("Failed to create input presentation.");
            return;
        }

        // 2. Perform LowCode conversion to PDF
        string outputPath = Path.Combine(Directory.GetCurrentDirectory(), "output.pdf");
        Aspose.Slides.LowCode.Convert.ToPdf(inputPath, outputPath);

        // 3. Validate output file and report success
        if (File.Exists(outputPath) && new FileInfo(outputPath).Length > 0)
        {
            long size = new FileInfo(outputPath).Length;
            Console.WriteLine($"Conversion succeeded. Output file size: {size} bytes.");
        }
        else
        {
            Console.WriteLine("Conversion failed: output file not found or empty.");
        }
    }
}