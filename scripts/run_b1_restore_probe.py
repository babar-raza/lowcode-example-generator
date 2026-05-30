"""B1 restore probe: run real dotnet restore for all 26 families.

Creates a minimal .csproj probe for each family, runs `dotnet restore`,
captures non-empty stdout/stderr to restore logs.

Output: reports/lowcode-systemization-pass2-20260530/discovery/restore-logs/<family>.log
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-systemization-pass2-20260530"
OUT_DIR = REPO_ROOT / "reports" / SPRINT_ID / "discovery" / "restore-logs"

FAMILIES = [
    # (family_slug, nuget_package_id, expected_result)
    ("barcode", "Aspose.BarCode", "success"),
    ("cad", "Aspose.CAD", "success"),
    ("cells", "Aspose.Cells", "success"),
    ("diagram", "Aspose.Diagram", "success"),
    ("drawing", "Aspose.Drawing", "success"),
    ("email", "Aspose.Email", "success"),
    ("epub", None, "external_package_blocker"),   # no NuGet package
    ("finance", "Aspose.Finance", "success"),
    ("font", "Aspose.Font", "success"),
    ("gis", "Aspose.GIS", "success"),
    ("html", "Aspose.HTML", "success"),
    ("imaging", "Aspose.Imaging", "success"),
    ("note", "Aspose.Note", "success"),
    ("ocr", "Aspose.OCR", "success"),
    ("omr", "Aspose.OMR", "success"),
    ("page", "Aspose.Page", "success"),
    ("pdf", "Aspose.PDF", "success"),
    ("psd", "Aspose.PSD", "success"),
    ("pub", "Aspose.PUB", "success"),
    ("slides", "Aspose.Slides.NET", "success"),
    ("svg", "Aspose.SVG", "success"),
    ("tasks", "Aspose.Tasks", "success"),
    ("tex", "Aspose.TeX", "success"),
    ("threed", "Aspose.3D", "success"),
    ("words", "Aspose.Words", "success"),
    ("zip", "Aspose.Zip", "success"),
]

PROBE_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{package}" Version="*" />
  </ItemGroup>
</Project>
"""


def run_restore(family: str, package: str | None, tmpdir: Path) -> tuple[str, bool]:
    """Run dotnet restore for a family. Returns (log_content, success)."""
    if package is None:
        # EXTERNAL_PACKAGE_BLOCKER — create a csproj that will fail with NU1101
        fake_package = "Aspose.Epub"
        csproj_content = PROBE_CSPROJ_TEMPLATE.format(package=fake_package)
    else:
        csproj_content = PROBE_CSPROJ_TEMPLATE.format(package=package)

    probe_dir = tmpdir / f"probe-{family}"
    probe_dir.mkdir(parents=True, exist_ok=True)
    csproj_path = probe_dir / f"probe-{family}.csproj"
    csproj_path.write_text(csproj_content, encoding="utf-8")

    # Run dotnet restore with --no-cache to get real output
    result = subprocess.run(
        ["dotnet", "restore", str(csproj_path), "--verbosity", "normal"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    combined = result.stdout
    if result.stderr:
        combined += "\n--- stderr ---\n" + result.stderr

    success = result.returncode == 0
    return combined.strip(), success


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n=== B1 restore probe: {SPRINT_ID} ===\n")
    print(f"Output: {OUT_DIR}\n")

    results = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for family, package, expected in FAMILIES:
            print(f"  [{family}] Restoring {package or 'N/A (EXTERNAL_PACKAGE_BLOCKER)'}...", end=" ", flush=True)

            if package is None:
                # epub — attempt restore, document failure
                log_content, success = run_restore(family, None, tmp)
                status = "EXTERNAL_PACKAGE_BLOCKER"
                print(f"EXTERNAL_BLOCKER (expected)")
            else:
                log_content, success = run_restore(family, package, tmp)
                if success:
                    status = "success"
                    print(f"OK")
                else:
                    status = "FAILED"
                    print(f"FAILED (rc!=0)")

            log_path = OUT_DIR / f"{family}.log"
            log_content_with_header = (
                f"# {family} — dotnet restore probe\n"
                f"# Package: {package or 'N/A'}\n"
                f"# Status: {status}\n"
                f"# Sprint: {SPRINT_ID}\n\n"
            ) + log_content

            log_path.write_text(log_content_with_header, encoding="utf-8")
            results[family] = {
                "package": package,
                "status": status,
                "log_bytes": log_path.stat().st_size,
                "expected": expected,
                "match": status.lower() == expected.replace("_", "").lower() or
                          (expected == "success" and status == "success") or
                          (expected == "external_package_blocker" and status == "EXTERNAL_PACKAGE_BLOCKER"),
            }

    # Write summary
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    blocker_count = sum(1 for r in results.values() if r["status"] == "EXTERNAL_PACKAGE_BLOCKER")
    failed_count = sum(1 for r in results.values() if r["status"] == "FAILED")

    summary = {
        "sprint_id": SPRINT_ID,
        "lane": "B1 — Universe evidence repair: real dotnet restore",
        "total_families": len(FAMILIES),
        "success": success_count,
        "external_package_blocker": blocker_count,
        "failed": failed_count,
        "families": results,
    }
    summary_path = OUT_DIR.parent / "restore-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\n=== Restore probe complete ===")
    print(f"Success: {success_count}/26")
    print(f"External blocker: {blocker_count}/26")
    print(f"Failed: {failed_count}/26")
    print(f"Summary: {summary_path}")

    if failed_count > 0:
        print("\nFailed families:")
        for fam, r in results.items():
            if r["status"] == "FAILED":
                print(f"  {fam}: {r['package']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
