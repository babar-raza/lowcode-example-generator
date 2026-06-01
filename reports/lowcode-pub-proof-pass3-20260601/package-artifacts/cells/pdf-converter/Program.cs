using System;
using System.IO;
using Aspose.Cells;
using Aspose.Cells.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: cells-pdf-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate PdfConverter.Process
            PdfConverter.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.pdf");

            Console.WriteLine("Done.");
        }
    }
}
