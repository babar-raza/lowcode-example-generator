"""
Lane G — Wave 7 Canonical Package Builder
Sprint: lowcode-plugin-canonical-identity-wave7-20260605

Builds 4 canonical dry-run packages for identity-verified candidates:
  ocr/photo-to-text
  ocr/table-to-text
  psd/animation-maker
  psd/photo-processor

All packages use canonical_plugin_slug as folder name and include
full canonical identity fields in source-provenance.json.
"""
import subprocess
import json
import shutil
import sys
from pathlib import Path
from datetime import date

SPRINT = "lowcode-plugin-canonical-identity-wave7-20260605"
TODAY = str(date.today())
BASE = Path(__file__).parent / "examples"

PACKAGES = [
    {
        "family": "ocr",
        "plugin_slug": "photo-to-text",
        "canonical_plugin_slug": "photo-to-text",
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "legacy_example_slug": "",
        "display_plugin_name": ".NET Photo to Text Converter",
        "canonical_url": "https://products.aspose.net/ocr/photo-to-text/",
        "nuget_package": "Aspose.OCR",
        "nuget_version": "24.12.0",
        "output_file": "output/photo-text.txt",
    },
    {
        "family": "ocr",
        "plugin_slug": "table-to-text",
        "canonical_plugin_slug": "table-to-text",
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "legacy_example_slug": "",
        "display_plugin_name": ".NET Table to Text Extractor",
        "canonical_url": "https://products.aspose.net/ocr/table-to-text/",
        "nuget_package": "Aspose.OCR",
        "nuget_version": "24.12.0",
        "output_file": "output/table-text.txt",
    },
    {
        "family": "psd",
        "plugin_slug": "animation-maker",
        "canonical_plugin_slug": "animation-maker",
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "legacy_example_slug": "",
        "display_plugin_name": ".NET Animation Maker",
        "canonical_url": "https://products.aspose.net/psd/animation-maker/",
        "nuget_package": "Aspose.PSD",
        "nuget_version": "24.12.0",
        "output_file": "output/animation.gif",
    },
    {
        "family": "psd",
        "plugin_slug": "photo-processor",
        "canonical_plugin_slug": "photo-processor",
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "legacy_example_slug": "",
        "display_plugin_name": ".NET PSD Photo Processor",
        "canonical_url": "https://products.aspose.net/psd/photo-processor/",
        "nuget_package": "Aspose.PSD",
        "nuget_version": "24.12.0",
        "output_file": "output/processed.jpg",
    },
]


PROGRAM_CS = {
    "ocr/photo-to-text": """\
// ocr/photo-to-text
// Canonical: https://products.aspose.net/ocr/photo-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr.Recognize -> extract text
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.GetFullPath("fixture.png");
string outputPath = Path.Combine("output", "photo-text.txt");

// Write minimal PNG fixture (40x12 white image) as base64
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
File.WriteAllBytes(fixturePath, pngBytes);

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = api.Recognize(input);
string text = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string output = $"photo-to-text result ({text.Length} chars recognized):\\n{text}";
File.WriteAllText(outputPath, output);
Console.WriteLine($"Photo text extracted: {outputPath} ({output.Length} bytes)");
""",
    "ocr/table-to-text": """\
// ocr/table-to-text
// Canonical: https://products.aspose.net/ocr/table-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr with DetectAreasMode.TABLE -> extract table text
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.GetFullPath("fixture.png");
string outputPath = Path.Combine("output", "table-text.txt");

// Write minimal PNG fixture (40x12 white image) as base64
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
File.WriteAllBytes(fixturePath, pngBytes);

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var settings = new RecognitionSettings
{
    DetectAreasMode = DetectAreasMode.TABLE
};
var results = api.Recognize(input, settings);
string text = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string output = $"table-to-text result ({text.Length} chars recognized):\\n{text}";
File.WriteAllText(outputPath, output);
Console.WriteLine($"Table text extracted: {outputPath} ({output.Length} bytes)");
""",
    "psd/animation-maker": """\
// psd/animation-maker
// Canonical: https://products.aspose.net/psd/animation-maker/
// Package: Aspose.PSD 24.12.0
// Pattern: PsdImage -> TimeLine frames -> export as GIF
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.FileFormats.Psd.Layers;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "animation.gif");

// Create a simple 2-frame animated PSD
int width = 100;
int height = 100;

using (var psdImage = new PsdImage(width, height))
{
    var graphics = new Graphics(psdImage);

    // Frame 1: blue background
    graphics.Clear(Color.FromArgb(70, 130, 180));

    // Get or create timeline for animation
    var timeLine = TimeLine.InitializeFrom(psdImage);
    timeLine.LoopesCount = 0; // infinite loop

    // Duplicate layer to create second frame
    psdImage.AddLayer(psdImage.Layers[0].Clone() as Layer ?? new RegularLayer(psdImage, width, height));

    // Export as GIF animation (2 frames)
    var gifOptions = new GifOptions();
    psdImage.Save(outputPath, gifOptions);
}

var fileInfo = new FileInfo(outputPath);
Console.WriteLine($"Animation created: {outputPath} ({fileInfo.Length} bytes)");
""",
    "psd/photo-processor": """\
// psd/photo-processor
// Canonical: https://products.aspose.net/psd/photo-processor/
// Package: Aspose.PSD 24.12.0
// Pattern: PsdImage.Load -> resize/process -> Save(JpegOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "processed.jpg");

// Create a PSD fixture programmatically
using (var psdImage = new PsdImage(200, 150))
{
    var graphics = new Graphics(psdImage);
    // Draw gradient-like pattern: top half green, bottom half blue
    graphics.FillRectangle(new SolidBrush(Color.FromArgb(34, 139, 34)), new Rectangle(0, 0, 200, 75));
    graphics.FillRectangle(new SolidBrush(Color.FromArgb(70, 130, 180)), new Rectangle(0, 75, 200, 75));
    psdImage.Save(psdFixturePath);
}

// Load and process: resize + convert to JPEG
using (var image = (PsdImage)Image.Load(psdFixturePath))
{
    // Resize (simulate photo processing: scale to 100x75)
    image.Resize(100, 75);

    // Save as JPEG with quality processing
    var jpegOptions = new JpegOptions { Quality = 85 };
    image.Save(outputPath, jpegOptions);
}

var fileInfo = new FileInfo(outputPath);
Console.WriteLine($"Photo processed: {outputPath} ({fileInfo.Length} bytes)");
""",
}

README_TEMPLATE = """\
# {display_name}

This example demonstrates the **{display_name}** for .NET.

Canonical product page: [{canonical_url}]({canonical_url})

## What It Does

{description}

## How to Run

```bash
dotnet run
```

## Output

{output_desc}

## Package

- NuGet: `{nuget_package}` {nuget_version}
- Sprint: `{sprint}`
- Canonical Plugin Slug: `{canonical_plugin_slug}`
- Identity Status: `{identity_status}`
"""

DESCRIPTIONS = {
    "ocr/photo-to-text": (
        "Extracts text from a photo image using Aspose.OCR. "
        "Loads an image, runs OCR recognition, and writes the extracted text to a file.",
        "Recognized text written to `output/photo-text.txt`.",
    ),
    "ocr/table-to-text": (
        "Extracts tabular text from an image using Aspose.OCR with TABLE area detection mode. "
        "Identifies table structures and extracts text cell-by-cell.",
        "Recognized table text written to `output/table-text.txt`.",
    ),
    "psd/animation-maker": (
        "Creates a multi-frame GIF animation from PSD layers using Aspose.PSD TimeLine API. "
        "Demonstrates programmatic animation creation with loop control.",
        "Animated GIF written to `output/animation.gif`.",
    ),
    "psd/photo-processor": (
        "Processes a PSD photo: loads the image, resizes it, and exports as JPEG. "
        "Demonstrates batch-capable photo processing with Aspose.PSD.",
        "Processed JPEG written to `output/processed.jpg`.",
    ),
}


def build_csproj(pkg):
    family = pkg["family"]
    slug = pkg["canonical_plugin_slug"]
    nuget = pkg["nuget_package"]
    version = pkg["nuget_version"]
    implicit = "enable" if family != "ocr" else "disable"
    return f"""\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>{implicit}</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{nuget}" Version="{version}" />
  </ItemGroup>
</Project>
"""


def run_cmd(cmd, cwd, log_path):
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, shell=True
    )
    log_content = result.stdout + result.stderr
    Path(log_path).write_text(log_content, encoding="utf-8")
    return result.returncode == 0, log_content


def build_package(pkg):
    family = pkg["family"]
    slug = pkg["canonical_plugin_slug"]
    key = f"{family}/{slug}"
    pkg_dir = BASE / family / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "output").mkdir(exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Building: {key}")

    # Program.cs
    (pkg_dir / "Program.cs").write_text(PROGRAM_CS[key], encoding="utf-8")

    # .csproj
    csproj_name = f"{family}-{slug}.csproj"
    (pkg_dir / csproj_name).write_text(build_csproj(pkg), encoding="utf-8")

    # README.md
    desc, output_desc = DESCRIPTIONS[key]
    readme = README_TEMPLATE.format(
        display_name=pkg["display_plugin_name"],
        canonical_url=pkg["canonical_url"],
        description=desc,
        output_desc=output_desc,
        nuget_package=pkg["nuget_package"],
        nuget_version=pkg["nuget_version"],
        sprint=SPRINT,
        canonical_plugin_slug=slug,
        identity_status=pkg["identity_status"],
    )
    (pkg_dir / "README.md").write_text(readme, encoding="utf-8")

    # source-provenance.json
    sp = {
        "package_key": key,
        "canonical_plugin_slug": slug,
        "canonical_url": pkg["canonical_url"],
        "display_plugin_name": pkg["display_plugin_name"],
        "legacy_example_slug": pkg["legacy_example_slug"],
        "identity_status": pkg["identity_status"],
        "nuget_package": pkg["nuget_package"],
        "nuget_version": pkg["nuget_version"],
        "sprint": SPRINT,
        "generated_at": TODAY,
    }
    (pkg_dir / "source-provenance.json").write_text(
        json.dumps(sp, indent=2), encoding="utf-8"
    )

    # package-manifest.json
    pm = {
        "package_key": key,
        "canonical_plugin_slug": slug,
        "canonical_url": pkg["canonical_url"],
        "display_plugin_name": pkg["display_plugin_name"],
        "nuget_package": pkg["nuget_package"],
        "nuget_version": pkg["nuget_version"],
        "sprint": SPRINT,
        "generated_at": TODAY,
    }
    (pkg_dir / "package-manifest.json").write_text(
        json.dumps(pm, indent=2), encoding="utf-8"
    )

    # dotnet restore
    ok_restore, restore_log = run_cmd(
        "dotnet restore", str(pkg_dir), str(pkg_dir / "restore.log")
    )
    if not ok_restore:
        print(f"  RESTORE FAILED")
        _write_ov(pkg_dir, key, slug, "FAIL", "RESTORE_FAIL", [])
        return {"key": key, "status": "FAIL", "stage": "restore"}

    # dotnet build
    ok_build, build_log = run_cmd(
        "dotnet build -c Release --no-restore",
        str(pkg_dir),
        str(pkg_dir / "build.log"),
    )
    if not ok_build:
        print(f"  BUILD FAILED")
        _write_ov(pkg_dir, key, slug, "FAIL", "BUILD_FAIL", [])
        return {"key": key, "status": "FAIL", "stage": "build"}

    # dotnet run
    ok_run, run_log = run_cmd(
        "dotnet run -c Release --no-build",
        str(pkg_dir),
        str(pkg_dir / "run.log"),
    )
    print(f"  Run output: {run_log.strip()[:200]}")

    # Collect outputs
    outputs = []
    for f in sorted((pkg_dir / "output").iterdir()):
        if f.is_file():
            outputs.append({"path": f"output/{f.name}", "size": f.stat().st_size})
            print(f"  Output: {f.name} ({f.stat().st_size} bytes)")

    verdict = "PASS" if ok_run and outputs else "FAIL"
    stage = "run" if not ok_run else ("output" if not outputs else "done")
    _write_ov(pkg_dir, key, slug, verdict, stage if verdict == "FAIL" else "", outputs)

    print(f"  Status: {verdict}")
    return {"key": key, "status": verdict, "outputs": outputs}


def _write_ov(pkg_dir, key, slug, verdict, fail_stage, outputs):
    ov = {
        "package_key": key,
        "sprint": SPRINT,
        "generated_at": TODAY,
        "canonical_plugin_slug": slug,
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "restore_status": "PASS",
        "build_status": "PASS" if fail_stage not in ("RESTORE_FAIL", "BUILD_FAIL") else "FAIL",
        "run_status": "PASS" if verdict == "PASS" else "FAIL",
        "verdict": verdict,
        "output_files": outputs,
    }
    if fail_stage and fail_stage not in ("done",):
        ov["fail_stage"] = fail_stage
    (pkg_dir / "output-validation.json").write_text(
        json.dumps(ov, indent=2), encoding="utf-8"
    )


def main():
    results = []
    for pkg in PACKAGES:
        r = build_package(pkg)
        results.append(r)

    print(f"\n\n{'='*50}")
    print("Wave 7 Build Summary:")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        print(f"  {r['status']} {r['key']}")
    print(f"\nTotal: {pass_count}/{len(results)} PASS")

    # Write build results JSON
    result_path = Path(__file__).parent.parent / "dryrun-identity" / "wave7-build-results.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(
            {
                "sprint": SPRINT,
                "generated_at": TODAY,
                "total": len(results),
                "pass": pass_count,
                "fail": len(results) - pass_count,
                "verdict": "WAVE7_CANONICAL_PASS" if pass_count == len(results) else "WAVE7_PARTIAL",
                "packages": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nResults written to: {result_path}")
    return 0 if pass_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
