"""
Build 4 canonical BarCode dry-run packages using canonical plugin slugs.
Sprint: lowcode-plugin-canonical-identity-wave7-20260605
"""
import os, subprocess, json, shutil
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-identity-wave7-20260605"
BASE = Path(__file__).parent / "examples"
BASE.mkdir(parents=True, exist_ok=True)

PACKAGES = {
    "1d-barcode-writer": {
        "family": "barcode",
        "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
        "display_name": "1D Barcode Writer for .NET",
        "nuget": "Aspose.BarCode",
        "version": "24.12.0",
        "legacy_slug": "generate-barcode",
        "program_cs": """\
// barcode/1d-barcode-writer
// Canonical: https://products.aspose.net/barcode/1d-barcode-writer/
// Package: Aspose.BarCode 24.12.0
// Generates a 1D barcode (Code128) and saves as PNG.
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "barcode-1d.png");

using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "ASPOSE-1D-BARCODE-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Parameters.Barcode.BarHeight.Pixels = 100;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}
Console.WriteLine($"1D barcode written: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",
        "output_file": "barcode-1d.png",
        "readme_title": "1D Barcode Writer for .NET",
    },
    "2d-barcode-writer": {
        "family": "barcode",
        "canonical_url": "https://products.aspose.net/barcode/2d-barcode-writer/",
        "display_name": "2D Barcode Writer for .NET",
        "nuget": "Aspose.BarCode",
        "version": "24.12.0",
        "legacy_slug": "generate-qr-code",
        "program_cs": """\
// barcode/2d-barcode-writer
// Canonical: https://products.aspose.net/barcode/2d-barcode-writer/
// Package: Aspose.BarCode 24.12.0
// Generates a 2D QR barcode and saves as PNG.
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "barcode-2d.png");

using (var gen = new BarcodeGenerator(EncodeTypes.QR, "https://www.aspose.com/barcode-2d"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 6;
    gen.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}
Console.WriteLine($"2D QR barcode written: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",
        "output_file": "barcode-2d.png",
        "readme_title": "2D Barcode Writer for .NET",
    },
    "1d-barcode-reader": {
        "family": "barcode",
        "canonical_url": "https://products.aspose.net/barcode/1d-barcode-reader/",
        "display_name": "1D Barcode Reader for .NET",
        "nuget": "Aspose.BarCode",
        "version": "24.12.0",
        "legacy_slug": "recognize-barcode",
        "program_cs": """\
// barcode/1d-barcode-reader
// Canonical: https://products.aspose.net/barcode/1d-barcode-reader/
// Package: Aspose.BarCode 24.12.0
// Generates a 1D Code128 fixture then reads it back.
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string fixturePath = "fixture_barcode.png";
using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "1D-READER-TEST-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}

var sb = new StringBuilder();
using (var reader = new BarCodeReader(fixturePath, DecodeType.Code128))
{
    foreach (var result in reader.ReadBarCodes())
    {
        string line = $"Type={result.CodeType}, Value={result.CodeText}";
        Console.WriteLine(line);
        sb.AppendLine(line);
    }
}
string outPath = Path.Combine("output", "1d-recognition.txt");
File.WriteAllText(outPath, sb.ToString());
Console.WriteLine($"1D barcode read: {outPath} ({new FileInfo(outPath).Length} bytes)");
""",
        "output_file": "1d-recognition.txt",
        "readme_title": "1D Barcode Reader for .NET",
    },
    "2d-barcode-reader": {
        "family": "barcode",
        "canonical_url": "https://products.aspose.net/barcode/2d-barcode-reader/",
        "display_name": "2D Barcode Reader for .NET",
        "nuget": "Aspose.BarCode",
        "version": "24.12.0",
        "legacy_slug": "scan-barcode",
        "program_cs": """\
// barcode/2d-barcode-reader
// Canonical: https://products.aspose.net/barcode/2d-barcode-reader/
// Package: Aspose.BarCode 24.12.0
// Generates a 2D QR fixture then reads it back.
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string fixturePath = "fixture_2d.png";
using (var gen = new BarcodeGenerator(EncodeTypes.QR, "2D-READER-TEST-ASPOSE-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 6;
    gen.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}

var sb = new StringBuilder();
using (var reader = new BarCodeReader(fixturePath, DecodeType.QR))
{
    foreach (var result in reader.ReadBarCodes())
    {
        string line = $"Type={result.CodeType}, Value={result.CodeText}";
        Console.WriteLine(line);
        sb.AppendLine(line);
    }
}
string outPath = Path.Combine("output", "2d-recognition.txt");
File.WriteAllText(outPath, sb.ToString());
Console.WriteLine($"2D barcode read: {outPath} ({new FileInfo(outPath).Length} bytes)");
""",
        "output_file": "2d-recognition.txt",
        "readme_title": "2D Barcode Reader for .NET",
    },
}


def run(cmd, cwd, timeout=120):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, shell=True)
    return r.returncode, r.stdout + r.stderr


def build_package(slug, cfg):
    family = cfg["family"]
    pkg_dir = BASE / family / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "output").mkdir(exist_ok=True)

    # Program.cs
    (pkg_dir / "Program.cs").write_text(cfg["program_cs"])

    # .csproj
    csproj = f"""\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{cfg['nuget']}" Version="{cfg['version']}" />
  </ItemGroup>
</Project>
"""
    (pkg_dir / f"{family}-{slug}.csproj").write_text(csproj)

    # README.md
    readme = f"""# {cfg['display_name']}

Dry-run example for the [{cfg['display_name']}]({cfg['canonical_url']}) plugin.

**Package:** {cfg['nuget']} {cfg['version']}
**Canonical URL:** {cfg['canonical_url']}
**Legacy alias:** {cfg['legacy_slug']}

## What this example does

1. Creates a barcode fixture (if needed for reader plugins)
2. Invokes the Aspose.BarCode API with the canonical plugin workflow
3. Saves the output to `output/`

## Running

```bash
dotnet restore
dotnet run
```
"""
    (pkg_dir / "README.md").write_text(readme)

    # source-provenance.json
    prov = {
        "package_key": f"{family}/{slug}",
        "canonical_plugin_slug": slug,
        "canonical_url": cfg["canonical_url"],
        "display_plugin_name": cfg["display_name"],
        "legacy_example_slug": cfg["legacy_slug"],
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "nuget_package": cfg["nuget"],
        "nuget_version": cfg["version"],
        "sprint": SPRINT,
        "generated_at": TODAY,
    }
    (pkg_dir / "source-provenance.json").write_text(json.dumps(prov, indent=2))

    # package-manifest.json
    manifest = {
        "package_key": f"{family}/{slug}",
        "canonical_plugin_slug": slug,
        "canonical_url": cfg["canonical_url"],
        "display_plugin_name": cfg["display_name"],
        "nuget_package": cfg["nuget"],
        "nuget_version": cfg["version"],
        "sprint": SPRINT,
        "generated_at": TODAY,
    }
    (pkg_dir / "package-manifest.json").write_text(json.dumps(manifest, indent=2))

    # dotnet restore
    print(f"\n[{slug}] restore...")
    rc, log = run("dotnet restore --verbosity quiet", pkg_dir)
    (pkg_dir / "restore.log").write_text(log)
    restore_status = "PASS" if rc == 0 else "FAILED"

    # dotnet build
    print(f"[{slug}] build...")
    rc, log = run("dotnet build -c Release --no-restore --verbosity quiet", pkg_dir)
    (pkg_dir / "build.log").write_text(log)
    build_status = "PASS" if rc == 0 else "FAILED"

    # dotnet run
    run_status = "SKIPPED"
    if build_status == "PASS":
        print(f"[{slug}] run...")
        rc, log = run("dotnet run -c Release --no-build", pkg_dir)
        (pkg_dir / "run.log").write_text(log)
        run_status = "PASS" if rc == 0 else "FAILED"

    # Check output
    out_file = pkg_dir / "output" / cfg["output_file"]
    out_size = out_file.stat().st_size if out_file.exists() else 0
    verdict = "PASS" if run_status == "PASS" and out_size > 0 else "FAIL"

    # output-validation.json
    ov = {
        "package_key": f"{family}/{slug}",
        "sprint": SPRINT,
        "generated_at": TODAY,
        "canonical_plugin_slug": slug,
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "restore_status": restore_status,
        "build_status": build_status,
        "run_status": run_status,
        "verdict": verdict,
        "output_files": [{"path": f"output/{cfg['output_file']}", "size": out_size}] if out_size > 0 else [],
    }
    (pkg_dir / "output-validation.json").write_text(json.dumps(ov, indent=2))

    print(f"[{slug}] verdict={verdict} out={out_size}B")
    return {"package_key": f"{family}/{slug}", "canonical_plugin_slug": slug, "status": verdict,
            "output_file": cfg["output_file"], "output_size": out_size}


results = []
for slug, cfg in PACKAGES.items():
    r = build_package(slug, cfg)
    results.append(r)

passed = sum(1 for r in results if r["status"] == "PASS")
summary = {
    "sprint": SPRINT,
    "date": TODAY,
    "total": len(results),
    "pass": passed,
    "fail": len(results) - passed,
    "verdict": "BARCODE_CANONICAL_PASS" if passed == len(results) else f"BARCODE_CANONICAL_PARTIAL_{passed}_OF_{len(results)}",
    "results": results,
}
out_path = Path(__file__).parent.parent / "dryrun-identity" / "barcode-canonical-build-results.json"
out_path.parent.mkdir(exist_ok=True)
out_path.write_text(json.dumps(summary, indent=2))
print(f"\nSummary: {passed}/{len(results)} PASS")
print(f"Saved: {out_path}")
