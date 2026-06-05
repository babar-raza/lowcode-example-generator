"""Create evidence bundle ZIP for sprint."""
import zipfile
import hashlib
from pathlib import Path

SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
ROOT = Path(__file__).parents[2]
OUT_ZIP = ROOT / f".local/evidence-bundles/{SPRINT}.zip"
OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)

INCLUDE_PATTERNS = [
    f"reports/{SPRINT}/**/*.json",
    f"reports/{SPRINT}/**/*.md",
    f"reports/{SPRINT}/**/*.py",
    "src/plugin_examples/plugin_code_registry/models.py",
    "src/plugin_examples/plugin_code_registry/loader.py",
    "src/plugin_examples/fixture_factory/canonical_primary_validators.py",
    "tests/unit/test_canonical_primary_validators.py",
    "skills/canonical-plugin-identity-and-aliasing.md",
    "pipeline/plugin-code-registry/family/barcode.yaml",
    "pipeline/plugin-code-registry/family/ocr.yaml",
    "pipeline/plugin-code-registry/family/psd.yaml",
    "pipeline/plugin-code-registry/family/imaging.yaml",
    "pipeline/plugin-code-registry/family/html.yaml",
    "pipeline/plugin-code-registry/family/note.yaml",
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
