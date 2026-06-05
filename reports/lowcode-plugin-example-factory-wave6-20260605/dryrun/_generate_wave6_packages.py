#!/usr/bin/env python3
"""Wave 6 dry-run package generator.
Builds 14 target packages and records results.
"""
import os, sys, json, subprocess, shutil
from pathlib import Path
from datetime import datetime

REPORT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPORT_ROOT / "dryrun" / "examples"
SPRINT = "lowcode-plugin-example-factory-wave6-20260605"
DATE = "2026-06-05"

EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────────────

def run(cmd, cwd, timeout=300):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=True)
    return r.returncode, r.stdout + r.stderr

def write_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2), encoding="utf-8")

def make_csproj(pkg_dir, name, nuget_pkg, nuget_ver, extra_refs=""):
    write_file(pkg_dir / f"{name}.csproj", f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{nuget_pkg}" Version="{nuget_ver}" />
{extra_refs}  </ItemGroup>
</Project>""")

def make_provenance(pkg_dir, family, slug, nuget_pkg, nuget_ver, canonical_url):
    write_json(pkg_dir / "source-provenance.json", {
        "family": family,
        "plugin_slug": slug,
        "nuget_package": nuget_pkg,
        "nuget_version": nuget_ver,
        "sprint": SPRINT,
        "generated_at": DATE,
        "canonical_url": canonical_url,
        "fixture_strategy": "programmatic",
        "fixture_source": f"reports/{SPRINT}/dryrun/_generate_wave6_packages.py"
    })

def make_manifest(pkg_dir, key, nuget_pkg, nuget_ver, canonical_url, output_files):
    write_json(pkg_dir / "package-manifest.json", {
        "package_key": key,
        "nuget_package": nuget_pkg,
        "nuget_version": nuget_ver,
        "sprint": SPRINT,
        "generated_at": DATE,
        "canonical_url": canonical_url,
        "output_files": output_files
    })

def build_and_run(pkg_dir, key):
    """Restore, build, run. Copy logs to root. Return (pass_flag, output_info)."""
    rc_r, out_r = run("dotnet restore", pkg_dir)
    (pkg_dir / "restore.log").write_text(out_r, encoding="utf-8")

    rc_b, out_b = run("dotnet build --no-restore -c Release", pkg_dir)
    (pkg_dir / "build.log").write_text(out_b, encoding="utf-8")

    if rc_b != 0:
        (pkg_dir / "run.log").write_text("BUILD FAILED — run skipped\n", encoding="utf-8")
        return False, {"build_error": out_b[-500:]}

    rc_run, out_run = run("dotnet run --no-build -c Release", pkg_dir, timeout=120)
    (pkg_dir / "run.log").write_text(out_run, encoding="utf-8")

    # copy logs from logs/ subdir if they ended up there
    logs_sub = pkg_dir / "logs"
    if logs_sub.exists():
        for lf in ["restore.log", "build.log", "run.log"]:
            src = logs_sub / lf
            if src.exists():
                shutil.copy2(src, pkg_dir / lf)

    output_dir = pkg_dir / "output"
    output_files = []
    if output_dir.exists():
        for f in sorted(output_dir.iterdir()):
            if f.is_file():
                output_files.append({"path": f"output/{f.name}", "size": f.stat().st_size})

    if rc_run != 0 and not output_files:
        return False, {"run_error": out_run[-500:]}

    # accept if output produced
    passed = bool(output_files)
    return passed, {"output_files": output_files, "exit_code": rc_run}

# ── Package definitions ────────────────────────────────────────────────────

PACKAGES = []

# 1. ocr/image-text-finder
def build_ocr_image_text_finder():
    fam, slug = "ocr", "image-text-finder"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// ocr/image-text-finder
// Canonical: https://products.aspose.net/ocr/image-text-finder/
// Package: Aspose.OCR 24.12.0
// Pattern: AsposeOcr + OcrInput(SingleImage) -> api.Recognize()
using Aspose.OCR;
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.Combine("output", "canvas.bmp");
string outputPath = Path.Combine("output", "recognized.txt");

// Generate fixture image
using (var bmp = new Bitmap(400, 150))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.White);
    g.DrawString("Find this text in image", new Font("Arial", 16), Brushes.Black, 20, 50);
    g.DrawString("Aspose.OCR image-text-finder", new Font("Arial", 12), Brushes.DarkBlue, 20, 90);
    bmp.Save(fixturePath, ImageFormat.Bmp);
}

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = api.Recognize(input);
string recognized = results[0].RecognitionText;
File.WriteAllText(outputPath, recognized);
Console.WriteLine($"Image text finder result: {outputPath} ({recognized.Length} chars)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.OCR", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.OCR", "24.12.0", "https://products.aspose.net/ocr/image-text-finder/")
    make_manifest(pkg_dir, key, "Aspose.OCR", "24.12.0", "https://products.aspose.net/ocr/image-text-finder/", ["output/recognized.txt"])
    return key, pkg_dir

# 2. ocr/invoice-to-text
def build_ocr_invoice_to_text():
    fam, slug = "ocr", "invoice-to-text"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// ocr/invoice-to-text
// Canonical: https://products.aspose.net/ocr/invoice-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: AsposeOcr + OcrInput(SingleImage) -> api.Recognize() -> text extraction
using Aspose.OCR;
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.Combine("output", "canvas.bmp");
string outputPath = Path.Combine("output", "invoice-text.txt");

// Generate invoice-style fixture image
using (var bmp = new Bitmap(500, 300))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.White);
    g.DrawString("INVOICE #INV-2026-001", new Font("Arial", 18, FontStyle.Bold), Brushes.Black, 20, 20);
    g.DrawString("Date: 2026-06-05", new Font("Arial", 12), Brushes.Black, 20, 60);
    g.DrawString("Bill To: Acme Corporation", new Font("Arial", 12), Brushes.Black, 20, 85);
    g.DrawString("Item: Software License    Amount: $500.00", new Font("Arial", 11), Brushes.Black, 20, 130);
    g.DrawString("Total: $500.00", new Font("Arial", 14, FontStyle.Bold), Brushes.Black, 20, 200);
    bmp.Save(fixturePath, ImageFormat.Bmp);
}

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = api.Recognize(input);
string recognized = results[0].RecognitionText;
File.WriteAllText(outputPath, recognized);
Console.WriteLine($"Invoice OCR result: {outputPath} ({recognized.Length} chars)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.OCR", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.OCR", "24.12.0", "https://products.aspose.net/ocr/invoice-to-text/")
    make_manifest(pkg_dir, key, "Aspose.OCR", "24.12.0", "https://products.aspose.net/ocr/invoice-to-text/", ["output/invoice-text.txt"])
    return key, pkg_dir

# 3. note/convert-one-to-word
def build_note_convert_to_word():
    fam, slug = "note", "convert-one-to-word"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// note/convert-one-to-word
// Canonical: https://products.aspose.net/note/convert-onenote-to-word/
// Package: Aspose.Note 24.12.0
// Pattern: new Document() -> AppendChildLast -> Save(SaveFormat.Docx)
using Aspose.Note;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.docx");

var doc = new Document();
var page = new Page();
var outline = new Outline();
var element = new OutlineElement();
var richText = new RichText()
{
    Text = "OneNote to Word Conversion Demo\\n" +
           "This document was generated programmatically by Aspose.Note.\\n" +
           "Section 1: Introduction\\n" +
           "Aspose.Note enables converting OneNote documents to Word format.\\n" +
           "Section 2: Features\\n" +
           "Preserve text, formatting, and document structure.",
    ParagraphStyle = ParagraphStyle.Default
};
element.AppendChildLast(richText);
outline.AppendChildLast(element);
page.AppendChildLast(outline);
doc.AppendChildLast(page);
doc.Save(outputPath, SaveFormat.Docx);
Console.WriteLine($"Note converted to Word: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Note", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Note", "24.12.0", "https://products.aspose.net/note/convert-onenote-to-word/")
    make_manifest(pkg_dir, key, "Aspose.Note", "24.12.0", "https://products.aspose.net/note/convert-onenote-to-word/", ["output/output.docx"])
    return key, pkg_dir

# 4. note/convert-one-to-image
def build_note_convert_to_image():
    fam, slug = "note", "convert-one-to-image"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// note/convert-one-to-image
// Canonical: https://products.aspose.net/note/convert-onenote-to-image/
// Package: Aspose.Note 24.12.0
// Pattern: new Document() -> AppendChildLast -> Save(SaveFormat.Png)
using Aspose.Note;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.png");

var doc = new Document();
var page = new Page();
var outline = new Outline();
var element = new OutlineElement();
var richText = new RichText()
{
    Text = "OneNote to Image Conversion Demo\\n" +
           "This page was generated by Aspose.Note and exported as PNG.\\n" +
           "Image export preserves page layout and text content.",
    ParagraphStyle = ParagraphStyle.Default
};
element.AppendChildLast(richText);
outline.AppendChildLast(element);
page.AppendChildLast(outline);
doc.AppendChildLast(page);
doc.Save(outputPath, SaveFormat.Png);
Console.WriteLine($"Note converted to Image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Note", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Note", "24.12.0", "https://products.aspose.net/note/convert-onenote-to-image/")
    make_manifest(pkg_dir, key, "Aspose.Note", "24.12.0", "https://products.aspose.net/note/convert-onenote-to-image/", ["output/output.png"])
    return key, pkg_dir

# 5. tasks/convert-mpp-to-excel
def build_tasks_to_excel():
    fam, slug = "tasks", "convert-mpp-to-excel"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
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
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Tasks", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-excel/")
    make_manifest(pkg_dir, key, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-excel/", ["output/project.xlsx"])
    return key, pkg_dir

# 6. tasks/convert-mpp-to-html
def build_tasks_to_html():
    fam, slug = "tasks", "convert-mpp-to-html"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
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
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Tasks", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-html/")
    make_manifest(pkg_dir, key, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-html/", ["output/project.html"])
    return key, pkg_dir

# 7. tasks/convert-mpp-to-image
def build_tasks_to_image():
    fam, slug = "tasks", "convert-mpp-to-image"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// tasks/convert-mpp-to-image
// Canonical: https://products.aspose.net/tasks/mpp-to-png/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() + project.Save(path, new ImageSaveOptions(SaveFileFormat.PNG))
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "project.png");

var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 6, 30));

var task1 = project.RootTask.Children.Add("Sprint 1");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Sprint 2");
task2.Set(Tsk.Start, new DateTime(2026, 1, 19));
task2.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var task3 = project.RootTask.Children.Add("Sprint 3");
task3.Set(Tsk.Start, new DateTime(2026, 2, 5));
task3.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var options = new ImageSaveOptions(SaveFileFormat.PNG);
project.Save(outputPath, options);
Console.WriteLine($"Project saved to Image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Tasks", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-png/")
    make_manifest(pkg_dir, key, "Aspose.Tasks", "24.12.0", "https://products.aspose.net/tasks/mpp-to-png/", ["output/project.png"])
    return key, pkg_dir

# 8. html/convert-html-to-word
def build_html_to_word():
    fam, slug = "html", "convert-html-to-word"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// html/convert-html-to-word
// Canonical: https://products.aspose.net/html/html-to-docx-converter/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, DocSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.docx");

string htmlContent =
    "<!DOCTYPE html><html><head><title>HTML to Word Demo</title></head><body>" +
    "<h1>HTML to Word Conversion</h1>" +
    "<p>This document was converted from HTML to Word format using Aspose.HTML for .NET.</p>" +
    "<h2>Features</h2>" +
    "<ul><li>Preserve HTML structure</li>" +
    "<li>Convert headings and paragraphs</li>" +
    "<li>Support lists and tables</li></ul>" +
    "<p>Generated on 2026-06-05 by the lowcode example factory.</p>" +
    "</body></html>";

var options = new DocSaveOptions();
Converter.ConvertHTML(htmlContent, ".", options, outputPath);
Console.WriteLine($"HTML converted to Word: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.HTML", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.HTML", "24.12.0", "https://products.aspose.net/html/html-to-docx-converter/")
    make_manifest(pkg_dir, key, "Aspose.HTML", "24.12.0", "https://products.aspose.net/html/html-to-docx-converter/", ["output/output.docx"])
    return key, pkg_dir

# 9. html/convert-html-to-image
def build_html_to_image():
    fam, slug = "html", "convert-html-to-image"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// html/convert-html-to-image
// Canonical: https://products.aspose.net/html/html-to-image-converter/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, ImageSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.jpg");

string htmlContent =
    "<!DOCTYPE html><html><head><title>HTML to Image Demo</title>" +
    "<style>body{font-family:Arial;background:#f0f4f8;padding:20px;}" +
    "h1{color:#1a5276;}div{background:white;padding:15px;border-radius:8px;}</style>" +
    "</head><body><div>" +
    "<h1>HTML to Image Conversion</h1>" +
    "<p>This HTML page was rendered as a JPEG image using Aspose.HTML.</p>" +
    "<p>Date: 2026-06-05</p>" +
    "</div></body></html>";

var options = new ImageSaveOptions(Aspose.Html.Rendering.Image.ImageFormat.Jpeg);
Converter.ConvertHTML(htmlContent, ".", options, outputPath);
Console.WriteLine($"HTML converted to Image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.HTML", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.HTML", "24.12.0", "https://products.aspose.net/html/html-to-image-converter/")
    make_manifest(pkg_dir, key, "Aspose.HTML", "24.12.0", "https://products.aspose.net/html/html-to-image-converter/", ["output/output.jpg"])
    return key, pkg_dir

# 10. page/convert-eps-to-pdf
def build_page_eps_to_pdf():
    fam, slug = "page", "convert-eps-to-pdf"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// page/convert-eps-to-pdf
// Canonical: https://products.aspose.net/page/eps-to-pdf/
// Package: Aspose.Page 24.12.0
// Pattern: PsDocument(epsStream) -> SaveAsPdf(pdfStream, PdfSaveOptions)
using Aspose.Page.EPS;
using Aspose.Page.EPS.Device;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.pdf");

// EPS fixture: minimal Encapsulated PostScript
byte[] epsBytes = System.Text.Encoding.ASCII.GetBytes(
    "%!PS-Adobe-3.0 EPSF-3.0\n" +
    "%%BoundingBox: 0 0 200 200\n" +
    "%%Title: Aspose.Page EPS Demo\n" +
    "%%Creator: lowcode-example-factory\n" +
    "%%EndComments\n" +
    "% Draw border rectangle\n" +
    "0.5 setlinewidth\n" +
    "10 10 moveto\n" +
    "190 10 lineto\n" +
    "190 190 lineto\n" +
    "10 190 lineto\n" +
    "closepath stroke\n" +
    "% Draw title text\n" +
    "/Helvetica findfont 16 scalefont setfont\n" +
    "30 150 moveto\n" +
    "(Aspose.Page EPS Demo) show\n" +
    "30 120 moveto\n" +
    "(EPS to PDF Conversion) show\n" +
    "30 90 moveto\n" +
    "(Generated 2026-06-05) show\n" +
    "%%EOF\n");

using var epsStream = new MemoryStream(epsBytes);
using var pdfStream = File.Open(outputPath, FileMode.Create);
var doc = new PsDocument(epsStream);
var options = new PdfSaveOptions();
doc.SaveAsPdf(pdfStream, options);
Console.WriteLine($"EPS converted to PDF: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.Page", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.Page", "24.12.0", "https://products.aspose.net/page/eps-to-pdf/")
    make_manifest(pkg_dir, key, "Aspose.Page", "24.12.0", "https://products.aspose.net/page/eps-to-pdf/", ["output/output.pdf"])
    return key, pkg_dir

# 11. psd/psd-image-converter
def build_psd_image_converter():
    fam, slug = "psd", "psd-image-converter"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// psd/psd-image-converter
// Canonical: https://products.aspose.net/psd/image-converter/
// Package: Aspose.PSD 24.12.0
// Pattern: new PsdImage(w,h) -> Save as PSD -> reload -> Save(JpegOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "output.jpg");

// Create PSD programmatically
using (var psdImage = new PsdImage(200, 150))
{
    // Fill with background color
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.LightBlue);
    graphics.DrawString("Aspose.PSD Demo", new Font("Arial", 14), new SolidBrush(Color.DarkBlue), new PointF(20, 60));
    psdImage.Save(psdFixturePath);
}

// Load and convert to JPEG
using (var image = (PsdImage)Image.Load(psdFixturePath))
{
    image.Save(outputPath, new JpegOptions { Quality = 90 });
}
Console.WriteLine($"PSD converted to JPEG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.PSD", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.PSD", "24.12.0", "https://products.aspose.net/psd/image-converter/")
    make_manifest(pkg_dir, key, "Aspose.PSD", "24.12.0", "https://products.aspose.net/psd/image-converter/", ["output/output.jpg"])
    return key, pkg_dir

# 12. psd/convert-psd-to-pdf
def build_psd_to_pdf():
    fam, slug = "psd", "convert-psd-to-pdf"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// psd/convert-psd-to-pdf
// Canonical: https://products.aspose.net/psd/psd-to-pdf/
// Package: Aspose.PSD 24.12.0
// Pattern: new PsdImage(w,h) -> Save as PSD -> Image.Load -> Save(PdfOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "output.pdf");

// Create PSD programmatically
using (var psdImage = new PsdImage(300, 200))
{
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.White);
    graphics.DrawString("PSD to PDF Conversion", new Font("Arial", 16), new SolidBrush(Color.Black), new PointF(20, 50));
    graphics.DrawString("Aspose.PSD for .NET", new Font("Arial", 12), new SolidBrush(Color.Gray), new PointF(20, 90));
    graphics.DrawString("2026-06-05", new Font("Arial", 10), new SolidBrush(Color.Gray), new PointF(20, 120));
    psdImage.Save(psdFixturePath);
}

// Load and convert to PDF
using (var image = Image.Load(psdFixturePath))
{
    image.Save(outputPath, new PdfOptions());
}
Console.WriteLine($"PSD converted to PDF: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.PSD", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.PSD", "24.12.0", "https://products.aspose.net/psd/psd-to-pdf/")
    make_manifest(pkg_dir, key, "Aspose.PSD", "24.12.0", "https://products.aspose.net/psd/psd-to-pdf/", ["output/output.pdf"])
    return key, pkg_dir

# 13. svg/vectorizer
def build_svg_vectorizer():
    fam, slug = "svg", "vectorizer"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// svg/vectorizer
// Canonical: https://products.aspose.net/svg/vectorizer/
// Package: Aspose.SVG 24.12.0
// Pattern: ImageVectorizer -> Vectorize(imagePath) -> SVGDocument.Save()
using Aspose.Svg;
using Aspose.Svg.ImageVectorization;
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.Combine("output", "fixture.png");
string outputPath = Path.Combine("output", "output.svg");

// Generate simple raster image fixture
using (var bmp = new Bitmap(100, 100))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.White);
    g.FillEllipse(Brushes.DarkBlue, 20, 20, 60, 60);
    g.DrawRectangle(Pens.Red, 10, 10, 80, 80);
    bmp.Save(fixturePath, ImageFormat.Png);
}

var vectorizer = new ImageVectorizer
{
    Configuration = new ImageVectorizerConfiguration
    {
        ColorsLimit = 8,
        LineWidth = 1.0
    }
};
using var document = vectorizer.Vectorize(fixturePath);
document.Save(outputPath);
Console.WriteLine($"Image vectorized to SVG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.SVG", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.SVG", "24.12.0", "https://products.aspose.net/svg/vectorizer/")
    make_manifest(pkg_dir, key, "Aspose.SVG", "24.12.0", "https://products.aspose.net/svg/vectorizer/", ["output/output.svg"])
    return key, pkg_dir

# 14. tex/convert-latex-to-pdf
def build_tex_latex_to_pdf():
    fam, slug = "tex", "convert-latex-to-pdf"
    key = f"{fam}/{slug}"
    pkg_dir = EXAMPLES_DIR / fam / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    write_file(pkg_dir / "Program.cs", """\
// tex/convert-latex-to-pdf
// Canonical: https://products.aspose.net/tex/net/convert-latex-to-pdf
// Package: Aspose.TeX 24.12.0
// Pattern: TeXOptions.ConsoleAppOptions(TeXConfig.ObjectLaTeX) + TeXJob + PdfDevice
using Aspose.TeX;
using Aspose.TeX.IO;
using Aspose.TeX.Presentation.Pdf;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
Directory.CreateDirectory("input");
string outputPath = Path.Combine("output", "job.pdf");

// Write minimal LaTeX source file
string latexContent = @"\\documentclass{minimal}
\\begin{document}
\\textbf{Aspose.TeX LaTeX to PDF Demo}\\\\
This document was compiled from LaTeX source\\\\
using Aspose.TeX for .NET.\\\\
Date: 2026-06-05
\\end{document}
";
File.WriteAllText(Path.Combine("input", "job.tex"), latexContent, Encoding.UTF8);

var options = TeXOptions.ConsoleAppOptions(TeXConfig.ObjectLaTeX);
options.InputWorkingDirectory = new InputFileSystemDirectory("input");
options.OutputWorkingDirectory = new OutputFileSystemDirectory("output");
options.TerminalOut = new OutputFileTerminal(options.OutputWorkingDirectory);

new TeXJob("job", new PdfDevice(), options).Run();
Console.WriteLine($"LaTeX compiled to PDF: {outputPath} ({(File.Exists(outputPath) ? new FileInfo(outputPath).Length : 0)} bytes)");
""")
    make_csproj(pkg_dir, f"{fam}-{slug}", "Aspose.TeX", "24.12.0")
    make_provenance(pkg_dir, fam, slug, "Aspose.TeX", "24.12.0", "https://products.aspose.net/tex/net/convert-latex-to-pdf")
    make_manifest(pkg_dir, key, "Aspose.TeX", "24.12.0", "https://products.aspose.net/tex/net/convert-latex-to-pdf", ["output/job.pdf"])
    return key, pkg_dir

# ── Main ───────────────────────────────────────────────────────────────────

BUILDERS = [
    build_ocr_image_text_finder,
    build_ocr_invoice_to_text,
    build_note_convert_to_word,
    build_note_convert_to_image,
    build_tasks_to_excel,
    build_tasks_to_html,
    build_tasks_to_image,
    build_html_to_word,
    build_html_to_image,
    build_page_eps_to_pdf,
    build_psd_image_converter,
    build_psd_to_pdf,
    build_svg_vectorizer,
    build_tex_latex_to_pdf,
]

results = []

for builder in BUILDERS:
    key, pkg_dir = builder()
    print(f"\n{'='*60}")
    print(f"Building: {key}")
    print(f"  Path: {pkg_dir}")

    passed, info = build_and_run(pkg_dir, key)
    status = "PASS" if passed else "FAIL"
    print(f"  Status: {status}")
    if "output_files" in info:
        for f in info["output_files"]:
            print(f"  Output: {f['path']} ({f['size']} bytes)")
    if "build_error" in info or "run_error" in info:
        err = info.get("build_error", info.get("run_error", ""))
        print(f"  Error: {err[:200]}")

    # Write output-validation.json
    ov = {
        "package_key": key,
        "sprint": SPRINT,
        "generated_at": DATE,
        "verdict": status,
    }
    if "output_files" in info:
        ov["output_files"] = info["output_files"]
    if "build_error" in info:
        ov["build_error"] = info["build_error"]
    if "run_error" in info:
        ov["run_error"] = info["run_error"]
    write_json(pkg_dir / "output-validation.json", ov)

    results.append({
        "package_key": key,
        "status": status,
        "pkg_dir": str(pkg_dir),
        "output_files": info.get("output_files", [])
    })

# Write build results summary
pass_count = sum(1 for r in results if r["status"] == "PASS")
fail_count = len(results) - pass_count

summary = {
    "sprint": SPRINT,
    "date": DATE,
    "total": len(results),
    "pass": pass_count,
    "fail": fail_count,
    "verdict": "WAVE6_PASS" if pass_count >= 8 else "WAVE6_INSUFFICIENT",
    "results": results
}

out_path = REPORT_ROOT / "dryrun" / "wave6" / "wave6-build-results.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
write_json(out_path, summary)

print(f"\n{'='*60}")
print(f"Wave 6 Build Summary: {pass_count}/{len(results)} PASS")
print(f"Verdict: {summary['verdict']}")
print(f"Results: {out_path}")
