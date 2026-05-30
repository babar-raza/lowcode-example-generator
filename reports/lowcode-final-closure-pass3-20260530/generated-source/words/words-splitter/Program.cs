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
            Console.WriteLine("Example: words-splitter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // ExtractPages — no suitable overload found in catalog
            // Demonstrate Splitter.RemoveBlankPages
            Splitter.RemoveBlankPages(Path.Combine(AppContext.BaseDirectory, "input.docx"), "output.docx");
            // Split — no suitable overload found in catalog

            Console.WriteLine("Done.");
        }
    }
}
