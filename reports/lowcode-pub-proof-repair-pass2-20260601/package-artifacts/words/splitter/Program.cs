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

            // Demonstrate Splitter.RemoveBlankPages
            Splitter.RemoveBlankPages(Path.Combine(AppContext.BaseDirectory, "input.docx"), "output.docx");

            Console.WriteLine("Done.");
        }
    }
}
