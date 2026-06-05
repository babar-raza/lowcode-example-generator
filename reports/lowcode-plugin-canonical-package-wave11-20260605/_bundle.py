"""Create evidence bundle ZIP for Wave 11 sprint."""
import zipfile
import hashlib
from pathlib import Path

SPRINT = "lowcode-plugin-canonical-package-wave11-20260605"
ROOT = Path(__file__).parents[2]
OUT_ZIP = ROOT / f".local/evidence-bundles/{SPRINT}.zip"
OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)

INCLUDE_PATTERNS = [
    f"reports/{SPRINT}/**/*.json",
    f"reports/{SPRINT}/**/*.md",
    f"reports/{SPRINT}/**/*.py",
    f"reports/{SPRINT}/**/*.txt",
    f"reports/{SPRINT}/**/*.cs",
    f"reports/{SPRINT}/**/*.csproj",
    f"reports/{SPRINT}/**/*.log",
    # Wave 10 repaired packages (new logs added)
    "reports/lowcode-plugin-canonical-package-wave10-20260605/dryrun/examples/barcode/1d-barcode-writer/*.log",
    "reports/lowcode-plugin-canonical-package-wave10-20260605/dryrun/examples/zip/compress-files/*.log",
    # Registry changes (slug alias resolution + CIV upgrades)
    "pipeline/plugin-code-registry/family/psd.yaml",
    "pipeline/plugin-code-registry/family/svg.yaml",
    "pipeline/plugin-code-registry/family/gis.yaml",
    # Validators and tests
    "src/plugin_examples/fixture_factory/registry_bundle_completeness_validators.py",
    "tests/unit/test_registry_bundle_completeness_validators.py",
    # Skills
    "skills/canonical-plugin-identity-and-aliasing.md",
]

entries = set()
for pattern in INCLUDE_PATTERNS:
    for f in sorted(ROOT.glob(pattern)):
        if f.is_file() and "bin" not in f.parts and "obj" not in f.parts:
            entries.add(f)

entries = sorted(entries)

with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for f in entries:
        rel = f.relative_to(ROOT)
        zf.write(f, str(rel))

data = OUT_ZIP.read_bytes()
sha = hashlib.sha256(data).hexdigest()
size = OUT_ZIP.stat().st_size

print(f"ZIP: {OUT_ZIP}")
print(f"SHA-256: {sha}")
print(f"Size: {size:,} bytes, {len(entries)} entries")
