"""Build Final Publication Closure evidence ZIP bundle."""
import json
import zipfile
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sprint_dir = repo_root / "reports" / "final-publication"
bundles_dir = sprint_dir / "bundles"
bundles_dir.mkdir(exist_ok=True)

bundle_name = "final-publication-closure-evidence-20260527.zip"
zip_path = bundles_dir / bundle_name

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
print(json.dumps({"bundle_name": bundle_name, "file_count": len(files_to_include)}, indent=2))
