using System;
using System.IO;
using Aspose.Slides;
using Aspose.Slides.Export;
using Aspose.Slides.LowCode;

class Program
{
    static void Main()
    {
        string inputPath = "input.pptx";
        string outputPath = "output.pptx";

        if (!File.Exists(inputPath))
        {
            Console.WriteLine($"Input file not found: {inputPath}");
            return;
        }

        using var pres = new Presentation(inputPath);
        Compress.RemoveUnusedLayoutSlides(pres);
        pres.Save(outputPath, SaveFormat.Pptx);

        if (File.Exists(outputPath))
        {
            Console.WriteLine("Compression completed successfully.");
        }
        else
        {
            Console.WriteLine("Failed to create output file.");
        }
    }
}