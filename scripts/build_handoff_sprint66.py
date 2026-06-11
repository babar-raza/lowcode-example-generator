"""Phase 3: Build self-contained handoff artifacts from sprint64 packages."""
import json
import shutil
import hashlib
import os
from pathlib import Path
from datetime import datetime

BASE = Path(".")
SPRINT64_PKG = BASE / "reports/sprint64/destination-packages"
SPRINT66_HANDOFF = BASE / "reports/sprint66/handoff/per-family"

FAMILIES = {
    "cells":   ("aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples",   "examples/cells/lowcode"),
    "words":   ("aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples",    "examples/words/lowcode"),
    "pdf":     ("aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples",        "examples/pdf/lowcode"),
    "diagram": ("aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples","examples/diagram/lowcode"),
    "email":   ("aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples",    "examples/email/lowcode"),
    "slides":  ("aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples",  "examples/slides/lowcode"),
}

FAMILY_NUGET_VERSIONS = {
    "cells": "26.5.1",
    "words": "26.4.0",
    "pdf": "26.4.0",
    "diagram": "26.4.0",
    "email": "26.4.0",
    "slides": "26.5.0",
}

# Load sprint65 content audit for package paths
with open("reports/sprint65/destination/content-audit-final.json", encoding="utf-8") as f:
    s65_audit = {r["scenario_id"]: r for r in json.load(f)["records"]}

# Load remote inventory for SHAs
with open("reports/sprint66/remote/remote-example-inventory.json", encoding="utf-8") as f:
    remote_inv = {r["scenario_id"]: r for r in json.load(f)["records"]}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def has_obj_bin(path):
    for root, dirs, files in os.walk(path):
        for d in list(dirs):
            if d in ("obj", "bin", ".vs", "__pycache__"):
                return True
    return False


all_hashes = []
family_indexes = {}
total_ok = 0
total_missing = 0

for family, (repo, examples_base) in FAMILIES.items():
    print(f"\n=== {family} ===")
    dest_family_dir = SPRINT66_HANDOFF / family
    dest_family_dir.mkdir(parents=True, exist_ok=True)

    src_pkg_dir = SPRINT64_PKG / "per-family" / family

    # Copy Directory.Packages.props if exists
    dpp = src_pkg_dir / "Directory.Packages.props"
    if dpp.exists():
        shutil.copy2(dpp, dest_family_dir / "Directory.Packages.props")

    family_scenarios = [sid for sid, rec in s65_audit.items() if rec["family"] == family]
    nuget_ver = FAMILY_NUGET_VERSIONS.get(family, "?")

    family_idx = {
        "family": family,
        "repo": repo,
        "examples_base": examples_base,
        "nuget_version": nuget_ver,
        "examples": [],
        "pr_title": f"Update README I/O documentation for Aspose.{family.capitalize()} LowCode examples",
        "pr_body": (
            f"Adds '## Input and Output' sections to all {len(family_scenarios)} "
            f"{family} LowCode examples.\n\n"
            "This provides clear documentation of input formats, output formats, "
            "and API semantics for each example."
        ),
        "branch_name": f"plugin-examples/{family}/readme-io/sprint66",
        "rollback": f"git revert --no-edit HEAD  # reverts README I/O updates for {family}",
    }

    for scenario_id in sorted(family_scenarios):
        rec = s65_audit[scenario_id]
        pkg_path_str = rec.get("publication_package_path", "")

        # Resolve source path
        if rec.get("special_case") and family == "pdf":
            if scenario_id == "pdf-pdfa-converter":
                src_example = SPRINT64_PKG / "special-cases" / "pdf-pdf-aconverter"
            elif scenario_id == "pdf-text-extractor":
                src_example = SPRINT64_PKG / "special-cases" / "pdf-text-extractor"
            else:
                src_example = Path(pkg_path_str) if pkg_path_str else None
        elif scenario_id == "pdf-html-converter":
            # Remote dir is 'html', local package dir is also 'html'
            src_example = SPRINT64_PKG / "per-family" / "pdf" / "html"
        else:
            src_example = Path(pkg_path_str) if pkg_path_str else None

        # Determine destination dir name from remote
        remote = remote_inv.get(scenario_id, {})
        remote_dir = remote.get("dir_name") or (
            scenario_id.replace(f"{family}-", "") if family != "diagram" else scenario_id
        )
        # For special cases, map to correct remote dir name
        if scenario_id == "pdf-pdfa-converter":
            remote_dir = "pdfa-converter"
        elif scenario_id == "pdf-text-extractor":
            remote_dir = "text-extractor"
        elif scenario_id == "pdf-html-converter":
            remote_dir = "html"

        dest_example = dest_family_dir / remote_dir

        if src_example and src_example.exists():
            if dest_example.exists():
                shutil.rmtree(dest_example)
            shutil.copytree(
                src_example, dest_example,
                ignore=shutil.ignore_patterns("obj", "bin", ".vs", "*.user", "*.suo")
            )

            readme = dest_example / "README.md"
            programcs = dest_example / "Program.cs"
            csproj_files = list(dest_example.glob("*.csproj"))

            has_io = False
            if readme.exists():
                try:
                    has_io = "## Input and Output" in readme.read_text(encoding="utf-8")
                except Exception:
                    pass

            has_ob = has_obj_bin(dest_example)
            readme_hash = sha256_file(readme) if readme.exists() else None
            programcs_hash = sha256_file(programcs) if programcs.exists() else None
            csproj_hash = sha256_file(csproj_files[0]) if csproj_files else None

            ok = readme.exists() and programcs.exists() and csproj_files and has_io and not has_ob
            status = "OK" if ok else "PARTIAL"
            issues = []
            if not readme.exists(): issues.append("no README")
            if not has_io: issues.append("no I/O section")
            if not programcs.exists(): issues.append("no Program.cs")
            if not csproj_files: issues.append("no csproj")
            if has_ob: issues.append("obj/bin present")
            print(f"  {scenario_id}: {status}" + (f" ({', '.join(issues)})" if issues else ""))

            if ok:
                total_ok += 1
            else:
                total_missing += 1

            entry = {
                "scenario_id": scenario_id,
                "family": family,
                "dest_dir": remote_dir,
                "handoff_path": str(dest_example.relative_to(BASE)),
                "readme_hash_local": readme_hash,
                "readme_hash_remote": remote.get("readme_content_sha256"),
                "programcs_hash_local": programcs_hash,
                "programcs_hash_remote": remote.get("programcs_content_sha256"),
                "csproj_hash": csproj_hash,
                "readme_has_io": has_io,
                "has_obj_bin": has_ob,
                "status": status,
            }
            family_idx["examples"].append(entry)
            all_hashes.append(entry)
        else:
            print(f"  {scenario_id}: MISSING source ({src_example})")
            total_missing += 1
            family_idx["examples"].append({
                "scenario_id": scenario_id,
                "status": "MISSING",
                "source": str(src_example) if src_example else None,
            })

    # Save per-family handoff index
    with open(dest_family_dir / "handoff-index.json", "w", encoding="utf-8") as f:
        json.dump(family_idx, f, indent=2)

    family_indexes[family] = family_idx

print(f"\nTotal: OK={total_ok}, MISSING/PARTIAL={total_missing}")

# Save global publication-handoff-index.json
pub_idx = {
    "generated": datetime.now().isoformat() + "Z",
    "total_examples": len(all_hashes),
    "ok_count": total_ok,
    "missing_count": total_missing,
    "families": {
        f: {
            "repo": v["repo"],
            "example_count": len(v["examples"]),
            "pr_title": v["pr_title"],
            "branch_name": v["branch_name"],
        }
        for f, v in family_indexes.items()
    },
}
with open("reports/sprint66/handoff/publication-handoff-index.json", "w", encoding="utf-8") as f:
    json.dump(pub_idx, f, indent=2)

# Save package-artifact-hashes.json
with open("reports/sprint66/handoff/package-artifact-hashes.json", "w", encoding="utf-8") as f:
    json.dump({
        "generated": datetime.now().isoformat() + "Z",
        "total": len(all_hashes),
        "records": all_hashes,
    }, f, indent=2)

print("Saved: per-family/*/handoff-index.json, publication-handoff-index.json, package-artifact-hashes.json")
