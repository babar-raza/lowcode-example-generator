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
            Console.WriteLine("Example: slides-compress");

            string inputPath = "input.pptx";
            using (var pres = new Presentation())
            {
                pres.Slides[0].Shapes.AddAutoShape(
                    Aspose.Slides.ShapeType.Rectangle, 100, 100, 200, 50);
                pres.Save(inputPath, SaveFormat.Pptx);
            }

            string outputPath = "output.pptx";
            using (var pres = new Presentation(inputPath))
            {
                Compress.RemoveUnusedLayoutSlides(pres);
                pres.Save(outputPath, SaveFormat.Pptx);
            }

            Console.WriteLine(File.Exists(outputPath)
                ? $"Compression succeeded: {outputPath}"
                : "Compression failed: output file not found.");
        }
    }
}
