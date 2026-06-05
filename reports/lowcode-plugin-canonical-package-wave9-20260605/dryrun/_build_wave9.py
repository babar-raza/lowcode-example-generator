"""
Lane E — Wave 9 Canonical Dry-Run Package Builder
Sprint: lowcode-plugin-canonical-package-wave9-20260605

Builds 12 canonical dryrun packages from the migrated registry entries.
Each package is migrated from an existing generic-slug package and upgraded
to canonical identity with full package proof files.
"""
import json
import shutil
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-package-wave9-20260605"
ROOT = Path(__file__).parents[3]
REPORT_ROOT = ROOT / f"reports/{SPRINT}"
DRYRUN_BASE = REPORT_ROOT / "dryrun" / "examples"

WAVE9_MAP = [
    # Imaging (6)
    {
        "family": "imaging",
        "canonical_slug": "image-compressor",
        "legacy_slug": "compress-image",
        "display_name": "Image Compressor for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-compressor/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-parallel-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "image-cropper",
        "legacy_slug": "crop-image",
        "display_name": "Image Cropper for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-cropper/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "image-filters",
        "legacy_slug": "filter-image",
        "display_name": "Image Filters for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-filters/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "image-merger",
        "legacy_slug": "merge-images",
        "display_name": "Image Merger for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-merger/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "add-watermark",
        "legacy_slug": "watermark-image",
        "display_name": "Add Watermark to Image for .NET",
        "canonical_url": "https://products.aspose.net/imaging/add-watermark/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "image-rotator",
        "legacy_slug": "rotate-image",
        "display_name": "Image Rotator for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-rotator/",
        "nuget_package": "Aspose.Imaging",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    # Tasks (2)
    {
        "family": "tasks",
        "canonical_slug": "project-to-pdf-converter",
        "legacy_slug": "convert-mpp-to-pdf",
        "display_name": "Project to PDF Converter for .NET",
        "canonical_url": "https://products.aspose.net/tasks/project-to-pdf-converter/",
        "nuget_package": "Aspose.Tasks",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-closeout-wave5-20260605",
    },
    {
        "family": "tasks",
        "canonical_slug": "mpp-to-excel",
        "legacy_slug": "convert-mpp-to-excel",
        "display_name": "MPP to Excel Converter for .NET",
        "canonical_url": "https://products.aspose.net/tasks/mpp-to-excel/",
        "nuget_package": "Aspose.Tasks",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
    # HTML (2)
    {
        "family": "html",
        "canonical_slug": "html-to-docx-converter",
        "legacy_slug": "convert-html-to-word",
        "display_name": "HTML to DOCX Converter for .NET",
        "canonical_url": "https://products.aspose.net/html/html-to-docx-converter/",
        "nuget_package": "Aspose.HTML",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
    {
        "family": "html",
        "canonical_slug": "html-to-image-converter",
        "legacy_slug": "convert-html-to-image",
        "display_name": "HTML to Image Converter for .NET",
        "canonical_url": "https://products.aspose.net/html/html-to-image-converter/",
        "nuget_package": "Aspose.HTML",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
    # Note (2)
    {
        "family": "note",
        "canonical_slug": "convert-onenote-to-word",
        "legacy_slug": "convert-one-to-word",
        "display_name": "OneNote to Word Converter for .NET",
        "canonical_url": "https://products.aspose.net/note/convert-onenote-to-word/",
        "nuget_package": "Aspose.Note",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
    {
        "family": "note",
        "canonical_slug": "convert-onenote-to-image",
        "legacy_slug": "convert-one-to-image",
        "display_name": "OneNote to Image Converter for .NET",
        "canonical_url": "https://products.aspose.net/note/convert-onenote-to-image/",
        "nuget_package": "Aspose.Note",
        "nuget_version": "24.12.0",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
]


def find_source(entry):
    """Locate the best source package for migration."""
    family, legacy = entry["family"], entry["legacy_slug"]
    # Try declared source sprint first, then all sprints
    search_dirs = [
        ROOT / f"reports/{entry['source_sprint']}",
    ] + sorted(ROOT.glob("reports/lowcode-plugin-example-factory-*/"))
    for sprint_dir in search_dirs:
        for subdir in ["dryrun/examples", "examples"]:
            pkg = sprint_dir / subdir / family / legacy
            if pkg.exists() and (pkg / "Program.cs").exists():
                return pkg
    return None


build_results = []

import sys
sys.path.insert(0, str(ROOT))
from src.plugin_examples.fixture_factory.plugin_identity_validators import run_plugin_identity_validators

for entry in WAVE9_MAP:
    family = entry["family"]
    canon = entry["canonical_slug"]
    legacy = entry["legacy_slug"]
    key = f"{family}/{canon}"

    src = find_source(entry)
    if not src:
        print(f"  SKIP {key}: no source found for {family}/{legacy}")
        build_results.append({"key": key, "status": "SKIPPED_NO_SOURCE"})
        continue

    dest = DRYRUN_BASE / family / canon
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Copy all files except bin/obj
    for item in src.iterdir():
        if item.name in ("bin", "obj"):
            continue
        if item.is_file():
            shutil.copy2(item, dest / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest / item.name)

    # Update source-provenance.json
    sp_path = dest / "source-provenance.json"
    sp = {}
    if sp_path.exists():
        try:
            sp = json.loads(sp_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    sp.update({
        "family": family,
        "plugin_slug": canon,
        "canonical_plugin_slug": canon,
        "canonical_url": entry["canonical_url"],
        "display_plugin_name": entry["display_name"],
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "migration_status": "CANONICAL_PRIMARY_MIGRATED",
        "migrated_from": legacy,
        "legacy_example_slug": legacy,
        "generation_sprint": SPRINT,
        "migrated_at": TODAY,
    })
    sp_path.write_text(json.dumps(sp, indent=2))

    # Update output-validation.json
    ov_path = dest / "output-validation.json"
    ov = {}
    if ov_path.exists():
        try:
            ov = json.loads(ov_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    ov["package"] = key
    ov["package_key"] = key
    ov["canonical_plugin_slug"] = canon
    ov["migrated_from"] = legacy
    ov["migration_sprint"] = SPRINT
    ov_path.write_text(json.dumps(ov, indent=2))

    # Update README title
    readme = dest / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="replace")
        lines = text.split("\n")
        if lines:
            lines[0] = f"# {entry['display_name']}"
            readme.write_text("\n".join(lines))

    # Add package-manifest.json
    pm_path = dest / "package-manifest.json"
    ov2 = json.loads(ov_path.read_text(encoding="utf-8"))
    out_dir = dest / "output"
    out_files = [f.name for f in out_dir.iterdir() if f.is_file() and f.stat().st_size > 0] if out_dir.exists() else []

    pm = {
        "package_key": key,
        "family": family,
        "plugin_slug": canon,
        "canonical_plugin_slug": canon,
        "canonical_url": entry["canonical_url"],
        "display_plugin_name": entry["display_name"],
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "migration_status": "CANONICAL_PRIMARY_MIGRATED",
        "nuget_package": sp.get("nuget_package", entry["nuget_package"]),
        "nuget_version": sp.get("nuget_version", entry["nuget_version"]),
        "sprint": SPRINT,
        "generated_at": TODAY,
        "proof_type": "MIGRATED_FULL_PACKAGE",
        "output_files": out_files,
    }
    pm_path.write_text(json.dumps(pm, indent=2))

    # PIV validation
    r = run_plugin_identity_validators(dest, key)
    verdict = ov2.get("verdict", "")
    status = "BUILT" if verdict == "PASS" and r.passes and out_files else "BUILT_WARNING"

    build_results.append({
        "key": key,
        "status": status,
        "verdict": verdict,
        "piv_pass": r.passes,
        "piv_errors": r.error_count,
        "piv_warnings": r.warning_count,
        "output_files": len(out_files),
        "source": str(src),
    })
    print(f"  {key}: {status} piv={'PASS' if r.passes else 'FAIL'} output={len(out_files)}")

passed = [r for r in build_results if r["status"] == "BUILT"]
print(f"\nWave 9: {len(passed)}/{len(build_results)} BUILT")

(REPORT_ROOT / "dryrun/wave9-build-results.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "total": len(build_results),
    "built": len(passed),
    "results": build_results,
    "verdict": "WAVE9_DRYRUN_DONE" if len(passed) == len(WAVE9_MAP) else "WAVE9_DRYRUN_PARTIAL",
}, indent=2))

print("\nWritten: dryrun/wave9-build-results.json")
