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
            Console.WriteLine("Example: cells-image-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate ImageConverter.Process
            ImageConverter.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.png");

            Console.WriteLine("Done.");
        }
    }
}
