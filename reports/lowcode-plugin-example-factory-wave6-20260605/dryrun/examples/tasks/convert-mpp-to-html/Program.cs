// tasks/convert-mpp-to-html
// Canonical: https://products.aspose.net/tasks/mpp-to-html/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() + project.Save(path, new HtmlSaveOptions())
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "project.html");

var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 12, 31));

var task1 = project.RootTask.Children.Add("Research");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(7, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Development");
task2.Set(Tsk.Start, new DateTime(2026, 1, 10));
task2.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var task3 = project.RootTask.Children.Add("Deployment");
task3.Set(Tsk.Start, new DateTime(2026, 1, 28));
task3.Set(Tsk.Duration, project.GetDuration(3, TimeUnitType.Day));

var options = new HtmlSaveOptions();
project.Save(outputPath, options);
Console.WriteLine($"Project saved to HTML: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
