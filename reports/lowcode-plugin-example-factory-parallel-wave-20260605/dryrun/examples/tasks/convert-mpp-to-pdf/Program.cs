// tasks/convert-mpp-to-pdf
// Canonical: https://products.aspose.net/tasks/project-to-pdf-converter/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() -> add tasks -> Save(path, SaveFileFormat.Pdf)
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "project.pdf");

var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 12, 31));

var task1 = project.RootTask.Children.Add("Design Phase");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Development Phase");
task2.Set(Tsk.Start, new DateTime(2026, 1, 8));
task2.Set(Tsk.Duration, project.GetDuration(10, TimeUnitType.Day));

var task3 = project.RootTask.Children.Add("Testing Phase");
task3.Set(Tsk.Start, new DateTime(2026, 1, 22));
task3.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

var options = new PdfSaveOptions();
project.Save(outputPath, options);
Console.WriteLine($"Project PDF saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
