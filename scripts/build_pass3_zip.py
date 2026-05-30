#!/usr/bin/env python3
"""Build the ZIP artifact for lowcode-final-closure-pass3-20260530 sprint."""

import json
import os
import subprocess
import zipfile
from pathlib import Path

SPRINT_ID = "lowcode-final-closure-pass3-20260530"
REPO_ROOT = Path(__file__).parent.parent
REPORT_DIR = REPO_ROOT / "reports" / SPRINT_ID
ARTIFACT_META_DIR = REPO_ROOT / ".local" / "artifact-metadata" / SPRINT_ID
OUTPUT_DIR = REPO_ROOT / ".local" / "evidence-bundles"
ZIP_NAME = f"{SPRINT_ID}-evidence.zip"


def get_tracked_files():
    """Get all tracked files in the sprint report directory."""
    result = subprocess.run(
        ["git", "ls-files", f"reports/{SPRINT_ID}/", "docs/development/open-taskcard-closure-matrix.md",
         "scripts/collect_lane2_lane4_evidence.py", "scripts/run_ecc_pass3.py",
         "scripts/build_pass3_zip.py"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    return files


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / ZIP_NAME

    tracked_files = get_tracked_files()
    meta_files = list(ARTIFACT_META_DIR.glob("*"))

    print(f"Sprint: {SPRINT_ID}")
    print(f"Tracked files to include: {len(tracked_files)}")
    print(f"Artifact metadata files: {len(meta_files)}")
    print(f"Output: {zip_path}")
    print()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add tracked files
        for rel_path in tracked_files:
            full_path = REPO_ROOT / rel_path
            if full_path.exists():
                zf.write(full_path, rel_path)
            else:
                print(f"  WARNING: tracked file not found: {rel_path}")

        # Add artifact-metadata (outside tracked repo)
        for meta_file in sorted(meta_files):
            arc_name = f"artifact-metadata/{meta_file.name}"
            zf.write(meta_file, arc_name)
            print(f"  + {arc_name}")

    # Count entries
    with zipfile.ZipFile(zip_path, "r") as zf:
        entries = zf.namelist()
        total_entries = len(entries)

    size_kb = zip_path.stat().st_size / 1024
    print(f"\nZIP built: {zip_path}")
    print(f"Total entries: {total_entries} ({len(tracked_files)} tracked + {len(meta_files)} metadata)")
    print(f"Size: {size_kb:.1f} KB")

    # Write zip-file-list
    zip_list_path = ARTIFACT_META_DIR / "zip-file-list.txt"
    with open(zip_list_path, "w") as f:
        f.write(f"# ZIP file list for {SPRINT_ID}\n")
        f.write(f"# {total_entries} entries\n\n")
        for name in sorted(entries):
            f.write(f"{name}\n")
    print(f"File list: {zip_list_path}")


if __name__ == "__main__":
    main()
