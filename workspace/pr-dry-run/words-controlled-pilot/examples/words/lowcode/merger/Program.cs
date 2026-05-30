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

            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");
            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.docx");
            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.docx");
            File.Copy(inputPath, input1Path, overwrite: true);
            File.Copy(inputPath, input2Path, overwrite: true);

            Merger.Merge("output.docx", new string[] { input1Path, input2Path });

            Console.WriteLine("Done.");
        }
    }
}
