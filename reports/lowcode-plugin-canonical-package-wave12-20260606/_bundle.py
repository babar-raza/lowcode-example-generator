"""Create evidence bundle ZIP for Wave 12 sprint."""
import zipfile
import hashlib
from pathlib import Path

SPRINT = "lowcode-plugin-canonical-package-wave12-20260606"
W11_SPRINT = "lowcode-plugin-canonical-package-wave11-20260605"
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
    # Wave 11 closeout repair files (commit proofs, git status)
    f"reports/{SPRINT}/wave11-closeout-repair/*.txt",
    # Wave 11 taskcards repair (DEFECT-01 fix)
    f"reports/{W11_SPRINT}/coordinator/taskcards.json",
    # Registry changes (SVG package proven)
    "pipeline/plugin-code-registry/family/svg.yaml",
    # New validators
    "src/plugin_examples/fixture_factory/taskcard_closeout_validators.py",
    "tests/unit/test_taskcard_closeout_validators.py",
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
