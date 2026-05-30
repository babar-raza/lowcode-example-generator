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
            Console.WriteLine("Example: cells-text-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate TextConverter.Process
            TextConverter.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.txt");

            Console.WriteLine("Done.");
        }
    }
}
