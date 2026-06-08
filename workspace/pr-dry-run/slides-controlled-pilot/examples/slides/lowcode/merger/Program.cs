using System;
using Aspose.Slides;
using Aspose.Slides.LowCode;
using Aspose.Slides.Export;
using Aspose.Slides.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: slides-merger");

            // Create input file(s)
            var pres1 = new Aspose.Slides.Presentation();
            pres1.Slides.AddEmptySlide(pres1.LayoutSlides[0]);
            pres1.Save("input1.pptx", Aspose.Slides.Export.SaveFormat.Pptx);
            var pres2 = new Aspose.Slides.Presentation();
            pres2.Slides.AddEmptySlide(pres2.LayoutSlides[0]);
            pres2.Save("input2.pptx", Aspose.Slides.Export.SaveFormat.Pptx);

            // Demonstrate Merger.Process
            Merger.Process(new string[] { "input1.pptx", "input2.pptx" }, "output.pptx");

            Console.WriteLine("Done.");
        }
    }
}
