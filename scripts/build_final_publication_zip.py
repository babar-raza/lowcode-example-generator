"""
2-pass ZIP builder for lowcode-final-publication-20260601 sprint.
Pass 1: Collect all files, compute SHA-256, write artifact-verification.
Pass 2: Rebuild ZIP including artifact-verification file.
"""
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORT_DIR = REPO / "reports" / "lowcode-final-publication-20260601"
LOCAL_DIR = REPO / ".local" / "evidence-bundles"
ZIP_NAME = "lowcode-final-publication-20260601-evidence.zip"
ZIP_PATH = LOCAL_DIR / ZIP_NAME
SPRINT = "lowcode-final-publication-20260601"

def collect_files():
    """Collect all files to include in the ZIP."""
    files = []

    # 1. Reports directory (all sprint evidence)
    for p in sorted(REPORT_DIR.rglob("*")):
        if p.is_file() and ".zip" not in p.name:
            arcname = f"reports/{p.relative_to(REPORT_DIR)}"
            files.append((str(p), arcname.replace("\\", "/")))

    # 2. Format-authority contracts
    contracts_dir = REPO / "pipeline" / "format-authority" / "contracts"
    for p in sorted(contracts_dir.glob("*.json")):
        files.append((str(p), f"format-authority/contracts/{p.name}"))

    # 3. Completion queue
    queue = REPO / "workspace" / "queues" / "example-completion-queue.json"
    if queue.exists():
        files.append((str(queue), "completion-queue/example-completion-queue.json"))

    # 4. Generated source snapshots (Program.cs + csproj for all publishable)
    manifest_path = REPORT_DIR / "package-artifacts" / "package-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for ex in manifest.get("examples", []):
            ex_dir = Path(ex["dir"])
            for f in ex_dir.iterdir():
                if f.is_file() and f.suffix in (".cs", ".csproj"):
                    arcname = f"generated-source/{ex['family']}/{ex['name']}/{f.name}"
                    files.append((str(f), arcname))

    # 5. Scripts
    for script in sorted((REPO / "scripts").glob("*.py")):
        if "final_publication" in script.name:
            files.append((str(script), f"scripts/{script.name}"))

    # 6. Blocker evidence from system-repair sprint
    blockers_dir = REPO / "reports" / "lowcode-system-repair-20260601" / "blockers"
    if blockers_dir.exists():
        for p in sorted(blockers_dir.rglob("*")):
            if p.is_file():
                arcname = f"blocker-evidence/{p.relative_to(blockers_dir)}"
                files.append((str(p), arcname.replace("\\", "/")))

    return files

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def build_zip(files, include_verification=None):
    """Build ZIP from file list, optionally adding verification data."""
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for filepath, arcname in files:
            zf.write(filepath, arcname)
        if include_verification:
            zf.writestr("artifact-metadata/artifact-verification.json",
                        json.dumps(include_verification, indent=2))
            zf.writestr("artifact-metadata/bundle-manifest.json",
                        json.dumps({
                            "sprint": SPRINT,
                            "built_at": datetime.now(timezone.utc).isoformat(),
                            "total_entries": len(files) + 2,
                            "verification_included": True,
                        }, indent=2))

def main():
    print(f"Sprint: {SPRINT}")
    print(f"Report dir: {REPORT_DIR}")
    print()

    files = collect_files()
    print(f"Pass 1: Collected {len(files)} files")

    # Pass 1: Build ZIP without verification
    build_zip(files)
    pass1_sha = compute_sha256(ZIP_PATH)
    pass1_size = ZIP_PATH.stat().st_size
    print(f"Pass 1 SHA-256: {pass1_sha}")
    print(f"Pass 1 size: {pass1_size} bytes")

    # Write file list
    file_list_path = REPORT_DIR / "artifact" / "zip-file-list.txt"
    file_list_path.parent.mkdir(parents=True, exist_ok=True)
    file_list_path.write_text("\n".join(arcname for _, arcname in files), encoding="utf-8")

    # Pass 2: Rebuild with verification
    verification = {
        "sprint": SPRINT,
        "zip_name": ZIP_NAME,
        "pass1_sha256": pass1_sha,
        "pass1_size": pass1_size,
        "pass1_entries": len(files),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "builder": "scripts/build_final_publication_zip.py",
    }

    build_zip(files, include_verification=verification)
    pass2_sha = compute_sha256(ZIP_PATH)
    pass2_size = ZIP_PATH.stat().st_size
    print(f"\nPass 2 SHA-256: {pass2_sha}")
    print(f"Pass 2 size: {pass2_size} bytes")

    # Write final verification
    final_verification = {
        "sprint": SPRINT,
        "zip_name": ZIP_NAME,
        "zip_path": str(ZIP_PATH),
        "pass1_sha256": pass1_sha,
        "pass1_size": pass1_size,
        "pass2_sha256": pass2_sha,
        "pass2_size": pass2_size,
        "total_entries": len(files) + 2,  # +2 for artifact-metadata files
        "built_at": datetime.now(timezone.utc).isoformat(),
    }
    verify_path = REPORT_DIR / "artifact" / "artifact-verification.json"
    verify_path.write_text(json.dumps(final_verification, indent=2), encoding="utf-8")

    # Count entries in final ZIP
    with zipfile.ZipFile(ZIP_PATH) as zf:
        entry_count = len(zf.namelist())

    print(f"\nFinal ZIP: {ZIP_PATH}")
    print(f"Entries: {entry_count}")
    print(f"SHA-256: {pass2_sha}")
    print(f"Size: {pass2_size} bytes")

    return 0

if __name__ == "__main__":
    sys.exit(main())
