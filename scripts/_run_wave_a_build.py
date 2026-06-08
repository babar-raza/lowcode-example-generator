"""Run dotnet build+run for all Wave A packages and record results."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.plugin_examples.example_factory.generator import ExamplePackageGenerator

DRYRUN_ROOT = Path(__file__).parents[1] / "reports" / "lowcode-plugin-example-factory-wave-20260605" / "dryrun" / "examples"

WAVE_A_SLUGS = [
    ("barcode", "generate-qr-code"),
    ("barcode", "scan-barcode"),
    ("svg", "svg-to-pdf-converter"),
    ("tex", "latex-figure-renderer"),
    ("zip", "create-archive"),
    ("zip", "compress-folder"),
    ("imaging", "resize-image"),
    ("imaging", "crop-image"),
    ("imaging", "filter-image"),
    ("imaging", "merge-images"),
    ("imaging", "watermark-image"),
    ("imaging", "rotate-image"),
]

gen = ExamplePackageGenerator(DRYRUN_ROOT)
results = []

for family, slug in WAVE_A_SLUGS:
    pkg_dir = DRYRUN_ROOT / family / slug
    if not pkg_dir.exists():
        print(f"SKIP (not found): {family}/{slug}")
        continue
    print(f"  Running: {family}/{slug} ...", end=" ", flush=True)
    result = gen.build_and_run(pkg_dir)
    verdict = result["verdict"]
    print(verdict)
    results.append({
        "key": f"{family}/{slug}",
        "pkg_dir": str(pkg_dir),
        "verdict": verdict,
        "restore": result["restore"]["status"] if result["restore"] else "N/A",
        "build": result["build"]["status"] if result["build"] else "N/A",
        "run": result["run"]["status"] if result["run"] else "N/A",
        "output_files": result["output_files"],
    })

# Summary
passes = sum(1 for r in results if r["verdict"] == "PASS")
fails = len(results) - passes
print(f"\n{'='*50}")
print(f"Wave A Build Results: {passes}/{len(results)} PASS, {fails} FAIL")

for r in results:
    status = "PASS" if r["verdict"] == "PASS" else "FAIL"
    print(f"  {status} {r['key']}: {r['verdict']}")

# Write summary
summary_path = Path(__file__).parents[1] / "reports" / "lowcode-plugin-example-factory-wave-20260605" / "dryrun" / "wave-a-build-results.json"
summary_path.write_text(json.dumps({
    "sprint": "lowcode-plugin-example-factory-wave-20260605",
    "wave": "A",
    "total": len(results),
    "pass": passes,
    "fail": fails,
    "packages": results,
}, indent=2), encoding="utf-8")
print(f"\nResults: {summary_path}")
