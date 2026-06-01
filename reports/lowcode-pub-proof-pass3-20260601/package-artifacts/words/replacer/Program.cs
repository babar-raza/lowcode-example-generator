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
            Console.WriteLine("Example: words-replacer");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // Demonstrate Replacer.Replace
            Replacer.Replace(Path.Combine(AppContext.BaseDirectory, "input.docx"), "output.docx", "sample", "sample");

            Console.WriteLine("Done.");
        }
    }
}
