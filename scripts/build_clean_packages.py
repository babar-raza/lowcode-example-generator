"""Build clean package artifacts for Sprint 64 Phase 3.

Extracts only Program.cs, README.md, .csproj, .props files from dry-run packages.
Excludes obj/, bin/, .vs/ intermediate build artifacts.
"""
import json
import shutil
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "reports" / "sprint64" / "destination-packages"
PER_FAMILY_DIR = OUTPUT_DIR / "per-family"

CLEAN_EXTENSIONS = {".cs", ".csproj", ".props", ".md"}
EXCLUDE_DIRS = {"obj", "bin", ".vs", ".vscode", "debug", "release"}


def is_clean_file(path: Path) -> bool:
    for part in path.parts:
        if part.lower() in EXCLUDE_DIRS:
            return False
    return path.suffix.lower() in CLEAN_EXTENSIONS


def copy_clean_files(src_dir: Path, dst_dir: Path) -> list:
    files = []
    for src_file in src_dir.rglob("*"):
        if not src_file.is_file():
            continue
        if not is_clean_file(src_file):
            continue
        rel = src_file.relative_to(src_dir)
        rel_str = str(rel).replace("\\", "/")
        dst_file = dst_dir / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        h = hashlib.sha256(src_file.read_bytes()).hexdigest()
        files.append({
            "file": rel_str,
            "sha256": h,
            "size": src_file.stat().st_size,
        })
    return files


FAMILY_SOURCES = {
    "cells": [("workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode", None)],
    "diagram": [("workspace/pr-dry-run/diagram-controlled-pilot/examples/diagram/lowcode", None)],
    "email": [("workspace/pr-dry-run/email-controlled-pilot/examples/email/lowcode", None)],
    "pdf": [
        ("workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-wave1/examples/pdf/lowcode", None),
        ("workspace/pr-dry-run/pdf-controlled-pilot-wave2/examples/pdf/lowcode", None),
    ],
    "slides": [("workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode", None)],
    "words": [
        ("workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode", None),
    ],
}

FAMILY_PROPS = {
    "cells": "workspace/pr-dry-run/cells-controlled-pilot/Directory.Packages.props",
    "diagram": "workspace/pr-dry-run/diagram-controlled-pilot/Directory.Packages.props",
    "email": "workspace/pr-dry-run/email-controlled-pilot/Directory.Packages.props",
    "pdf": "workspace/pr-dry-run/pdf-controlled-pilot/Directory.Packages.props",
    "slides": "workspace/pr-dry-run/slides-controlled-pilot/Directory.Packages.props",
    "words": "workspace/pr-dry-run/words-controlled-pilot/Directory.Packages.props",
}


def main():
    if PER_FAMILY_DIR.exists():
        shutil.rmtree(PER_FAMILY_DIR)
    PER_FAMILY_DIR.mkdir(parents=True, exist_ok=True)

    index = {}
    all_hashes = {}
    source_manifest = {}
    total_files = 0

    for family, sources in FAMILY_SOURCES.items():
        family_dir = PER_FAMILY_DIR / family
        family_dir.mkdir(parents=True, exist_ok=True)
        family_scenarios = {}

        for src_path_str, override_name in sources:
            src_dir = REPO_ROOT / src_path_str
            if not src_dir.exists():
                print(f"  SKIP (not found): {src_path_str}")
                continue

            if override_name:
                dst_dir = family_dir / override_name
                files = copy_clean_files(src_dir, dst_dir)
                family_scenarios[override_name] = {
                    "source": src_path_str,
                    "file_count": len(files),
                }
                for f in files:
                    key = f"{family}/{override_name}/{f['file']}"
                    all_hashes[key] = f["sha256"]
                total_files += len(files)
            else:
                for scenario_dir in sorted(src_dir.iterdir()):
                    if not scenario_dir.is_dir():
                        continue
                    scenario_name = scenario_dir.name
                    dst_dir = family_dir / scenario_name
                    files = copy_clean_files(scenario_dir, dst_dir)
                    if scenario_name in family_scenarios:
                        family_scenarios[scenario_name]["file_count"] += len(files)
                    else:
                        family_scenarios[scenario_name] = {
                            "source": src_path_str,
                            "file_count": len(files),
                        }
                    for f in files:
                        key = f"{family}/{scenario_name}/{f['file']}"
                        all_hashes[key] = f["sha256"]
                    total_files += len(files)

        props_src = REPO_ROOT / FAMILY_PROPS.get(family, "")
        if props_src.exists():
            props_dst = family_dir / "Directory.Packages.props"
            shutil.copy2(props_src, props_dst)
            h = hashlib.sha256(props_src.read_bytes()).hexdigest()
            all_hashes[f"{family}/Directory.Packages.props"] = h
            total_files += 1

        index[family] = {
            "total_scenarios": len(family_scenarios),
            "scenarios": family_scenarios,
        }
        source_manifest[family] = {s: d["source"] for s, d in family_scenarios.items()}

    for fam, data in index.items():
        print(f"  {fam}: {data['total_scenarios']} scenarios")
    print(f"Total clean files: {total_files}")

    (OUTPUT_DIR / "package-artifact-index.json").write_text(
        json.dumps(index, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "package-hashes.json").write_text(
        json.dumps(all_hashes, indent=2, sort_keys=True), encoding="utf-8"
    )
    (OUTPUT_DIR / "package-source-manifest.json").write_text(
        json.dumps(source_manifest, indent=2), encoding="utf-8"
    )
    print("Written: package-artifact-index.json, package-hashes.json, package-source-manifest.json")
    return index


if __name__ == "__main__":
    main()
