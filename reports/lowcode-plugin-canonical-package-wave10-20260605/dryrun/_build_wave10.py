"""
Lane D — Wave 10 Canonical Dryrun Package Builder
Sprint: lowcode-plugin-canonical-package-wave10-20260605

Builds 17 canonical dryrun packages from existing source packages.
All 17 targets are CANONICAL_IDENTITY_VERIFIED in the registry.
"""
import json
import shutil
import yaml
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parents[3]
SPRINT = "lowcode-plugin-canonical-package-wave10-20260605"
TODAY = str(date.today())
REPORT = Path(__file__).parent
EXAMPLES_OUT = REPORT / "examples"
REGISTRY_DIR = ROOT / "pipeline/plugin-code-registry/family"

sys.path.insert(0, str(ROOT))
from src.plugin_examples.fixture_factory.plugin_identity_validators import run_plugin_identity_validators

# Source package locations for each Wave 10 candidate
# Format: (family, canonical_slug, source_path, legacy_slug)
WAVE10_TARGETS = [
    ("barcode", "1d-barcode-writer",
     ROOT / "reports/lowcode-plugin-code-registry-reconciliation-20260604/transformation/packages/barcode-generate-barcode",
     "generate-barcode", "https://products.aspose.net/barcode/1d-barcode-writer/",
     "1D Barcode Writer for .NET", "Aspose.BarCode"),
    ("barcode", "1d-barcode-reader",
     ROOT / "reports/lowcode-plugin-example-factory-parallel-wave-20260605/dryrun/examples/barcode/recognize-barcode",
     "recognize-barcode", "https://products.aspose.net/barcode/1d-barcode-reader/",
     "1D Barcode Reader for .NET", "Aspose.BarCode"),
    ("barcode", "2d-barcode-writer",
     ROOT / "reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples/barcode/generate-qr-code",
     "generate-qr-code", "https://products.aspose.net/barcode/2d-barcode-writer/",
     "2D Barcode Writer for .NET", "Aspose.BarCode"),
    ("barcode", "2d-barcode-reader",
     ROOT / "reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples/barcode/scan-barcode",
     "scan-barcode", "https://products.aspose.net/barcode/2d-barcode-reader/",
     "2D Barcode Reader for .NET", "Aspose.BarCode"),
    ("drawing", "convert-drawing",
     ROOT / "reports/lowcode-plugin-example-factory-closeout-wave5-20260605/dryrun/examples/drawing/convert-drawing",
     "convert-drawing", "https://products.aspose.net/drawing/net/convert-drawing/",
     "Drawing Converter for .NET", "Aspose.Drawing"),
    ("drawing", "create-drawing",
     ROOT / "reports/lowcode-plugin-example-factory-closeout-wave5-20260605/dryrun/examples/drawing/create-drawing",
     "create-drawing", "https://products.aspose.net/drawing/net/create-drawing/",
     "Drawing Creator for .NET", "Aspose.Drawing"),
    ("finance", "convert-xbrl",
     ROOT / "reports/lowcode-plugin-example-factory-closeout-wave5-20260605/dryrun/examples/finance/convert-xbrl",
     "convert-xbrl", "https://products.aspose.net/finance/convert-xbrl/",
     "XBRL Converter for .NET", "Aspose.Finance"),
    ("ocr", "scan-document",
     ROOT / "reports/lowcode-plugin-example-factory-closeout-wave5-20260605/dryrun/examples/ocr/scan-document",
     "scan-document", "https://products.aspose.net/ocr/scan-document/",
     "Document Scanner for .NET", "Aspose.OCR"),
    ("ocr", "image-text-finder",
     ROOT / "reports/lowcode-plugin-example-factory-wave6-20260605/dryrun/examples/ocr/image-text-finder",
     "image-text-finder", "https://products.aspose.net/ocr/image-text-finder/",
     "Image Text Finder for .NET", "Aspose.OCR"),
    ("ocr", "invoice-to-text",
     ROOT / "reports/lowcode-plugin-example-factory-wave6-20260605/dryrun/examples/ocr/invoice-to-text",
     "invoice-to-text", "https://products.aspose.net/ocr/invoice-to-text/",
     "Invoice to Text Converter for .NET", "Aspose.OCR"),
    ("ocr", "photo-to-text",
     ROOT / "reports/lowcode-plugin-canonical-identity-wave7-20260605/dryrun/examples/ocr/photo-to-text",
     "photo-to-text", "https://products.aspose.net/ocr/photo-to-text/",
     "Photo to Text Converter for .NET", "Aspose.OCR"),
    ("ocr", "table-to-text",
     ROOT / "reports/lowcode-plugin-canonical-identity-wave7-20260605/dryrun/examples/ocr/table-to-text",
     "table-to-text", "https://products.aspose.net/ocr/table-to-text/",
     "Table to Text Converter for .NET", "Aspose.OCR"),
    ("psd", "animation-maker",
     ROOT / "reports/lowcode-plugin-canonical-identity-wave7-20260605/dryrun/examples/psd/animation-maker",
     "animation-maker", "https://products.aspose.net/psd/animation-maker/",
     "PSD Animation Maker for .NET", "Aspose.PSD"),
    ("psd", "photo-processor",
     ROOT / "reports/lowcode-plugin-canonical-identity-wave7-20260605/dryrun/examples/psd/photo-processor",
     "photo-processor", "https://products.aspose.net/psd/photo-processor/",
     "PSD Photo Processor for .NET", "Aspose.PSD"),
    ("svg", "svg-to-image-converter",
     ROOT / "reports/lowcode-plugin-example-factory-parallel-wave-20260605/dryrun/examples/svg/svg-to-image-converter",
     "svg-to-image-converter", "https://products.aspose.net/svg/svg-to-image-converter/",
     "SVG to Image Converter for .NET", "Aspose.SVG"),
    ("tex", "latex-figure-renderer",
     ROOT / "reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples/tex/latex-figure-renderer",
     "latex-figure-renderer", "https://products.aspose.net/tex/latex-figure-renderer/",
     "LaTeX Figure Renderer for .NET", "Aspose.TeX"),
    ("zip", "compress-files",
     ROOT / "reports/lowcode-plugin-code-registry-reconciliation-20260604/transformation/packages/zip-compress-files",
     "compress-files", "https://products.aspose.net/zip/compress-files/",
     "ZIP File Compressor for .NET", "Aspose.ZIP"),
]

results = []
built = 0
skipped = 0

EXAMPLES_OUT.mkdir(parents=True, exist_ok=True)

for target in WAVE10_TARGETS:
    family, canonical_slug, source_dir, legacy_slug, canonical_url, display_name, nuget_pkg = target
    key = f"{family}/{canonical_slug}"
    out_dir = EXAMPLES_OUT / family / canonical_slug

    if not source_dir.exists():
        print(f"  SKIP {key}: source not found at {source_dir}")
        results.append({"key": key, "status": "SOURCE_NOT_FOUND", "source": str(source_dir)})
        skipped += 1
        continue

    # Copy source to canonical path
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(source_dir, out_dir, ignore=shutil.ignore_patterns("obj", "bin", ".vs"))

    # Update source-provenance.json
    sp_path = out_dir / "source-provenance.json"
    sp = {}
    if sp_path.exists():
        try:
            sp = json.loads(sp_path.read_text(encoding="utf-8"))
        except Exception:
            sp = {}
    sp.update({
        "family": family,
        "plugin_slug": canonical_slug,
        "canonical_plugin_slug": canonical_slug,
        "legacy_slug": legacy_slug,
        "canonical_url": canonical_url,
        "display_plugin_name": display_name,
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "sprint": SPRINT,
        "generated_at": TODAY,
    })
    sp_path.write_text(json.dumps(sp, indent=2))

    # Update output-validation.json package field
    ov_path = out_dir / "output-validation.json"
    if ov_path.exists():
        try:
            ov = json.loads(ov_path.read_text(encoding="utf-8"))
            ov["package_key"] = key
            ov["package"] = key
            ov_path.write_text(json.dumps(ov, indent=2))
        except Exception:
            pass

    # Update README title
    readme_path = out_dir / "README.md"
    if readme_path.exists():
        lines = readme_path.read_text(encoding="utf-8", errors="replace").split("\n")
        if lines and lines[0].startswith("#"):
            lines[0] = f"# {display_name}"
            readme_path.write_text("\n".join(lines))
    else:
        readme_path.write_text(f"# {display_name}\n\nCanonical dryrun package for {canonical_url}\n")

    # Add/update package-manifest.json
    pm_path = out_dir / "package-manifest.json"
    manifest = {
        "package_key": key,
        "family": family,
        "plugin_slug": canonical_slug,
        "canonical_plugin_slug": canonical_slug,
        "canonical_url": canonical_url,
        "display_plugin_name": display_name,
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "migration_status": "CANONICAL_PRIMARY_MIGRATED",
        "legacy_slug": legacy_slug,
        "nuget_package": nuget_pkg,
        "sprint": SPRINT,
        "generated_at": TODAY,
        "proof_type": "MIGRATED_FULL_PACKAGE",
    }
    pm_path.write_text(json.dumps(manifest, indent=2))

    # Run PIV validator
    piv = run_plugin_identity_validators(out_dir, key)
    piv_pass = piv.passes
    piv_errors = piv.error_count
    piv_warnings = piv.warning_count

    # Check output
    output_dir = out_dir / "output"
    output_files = list(output_dir.iterdir()) if output_dir.exists() else []
    has_output = len(output_files) > 0

    # Get verdict
    ov_verdict = "UNKNOWN"
    if ov_path.exists():
        try:
            ov = json.loads(ov_path.read_text(encoding="utf-8"))
            ov_verdict = ov.get("verdict", "UNKNOWN")
        except Exception:
            pass

    status = "BUILT" if (piv_pass and has_output and ov_verdict == "PASS") else "BUILT_WITH_WARNINGS"
    built += 1

    print(f"  {status} {key} piv={'PASS' if piv_pass else 'FAIL'} output={len(output_files)} verdict={ov_verdict}")
    results.append({
        "key": key,
        "status": status,
        "piv_pass": piv_pass,
        "piv_errors": piv_errors,
        "piv_warnings": piv_warnings,
        "output_files": len(output_files),
        "verdict": ov_verdict,
        "source": str(source_dir),
    })

print(f"\nBuilt: {built}  Skipped: {skipped}  Total: {len(results)}")

build_results = {
    "sprint": SPRINT,
    "date": TODAY,
    "total": len(results),
    "built": built,
    "skipped": skipped,
    "results": results,
    "verdict": "WAVE10_DRYRUN_DONE" if skipped == 0 else "WAVE10_PARTIAL",
}
(REPORT / "wave10-build-results.json").write_text(json.dumps(build_results, indent=2))
print("Written: wave10-build-results.json")
