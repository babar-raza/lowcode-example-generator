using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Define file paths
        string baseDir = AppContext.BaseDirectory;
        string inputPath1 = Path.Combine(baseDir, "input1.docx");
        string inputPath2 = Path.Combine(baseDir, "input2.docx");
        string outputPath = Path.Combine(baseDir, "output.docx");

        // Create first input DOCX file
        var doc1 = new Document();
        var builder1 = new DocumentBuilder(doc1);
        builder1.Writeln("This is the first document.");
        doc1.Save(inputPath1);

        // Create second input DOCX file
        var doc2 = new Document();
        var builder2 = new DocumentBuilder(doc2);
        builder2.Writeln("This is the second document.");
        doc2.Save(inputPath2);

        // Validate that both input files exist
        if (!File.Exists(inputPath1) || !File.Exists(inputPath2))
            throw new FileNotFoundException("One or more input files were not found.");

        // Ensure a clean output state
        if (File.Exists(outputPath))
            File.Delete(outputPath);

        // Merge the documents using the static Merger.Merge method
        Merger.Merge(outputPath, new[] { inputPath1, inputPath2 });

        // Verify that the output file was created
        if (File.Exists(outputPath))
            Console.WriteLine($"Success: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
        else
            throw new InvalidOperationException("Output file was not created.");
    }
}