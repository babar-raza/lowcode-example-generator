using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-comparer");

            string v1Path = "input_v1.docx";
            string v2Path = "input_v2.docx";

            var doc1 = new Document();
            var builder1 = new DocumentBuilder(doc1);
            builder1.Writeln("This is version 1 of the document.");
            doc1.Save(v1Path);

            var doc2 = new Document();
            var builder2 = new DocumentBuilder(doc2);
            builder2.Writeln("This is version 2 of the document with changes.");
            doc2.Save(v2Path);

            string outputPath = "output.docx";
            Comparer.Compare(v1Path, v2Path, outputPath, "Author", DateTime.UtcNow);

            Console.WriteLine(File.Exists(outputPath)
                ? $"Comparison succeeded: {outputPath}"
                : "Comparison failed: output not found.");
        }
    }
}
