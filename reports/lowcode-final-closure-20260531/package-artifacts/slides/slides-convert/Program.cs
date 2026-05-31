using System;
using System.IO;
using Aspose.Slides;
using Aspose.Slides.Export;
using Aspose.Slides.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: slides-convert");

            // Create input PPTX programmatically
            string inputPath = "input.pptx";
            using (var pres = new Presentation())
            {
                pres.Slides[0].Shapes.AddAutoShape(
                    Aspose.Slides.ShapeType.Rectangle, 100, 100, 200, 50);
                pres.Save(inputPath, SaveFormat.Pptx);
            }

            // Convert PPTX to PDF using LowCode Convert
            // Use fully-qualified name to avoid ambiguity with System.Convert
            string outputPath = "output.pdf";
            Aspose.Slides.LowCode.Convert.ToPdf(inputPath, outputPath);

            Console.WriteLine(File.Exists(outputPath)
                ? $"Conversion succeeded: {outputPath}"
                : "Conversion failed: output file not found.");
        }
    }
}
