"""Create evidence bundle ZIP for Wave 9 sprint."""
import zipfile
import hashlib
from pathlib import Path

SPRINT = "lowcode-plugin-canonical-package-wave9-20260605"
WAVE8_SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
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
    # Wave 8 repaired files
    f"reports/{WAVE8_SPRINT}/coordinator/lane-ledger.json",
    f"reports/{WAVE8_SPRINT}/taskcards/taskcards.json",
    f"reports/{WAVE8_SPRINT}/sprint-closeout.json",
    f"reports/{WAVE8_SPRINT}/wave8/dryrun/examples/**/package-manifest.json",
    f"reports/{WAVE8_SPRINT}/wave8/dryrun/examples/**/output-validation.json",
    # Registry changes
    "pipeline/plugin-code-registry/family/drawing.yaml",
    "pipeline/plugin-code-registry/family/finance.yaml",
    "pipeline/plugin-code-registry/family/html.yaml",
    "pipeline/plugin-code-registry/family/imaging.yaml",
    "pipeline/plugin-code-registry/family/note.yaml",
    "pipeline/plugin-code-registry/family/ocr.yaml",
    "pipeline/plugin-code-registry/family/psd.yaml",
    "pipeline/plugin-code-registry/family/svg.yaml",
    "pipeline/plugin-code-registry/family/tasks.yaml",
    "pipeline/plugin-code-registry/family/tex.yaml",
    "pipeline/plugin-code-registry/family/zip.yaml",
    # Validators and tests
    "src/plugin_examples/fixture_factory/full_package_proof_validator.py",
    "src/plugin_examples/fixture_factory/closeout_consistency_validators.py",
    "tests/unit/test_full_package_proof_validator.py",
    "tests/unit/test_closeout_consistency_validators.py",
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
