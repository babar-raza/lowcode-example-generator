"""Build Healing Sprint 1E final artifact evidence ZIP bundle.

MANDATORY FINAL ARTIFACT CONVENTION:
- All commits happen first. ZIP is built last. No commit after ZIP build.
- artifact_build_head_sha = git rev-parse HEAD at build time = final_commit_sha
"""
import json, subprocess, zipfile
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sprint_dir = repo_root / "reports" / "healing-sprint-1e"
bundles_dir = sprint_dir / "bundles"
bundles_dir.mkdir(exist_ok=True)

bundle_name = "healing-sprint-1e-final-artifact-evidence-20260527.zip"
zip_path = bundles_dir / bundle_name

# Capture HEAD SHA at ZIP build time -- must equal final_commit_sha
head_sha = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
).strip()

files_to_include = [
    f for f in sorted(sprint_dir.rglob("*"))
    if f.is_file() and "bundles" not in f.parts and not f.name.endswith(".zip")
]

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in files_to_include:
        zf.write(f, f.relative_to(repo_root))

file_count = len(files_to_include)

print(f"Bundle: {zip_path}")
print(f"artifact_build_head_sha (git rev-parse HEAD): {head_sha}")
print(f"Files included: {file_count}")
for f in files_to_include:
    print(f"  {f.relative_to(repo_root)}")

result = {
    "bundle_name": bundle_name,
    "artifact_build_head_sha": head_sha,
    "file_count": file_count
}
print(json.dumps(result, indent=2))

# Verify no placeholder tokens remain in ZIP
placeholder_found = False
with zipfile.ZipFile(zip_path, "r") as zf:
    for name in zf.namelist():
        content = zf.read(name).decode("utf-8", errors="replace")
        if "SHA1_PLACEHOLDER" in content or "ZIP_COUNT_PLACEHOLDER" in content:
            print(f"WARNING: placeholder token found in {name}")
            placeholder_found = True

if not placeholder_found:
    print("Placeholder check: CLEAN -- no SHA1_PLACEHOLDER or ZIP_COUNT_PLACEHOLDER in ZIP")
else:
    print("ERROR: placeholder tokens found in ZIP -- update files on disk and rebuild")
