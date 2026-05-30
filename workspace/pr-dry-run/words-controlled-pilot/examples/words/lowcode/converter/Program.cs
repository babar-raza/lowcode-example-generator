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
            Console.WriteLine("Example: words-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // Demonstrate Converter.Convert
            Converter.Convert(Path.Combine(AppContext.BaseDirectory, "input.docx"), "output.pdf");
            // ConvertToImages — no suitable overload found in catalog
            // Demonstrate Converter.Create
            Converter.Create();

            Console.WriteLine("Done.");
        }
    }
}
