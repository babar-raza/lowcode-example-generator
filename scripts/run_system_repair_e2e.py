"""
Comprehensive E2E runner for lowcode-system-repair-20260601 sprint.
Runs restore/build/run for every example in all pr-dry-run packages.
Captures per-example logs to reports directory.
"""
import json
import os
import subprocess
import sys
import time
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORT_DIR = REPO / "reports" / "lowcode-system-repair-20260601" / "e2e"
PR_DRY_RUN = REPO / "workspace" / "pr-dry-run"

FAMILIES = {
    "cells": ["cells-controlled-pilot"],
    "diagram": ["diagram-controlled-pilot"],
    "email": ["email-controlled-pilot"],
    "pdf": [
        "pdf-controlled-pilot", "pdf-controlled-pilot-pr5",
        "pdf-controlled-pilot-pr6", "pdf-controlled-pilot-pr7",
        "pdf-controlled-pilot-pr8", "pdf-controlled-pilot-pr9",
        "pdf-controlled-pilot-pr10", "pdf-controlled-pilot-pr11",
    ],
    "slides": ["slides-controlled-pilot"],
    "words": ["words-controlled-pilot"],
}

def find_examples():
    """Find all examples across all packages."""
    examples = []
    for family, pilots in FAMILIES.items():
        for pilot in pilots:
            base = PR_DRY_RUN / pilot / "examples" / family / "lowcode"
            if not base.exists():
                continue
            for ex_dir in sorted(base.iterdir()):
                if not ex_dir.is_dir():
                    continue
                csprojs = list(ex_dir.glob("*.csproj"))
                if not csprojs:
                    continue
                examples.append({
                    "family": family,
                    "name": ex_dir.name,
                    "dir": str(ex_dir),
                    "csproj": str(csprojs[0]),
                    "csproj_count": len(csprojs),
                    "pilot": pilot,
                })
    return examples

def run_cmd(cmd, cwd, timeout=120):
    """Run command and capture output."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"exit_code": -2, "stdout": "", "stderr": str(e)}

def main():
    examples = find_examples()
    print(f"Found {len(examples)} examples")

    results = []
    pass_count = 0
    fail_count = 0

    for i, ex in enumerate(examples, 1):
        fam = ex["family"]
        name = ex["name"]
        label = f"{fam}/{name}"
        ex_dir = ex["dir"]
        csproj = ex["csproj"]

        # Create per-example log dir
        log_dir = REPORT_DIR / fam / name
        log_dir.mkdir(parents=True, exist_ok=True)

        # Check for multiple csproj
        if ex["csproj_count"] > 1:
            msg = f"FAIL {label}: {ex['csproj_count']} csproj files in directory"
            print(f"  FAIL {label}: MULTIPLE_CSPROJ ({ex['csproj_count']})")
            result = {
                "family": fam, "name": name, "label": label,
                "e2e_pass": False, "failure_reason": "MULTIPLE_CSPROJ",
                "build_exit": -3, "run_exit": -3,
            }
            results.append(result)
            fail_count += 1
            (log_dir / "command.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            continue

        # Restore
        restore = run_cmd(["dotnet", "restore", csproj], cwd=ex_dir, timeout=120)
        (log_dir / "restore.log").write_text(
            f"EXIT: {restore['exit_code']}\n--- STDOUT ---\n{restore['stdout']}\n--- STDERR ---\n{restore['stderr']}", encoding="utf-8")

        # Build
        build = run_cmd(["dotnet", "build", csproj, "--no-restore", "-c", "Debug"], cwd=ex_dir, timeout=120)
        (log_dir / "build.log").write_text(
            f"EXIT: {build['exit_code']}\n--- STDOUT ---\n{build['stdout']}\n--- STDERR ---\n{build['stderr']}", encoding="utf-8")

        # Run
        if build["exit_code"] == 0:
            run = run_cmd(["dotnet", "run", "--project", csproj, "--no-build", "-c", "Debug"], cwd=ex_dir, timeout=120)
        else:
            run = {"exit_code": -4, "stdout": "", "stderr": "SKIPPED: build failed"}

        (log_dir / "run.log").write_text(
            f"EXIT: {run['exit_code']}\n--- STDOUT ---\n{run['stdout']}\n--- STDERR ---\n{run['stderr']}", encoding="utf-8")

        build_ok = build["exit_code"] == 0
        run_ok = run["exit_code"] == 0
        e2e_pass = build_ok and run_ok

        status = "PASS" if e2e_pass else "FAIL"
        if e2e_pass:
            pass_count += 1
        else:
            fail_count += 1

        reason = None
        if not build_ok:
            reason = f"BUILD_FAIL (exit {build['exit_code']})"
        elif not run_ok:
            reason = f"RUN_FAIL (exit {run['exit_code']})"

        result = {
            "family": fam, "name": name, "label": label,
            "pilot": ex["pilot"],
            "csproj": os.path.basename(csproj),
            "e2e_pass": e2e_pass,
            "build_exit": build["exit_code"],
            "run_exit": run["exit_code"],
            "failure_reason": reason,
        }
        results.append(result)

        # Write per-example command.json
        (log_dir / "command.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

        print(f"  [{i}/{len(examples)}] {'OK' if e2e_pass else 'FAIL'} {label}: build={build['exit_code']} run={run['exit_code']}")

    # Aggregate
    aggregate = {
        "sprint": "lowcode-system-repair-20260601",
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
        "all_pass": fail_count == 0,
        "results": results,
    }

    agg_path = REPORT_DIR / "e2e-aggregate.json"
    agg_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"\nTOTAL: {len(results)} | PASS: {pass_count} | FAIL: {fail_count}")
    print(f"Aggregate: {agg_path}")

    # Also write e2e-aggregate-v2 (identical — single source of truth)
    agg2_path = REPORT_DIR / "e2e-aggregate-v2.json"
    agg2_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
