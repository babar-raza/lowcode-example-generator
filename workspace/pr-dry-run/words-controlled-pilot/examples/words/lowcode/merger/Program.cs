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
            Console.WriteLine("Example: words-merger");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // Merger.Merge requires multiple input files.
            // Create input1.docx and input2.docx from the available fixture.
            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.docx");
            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.docx");
            File.Copy(inputPath, input1Path, overwrite: true);
            File.Copy(inputPath, input2Path, overwrite: true);

            // Demonstrate Merger.Merge
            Merger.Merge("output.docx", new string[] { input1Path, input2Path });

            Console.WriteLine("Done.");
        }
    }
}
