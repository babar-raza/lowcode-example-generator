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
            Console.WriteLine("Example: slides-for-each");

            string inputPath = "input.pptx";

            // Create a test presentation programmatically
            using (var pres = new Presentation())
            {
                pres.Slides[0].Shapes.AddAutoShape(
                    Aspose.Slides.ShapeType.Rectangle, 100, 100, 200, 50);
                pres.Slides.AddEmptySlide(pres.Slides[0].LayoutSlide);
                pres.Save(inputPath, SaveFormat.Pptx);
            }

            string outputPath = "output.pptx";
            int slideCount = 0;

            using (var pres = new Presentation(inputPath))
            {
                // Demonstrate ForEach.Slide — iterates each slide with index
                ForEach.Slide(pres, (Slide slide, int index) =>
                {
                    slideCount++;
                });

                pres.Save(outputPath, SaveFormat.Pptx);
            }

            Console.WriteLine(File.Exists(outputPath)
                ? $"ForEach complete: {slideCount} slides processed, output: {outputPath}"
                : "ForEach failed: output file not found.");

            Console.WriteLine("Done.");
        }
    }
}
