using System;
using System.IO;
using Aspose.Slides;
using Aspose.Slides.Export;
using Aspose.Slides.LowCode;

class Program
{
    static void Main()
    {
        // SECTION 1: INPUT FIXTURE CREATION
        string inputPath = Path.Combine(Path.GetTempPath(), "input.pptx");
        using (Presentation pres = new Presentation())
        {
            // Add a simple slide with a title
            ISlide slide = pres.Slides[0];
            IAutoShape titleShape = slide.Shapes.AddAutoShape(ShapeType.Rectangle, 50, 50, 600, 100);
            titleShape.AddTextFrame("Sample Slide");
            pres.Save(inputPath, SaveFormat.Pptx);
        }

        // Verify input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.WriteLine("Failed to create a valid input file.");
            return;
        }

        // SECTION 2: LOWCODE OPERATION
        string outputPath = Path.Combine(Path.GetTempPath(), "output.pptx");
        Merger.Process(new string[] { inputPath }, outputPath);

        // SECTION 3: OUTPUT VALIDATION
        if (File.Exists(outputPath))
        {
            long size = new FileInfo(outputPath).Length;
            Console.WriteLine($"Success: output file size = {size} bytes");
        }
        else
        {
            Console.WriteLine("Merger failed to produce an output file.");
        }
    }
}