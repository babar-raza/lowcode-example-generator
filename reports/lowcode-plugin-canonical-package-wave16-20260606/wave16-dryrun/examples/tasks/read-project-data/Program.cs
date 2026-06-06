// tasks/read-project-data
// Canonical: https://products.aspose.net/tasks/read-project-data/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() -> Save fixture -> new Project(path) -> read task data -> write report
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string fixturePath = Path.Combine("output", "fixture.xml");
string outputPath = Path.Combine("output", "project-data.txt");

// Create project fixture programmatically
var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 6, 30));
project.Set(Prj.Name, "Wave 16 Sample Project");

var task1 = project.RootTask.Children.Add("Phase 1: Research");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(10, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Phase 2: Development");
task2.Set(Tsk.Start, new DateTime(2026, 1, 15));
task2.Set(Tsk.Duration, project.GetDuration(20, TimeUnitType.Day));

var task3 = project.RootTask.Children.Add("Phase 3: Testing");
task3.Set(Tsk.Start, new DateTime(2026, 2, 10));
task3.Set(Tsk.Duration, project.GetDuration(7, TimeUnitType.Day));

// Save to XML format (no binary fixture needed)
project.Save(fixturePath, SaveFileFormat.Xml);

// Now read project data from the saved file
var loadedProject = new Project(fixturePath);

var sb = new StringBuilder();
sb.AppendLine($"Project: {loadedProject.Get(Prj.Name)}");
sb.AppendLine($"Start: {loadedProject.Get(Prj.StartDate):yyyy-MM-dd}");
sb.AppendLine($"Finish: {loadedProject.Get(Prj.FinishDate):yyyy-MM-dd}");
sb.AppendLine();
sb.AppendLine("Tasks:");

int taskCount = 0;
foreach (Task task in loadedProject.RootTask.Children)
{
    sb.AppendLine($"  [{taskCount + 1}] {task.Get(Tsk.Name)}");
    sb.AppendLine($"      Start: {task.Get(Tsk.Start):yyyy-MM-dd}");
    sb.AppendLine($"      Duration: {task.Get(Tsk.Duration)}");
    taskCount++;
}

sb.AppendLine();
sb.AppendLine($"Total tasks read: {taskCount}");
File.WriteAllText(outputPath, sb.ToString(), Encoding.UTF8);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Project data read: {taskCount} tasks extracted -> {outputPath} ({size} bytes)");
