using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Prepare two input DOCX files with different content.
        string baseDir = AppContext.BaseDirectory;
        string inputPath1 = Path.Combine(baseDir, "input1.docx");
        string inputPath2 = Path.Combine(baseDir, "input2.docx");
        CreateSampleDoc(inputPath1, "First document content");
        CreateSampleDoc(inputPath2, "Second document content");

        // Validate that both input files exist.
        if (!File.Exists(inputPath1))
            throw new FileNotFoundException("Input file 1 not found.", inputPath1);
        if (!File.Exists(inputPath2))
            throw new FileNotFoundException("Input file 2 not found.", inputPath2);

        // Define the output document path.
        string outputPath = Path.Combine(baseDir, "output.docx");

        // Call the static Compare method (simplest string‑path overload).
        Comparer.Compare(
            v1: inputPath1,
            v2: inputPath2,
            outputFileName: outputPath,
            author: "Demo Author",
            dateTime: DateTime.UtcNow);

        // Verify that the output file was created.
        if (!File.Exists(outputPath))
            throw new InvalidOperationException("Output file was not created.");

        var info = new FileInfo(outputPath);
        Console.WriteLine($"Comparison completed successfully. Output: {outputPath} ({info.Length} bytes)");
    }

    private static void CreateSampleDoc(string path, string text)
    {
        var doc = new Document();
        var builder = new DocumentBuilder(doc);
        builder.Writeln(text);
        doc.Save(path);
    }
}