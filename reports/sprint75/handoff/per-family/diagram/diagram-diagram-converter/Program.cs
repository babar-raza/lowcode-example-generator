using System;
using System.IO;
using Aspose.Diagram;
using Aspose.Diagram.LowCode;

class Program
{
    static void Main()
    {
        // Prepare temporary working directory
        string workDir = Path.Combine(Path.GetTempPath(), "AsposeDiagramLowCodeDemo");
        Directory.CreateDirectory(workDir);

        string inputPath = Path.Combine(workDir, "input.vsdx");
        string outputPath = Path.Combine(workDir, "output.vdx");

        // INPUT FIXTURE CREATION — create a valid VSDX file using the core API
        var diagram = new Diagram();
        var page = diagram.Pages[0];
        page.Name = "TestPage";

        var shape = new Shape();
        shape.ID = 1;
        shape.Name = "SampleRect";
        shape.Type = TypeValue.Shape;
        shape.XForm.PinX.Value = 4.0;
        shape.XForm.PinY.Value = 5.0;
        shape.XForm.Width.Value = 2.0;
        shape.XForm.Height.Value = 1.5;
        page.Shapes.Add(shape);

        diagram.Save(inputPath, SaveFileFormat.Vsdx);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath))
        {
            Console.WriteLine("Failed to create input file.");
            return;
        }
        var inputInfo = new FileInfo(inputPath);
        if (inputInfo.Length == 0)
        {
            Console.WriteLine("Input file is empty.");
            return;
        }

        // LOWCODE OPERATION — convert VSDX to VDX using DiagramConverter
        DiagramConverter.Process(inputPath, outputPath);

        // OUTPUT VALIDATION — verify output file exists and report its size
        if (!File.Exists(outputPath))
        {
            Console.WriteLine("Conversion failed: output file not found.");
            return;
        }
        var outputInfo = new FileInfo(outputPath);
        Console.WriteLine($"Conversion succeeded: output size = {outputInfo.Length} bytes");
    }
}