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
            Console.WriteLine("Example: cells-json-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate JsonConverter.Process
            JsonConverter.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.json");

            Console.WriteLine("Done.");
        }
    }
}
