// tasks/convert-mpp-to-excel
// Canonical: https://products.aspose.net/tasks/mpp-to-excel/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() + project.Save(path, new XlsxOptions())
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "project.xlsx");

var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 12, 31));

var task1 = project.RootTask.Children.Add("Planning");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Implementation");
task2.Set(Tsk.Start, new DateTime(2026, 1, 8));
task2.Set(Tsk.Duration, project.GetDuration(15, TimeUnitType.Day));

var task3 = project.RootTask.Children.Add("Review");
task3.Set(Tsk.Start, new DateTime(2026, 1, 27));
task3.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

var options = new XlsxOptions();
project.Save(outputPath, options);
Console.WriteLine($"Project saved to Excel: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
