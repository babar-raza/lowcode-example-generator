"""Build Sprint 91 final authority closeout evidence ZIP bundle."""
import json
import zipfile
from pathlib import Path
from datetime import datetime

repo_root = Path(__file__).resolve().parents[1]
sprint_dir = repo_root / "reports" / "sprint91"
bundles_dir = sprint_dir / "bundles"
bundles_dir.mkdir(exist_ok=True)

timestamp = "20260527"
bundle_name = f"sprint91-final-authority-closeout-evidence-{timestamp}.zip"
zip_path = bundles_dir / bundle_name

# Collect all Sprint 91 files (excluding bundles/ dir and .zip files)
files_to_include = []
for f in sorted(sprint_dir.rglob("*")):
    if f.is_file() and "bundles" not in f.parts and not f.name.endswith(".zip"):
        files_to_include.append(f)

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in files_to_include:
        arcname = f.relative_to(repo_root)
        zf.write(f, arcname)

print(f"Bundle: {zip_path}")
print(f"Files included: {len(files_to_include)}")

# Return info for bundle-manifest
info = {
    "bundle_path": str(zip_path),
    "file_count": len(files_to_include),
    "timestamp": timestamp,
    "bundle_name": bundle_name,
}
print(json.dumps(info, indent=2))
