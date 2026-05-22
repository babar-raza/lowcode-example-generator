using System;
using System.IO;
using Aspose.Diagram;
using Aspose.Diagram.LowCode;

namespace PdfConverterExample
{
    class Program
    {
        static void Main()
        {
            // Paths for the fixture and result
            string inputPath = "input.vsdx";
            string outputPath = "output.pdf";

            // -------------------------------------------------
            // 1. INPUT FIXTURE CREATION
            // -------------------------------------------------
            var diagram = new Diagram();
            var page = diagram.Pages[0];
            page.Name = "TestPage";

            var shape = new Shape
            {
                ID = 1,
                Name = "SampleRect",
                Type = TypeValue.Shape
            };
            shape.XForm.PinX.Value = 4.0;
            shape.XForm.PinY.Value = 5.0;
            shape.XForm.Width.Value = 2.0;
            shape.XForm.Height.Value = 1.5;
            page.Shapes.Add(shape);

            diagram.Save(inputPath, SaveFileFormat.Vsdx);

            // Validate input file exists and is non‑empty
            if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
            {
                Console.WriteLine("Failed to create a valid input VSDX file.");
                return;
            }

            // -------------------------------------------------
            // 2. LOWCODE OPERATION
            // -------------------------------------------------
            PdfConverter.Process(inputPath, outputPath);

            // -------------------------------------------------
            // 3. OUTPUT VALIDATION
            // -------------------------------------------------
            if (File.Exists(outputPath))
            {
                long size = new FileInfo(outputPath).Length;
                Console.WriteLine($"Conversion succeeded. Output PDF size: {size} bytes.");
            }
            else
            {
                Console.WriteLine("Conversion failed: output PDF was not created.");
            }
        }
    }
}