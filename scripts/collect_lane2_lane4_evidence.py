"""
Collect Lane 2 (source snapshots) and Lane 4 (raw E2E logs) evidence.

For each canonical run:
1. Copy generated source files (Program.cs, csproj, README, manifests, fixtures) to sprint evidence
2. Run dotnet restore/build/run and capture raw logs
3. Write per-example command.json and output-proof.json
"""
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-final-closure-pass3-20260530"
SPRINT_ROOT = REPO_ROOT / "reports" / SPRINT_ID
EVIDENCE_GENERATED = SPRINT_ROOT / "generated-source"
EVIDENCE_E2E = SPRINT_ROOT / "e2e-raw"
WORKSPACE_RUNS = REPO_ROOT / "workspace" / "runs"

CANONICAL_RUNS = {
    "cells":   "pilot-cells-20260529-221017",
    "diagram": "pilot-diagram-20260529-221021",
    "email":   "pilot-email-20260529-220716",
    "pdf":     "pilot-pdf-20260529-222233",
    "slides":  "pilot-slides-20260529-221814",
    "words":   "pilot-words-20260529-221024",
}

# Files to copy for source snapshots (exclude bin/, obj/)
SOURCE_INCLUDE = {".cs", ".csproj", ".md", ".json", ".txt", ".xlsx", ".docx",
                   ".pptx", ".pdf", ".eml", ".bmp", ".png", ".jpg", ".vsdx"}

def copy_source_snapshot(src_example_dir: Path, dst_dir: Path) -> list[str]:
    """Copy relevant source files, excluding bin/obj."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for p in src_example_dir.rglob("*"):
        # Skip bin/obj directories
        parts = p.relative_to(src_example_dir).parts
        if parts and parts[0] in ("bin", "obj"):
            continue
        if p.is_file():
            rel = p.relative_to(src_example_dir)
            dst = dst_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            copied.append(str(rel))
    return copied

def run_dotnet(cmd: list[str], cwd: Path, timeout: int = 120) -> dict:
    """Run a dotnet command and capture stdout/stderr."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        elapsed_ms = (time.time() - start) * 1000
        return {
            "command": " ".join(cmd),
            "cwd": str(cwd),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_ms": round(elapsed_ms, 1),
            "success": result.returncode == 0,
            "error": None,
        }
    except subprocess.TimeoutExpired:
        elapsed_ms = (time.time() - start) * 1000
        return {
            "command": " ".join(cmd),
            "cwd": str(cwd),
            "exit_code": -1,
            "stdout": "",
            "stderr": "TIMEOUT",
            "duration_ms": round(elapsed_ms, 1),
            "success": False,
            "error": "timeout",
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "cwd": str(cwd),
            "exit_code": -2,
            "stdout": "",
            "stderr": str(e),
            "duration_ms": 0,
            "success": False,
            "error": str(e),
        }

def write_log(path: Path, result: dict):
    """Write a simple text log from a dotnet result."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"COMMAND: {result['command']}\n")
        f.write(f"CWD: {result['cwd']}\n")
        f.write(f"EXIT_CODE: {result['exit_code']}\n")
        f.write(f"DURATION_MS: {result['duration_ms']}\n")
        f.write(f"SUCCESS: {result['success']}\n")
        f.write("---STDOUT---\n")
        f.write(result["stdout"] or "(empty)\n")
        f.write("---STDERR---\n")
        f.write(result["stderr"] or "(empty)\n")

aggregate = {
    "sprint_id": SPRINT_ID,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "families": {},
    "total_examples": 0,
    "total_passed": 0,
    "total_failed": 0,
}

source_manifest_entries = []
hash_verification_entries = []

for family, run_id in CANONICAL_RUNS.items():
    run_dir = WORKSPACE_RUNS / run_id / "generated" / family
    if not run_dir.exists():
        print(f"WARNING: Run dir not found: {run_dir}")
        continue

    examples = sorted([d for d in run_dir.iterdir() if d.is_dir()])
    print(f"\n=== {family.upper()} ({len(examples)} examples) ===")

    family_results = []
    for example_dir in examples:
        example_id = example_dir.name
        print(f"  Processing {example_id}...")

        # Lane 2: Copy source snapshot
        dst_src = EVIDENCE_GENERATED / family / example_id
        copied_files = copy_source_snapshot(example_dir, dst_src)
        source_manifest_entries.append({
            "family": family,
            "example_id": example_id,
            "run_id": run_id,
            "source_dir": str(example_dir.relative_to(REPO_ROOT)),
            "snapshot_dir": str(dst_src.relative_to(REPO_ROOT)),
            "files_copied": copied_files,
        })

        # Lane 4: Run dotnet restore / build / run
        e2e_dir = EVIDENCE_E2E / family / example_id
        e2e_dir.mkdir(parents=True, exist_ok=True)

        # dotnet restore
        restore_result = run_dotnet(["dotnet", "restore", "--nologo"], example_dir)
        write_log(e2e_dir / "restore.log", restore_result)

        # dotnet build (only if restore succeeded)
        if restore_result["success"]:
            build_result = run_dotnet(
                ["dotnet", "build", "--nologo", "--no-restore", "-c", "Release"], example_dir
            )
        else:
            build_result = {"command": "dotnet build (skipped)", "exit_code": -3,
                            "stdout": "", "stderr": "restore failed", "duration_ms": 0,
                            "success": False, "error": "restore_failed", "cwd": str(example_dir)}
        write_log(e2e_dir / "build.log", build_result)

        # dotnet run (only if build succeeded)
        if build_result["success"]:
            run_result = run_dotnet(
                ["dotnet", "run", "--nologo", "--no-build", "-c", "Release"], example_dir,
                timeout=60
            )
        else:
            run_result = {"command": "dotnet run (skipped)", "exit_code": -3,
                          "stdout": "", "stderr": "build failed", "duration_ms": 0,
                          "success": False, "error": "build_failed", "cwd": str(example_dir)}
        write_log(e2e_dir / "run.log", run_result)

        # command.json
        cmd_record = {
            "example_id": example_id,
            "family": family,
            "run_id": run_id,
            "restore": {"command": restore_result["command"], "exit_code": restore_result["exit_code"],
                        "success": restore_result["success"], "duration_ms": restore_result["duration_ms"]},
            "build":   {"command": build_result["command"], "exit_code": build_result["exit_code"],
                        "success": build_result["success"], "duration_ms": build_result["duration_ms"]},
            "run":     {"command": run_result["command"], "exit_code": run_result["exit_code"],
                        "success": run_result["success"], "duration_ms": run_result["duration_ms"]},
        }
        with open(e2e_dir / "command.json", "w") as f:
            json.dump(cmd_record, f, indent=2)

        # output-proof.json
        all_passed = restore_result["success"] and build_result["success"] and run_result["success"]
        output_proof = {
            "example_id": example_id,
            "all_passed": all_passed,
            "restore_passed": restore_result["success"],
            "build_passed": build_result["success"],
            "run_passed": run_result["success"],
            "run_stdout_snippet": run_result["stdout"][:500] if run_result["stdout"] else "",
        }
        with open(e2e_dir / "output-proof.json", "w") as f:
            json.dump(output_proof, f, indent=2)

        status = "PASS" if all_passed else "FAIL"
        print(f"    restore={restore_result['success']} build={build_result['success']} "
              f"run={run_result['success']} -> {status}")
        family_results.append({"example_id": example_id, "passed": all_passed,
                                "restore": restore_result["success"],
                                "build": build_result["success"],
                                "run": run_result["success"]})

    family_passed = sum(1 for r in family_results if r["passed"])
    family_total = len(family_results)
    aggregate["families"][family] = {
        "run_id": run_id,
        "total": family_total,
        "passed": family_passed,
        "failed": family_total - family_passed,
        "results": family_results,
    }
    aggregate["total_examples"] += family_total
    aggregate["total_passed"] += family_passed
    aggregate["total_failed"] += (family_total - family_passed)
    print(f"  {family}: {family_passed}/{family_total} PASS")

# Write aggregate
with open(EVIDENCE_E2E / "e2e-aggregate.json", "w") as f:
    json.dump(aggregate, f, indent=2)

# Write source snapshot manifest
with open(EVIDENCE_GENERATED / "source-snapshot-manifest.json", "w") as f:
    json.dump({"sprint_id": SPRINT_ID, "entries": source_manifest_entries,
               "total_examples": len(source_manifest_entries)}, f, indent=2)

# Write e2e summary
total = aggregate["total_examples"]
passed = aggregate["total_passed"]
with open(EVIDENCE_E2E / "e2e-summary.md", "w") as f:
    f.write(f"# E2E Raw Validation Summary\n\n")
    f.write(f"**Sprint**: {SPRINT_ID}\n\n")
    f.write(f"**Total**: {passed}/{total} examples passed restore+build+run\n\n")
    f.write(f"| Family | Total | Passed | Failed |\n|--------|-------|--------|--------|\n")
    for fam, data in aggregate["families"].items():
        f.write(f"| {fam} | {data['total']} | {data['passed']} | {data['failed']} |\n")
    f.write(f"\n**Verdict**: {'ALL_PASS' if passed == total else 'SOME_FAIL'}\n")

print(f"\n=== FINAL: {passed}/{total} examples passed ===")
print(f"Aggregate written: {EVIDENCE_E2E / 'e2e-aggregate.json'}")
print(f"Source manifest: {EVIDENCE_GENERATED / 'source-snapshot-manifest.json'}")
