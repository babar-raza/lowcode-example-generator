using System;
using System.IO;
using Aspose.Cells.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: cells-spreadsheet-merger");

            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.xlsx");
            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.xlsx");
            File.Copy(inputPath, input1Path, overwrite: true);
            File.Copy(inputPath, input2Path, overwrite: true);

            SpreadsheetMerger.Process(new string[] { input1Path, input2Path }, "output.xlsx");

            Console.WriteLine("Done.");
        }
    }
}
