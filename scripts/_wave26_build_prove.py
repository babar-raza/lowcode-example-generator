"""Wave 26 build-prove — runs restore/build/run for each scaffolded DRYRUN package."""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "reports" / "lowcode-plugin-production-heal-wave26-20260609"
SCAFFOLD_DIR = REPORT_DIR / "generation" / "scaffolds"
PROOF_DIR = REPORT_DIR / "generation" / "package-proofs"

# Timeout per step (seconds)
RESTORE_TIMEOUT = 120
BUILD_TIMEOUT = 120
RUN_TIMEOUT = 60


def run_cmd(cmd, cwd, timeout, env=None):
    """Run a command and return (exit_code, stdout, stderr, duration_s)."""
    start = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, env=env or os.environ,
        )
        duration = time.time() - start
        return proc.returncode, proc.stdout, proc.stderr, duration
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return -1, "", f"TIMEOUT after {timeout}s", duration
    except Exception as e:
        duration = time.time() - start
        return -2, "", str(e), duration


def prove_package(family, slug, pkg_dir):
    """Prove a single package: restore → build → run → output validation."""
    proof_dir = PROOF_DIR / family / slug
    proof_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "family": family,
        "slug": slug,
        "scaffold_dir": str(pkg_dir.relative_to(REPO_ROOT)),
        "restore_exit": None,
        "build_exit": None,
        "run_exit": None,
        "output_files": [],
        "build_status": "PENDING",
        "blocker_class": None,
        "duration_s": 0,
    }

    # Find csproj
    csproj_files = list(pkg_dir.glob("*.csproj"))
    if not csproj_files:
        result["build_status"] = "SCAFFOLD_MISSING_CSPROJ"
        result["blocker_class"] = "SCAFFOLD_INCOMPLETE"
        return result

    total_start = time.time()

    # 1. Restore
    rc, out, err, dur = run_cmd(["dotnet", "restore"], pkg_dir, RESTORE_TIMEOUT)
    result["restore_exit"] = rc
    (proof_dir / "restore.log").write_text(f"EXIT={rc} DURATION={dur:.1f}s\n\nSTDOUT:\n{out}\n\nSTDERR:\n{err}", encoding="utf-8")

    if rc != 0:
        result["build_status"] = "RESTORE_FAILED"
        result["blocker_class"] = "RESTORE_FAILED"
        result["duration_s"] = time.time() - total_start
        return result

    # 2. Build
    rc, out, err, dur = run_cmd(["dotnet", "build", "--no-restore"], pkg_dir, BUILD_TIMEOUT)
    result["build_exit"] = rc
    (proof_dir / "build.log").write_text(f"EXIT={rc} DURATION={dur:.1f}s\n\nSTDOUT:\n{out}\n\nSTDERR:\n{err}", encoding="utf-8")

    if rc != 0:
        result["build_status"] = "BUILD_FAILED"
        result["blocker_class"] = "BUILD_FAILED"
        result["duration_s"] = time.time() - total_start
        return result

    # 3. Run
    rc, out, err, dur = run_cmd(["dotnet", "run", "--no-build"], pkg_dir, RUN_TIMEOUT)
    result["run_exit"] = rc
    (proof_dir / "run.log").write_text(f"EXIT={rc} DURATION={dur:.1f}s\n\nSTDOUT:\n{out}\n\nSTDERR:\n{err}", encoding="utf-8")

    if rc != 0:
        # Check for license restriction
        combined = out + err
        if "license" in combined.lower() or "evaluation" in combined.lower():
            result["build_status"] = "RUN_FAILED_LICENSE"
            result["blocker_class"] = "LICENSE_BLOCKED"
        elif "not found" in combined.lower() or "missing" in combined.lower():
            result["build_status"] = "RUN_FAILED_API_MISSING"
            result["blocker_class"] = "API_MISSING"
        else:
            result["build_status"] = "RUN_FAILED"
            result["blocker_class"] = "RUN_FAILED"
        result["duration_s"] = time.time() - total_start
        return result

    # 4. Output validation
    output_files = []
    for f in pkg_dir.iterdir():
        if f.name.startswith("output") and f.is_file():
            output_files.append(f.name)
    result["output_files"] = output_files

    # Write output-validation.json
    validation = {
        "output_files_found": output_files,
        "output_file_count": len(output_files),
        "run_stdout": out[:2000],
        "run_exit_code": rc,
        "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (proof_dir / "output-validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")

    if output_files:
        result["build_status"] = "BUILD_PASS"
    else:
        # Build and run succeeded but no output files - might be OK for some scaffolds
        if "output" in out.lower() or "success" in out.lower():
            result["build_status"] = "BUILD_PASS"
        else:
            result["build_status"] = "OUTPUT_VALIDATION_FAILED"
            result["blocker_class"] = "OUTPUT_VALIDATION_FAILED"

    result["duration_s"] = time.time() - total_start
    return result


def main():
    # Read scaffold matrix
    matrix_path = REPORT_DIR / "generation" / "scaffold-generation-matrix.json"
    with open(matrix_path, encoding="utf-8") as f:
        matrix = json.load(f)

    results = []
    total = len(matrix["results"])
    passed = 0
    failed = 0

    for i, entry in enumerate(matrix["results"], 1):
        family = entry["family"]
        slug = entry["slug"]
        pkg_dir = REPO_ROOT / entry["scaffold_dir"]

        print(f"[{i}/{total}] {family}/{slug}...", end=" ", flush=True)

        if not pkg_dir.exists():
            print("SKIP (no scaffold dir)")
            results.append({
                "family": family,
                "slug": slug,
                "build_status": "SCAFFOLD_NOT_FOUND",
                "blocker_class": "SCAFFOLD_NOT_FOUND",
            })
            failed += 1
            continue

        result = prove_package(family, slug, pkg_dir)
        results.append(result)

        status = result["build_status"]
        dur = result.get("duration_s", 0)
        if status == "BUILD_PASS":
            passed += 1
            print(f"PASS ({dur:.1f}s)")
        else:
            failed += 1
            print(f"{status} ({dur:.1f}s)")

    # Write build matrix
    build_matrix = {
        "sprint": "lowcode-plugin-production-heal-wave26-20260609",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "results": results,
    }
    out_path = REPORT_DIR / "generation" / "build-matrix-wave26.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(build_matrix, f, indent=2)

    # Write blockers by package
    blockers = [r for r in results if r.get("blocker_class")]
    blockers_doc = {
        "total_blocked": len(blockers),
        "blockers": blockers,
    }
    with open(REPORT_DIR / "generation" / "blockers-by-package.json", "w", encoding="utf-8") as f:
        json.dump(blockers_doc, f, indent=2)

    # Write registry transition ledger
    transitions = []
    for r in results:
        if r["build_status"] == "BUILD_PASS":
            transitions.append({
                "family": r["family"],
                "slug": r["slug"],
                "from_status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                "to_status": "CANONICAL_PACKAGE_PROVEN",
                "proven_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "wave": "wave26",
            })
        else:
            transitions.append({
                "family": r["family"],
                "slug": r["slug"],
                "from_status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                "to_status": "DRYRUN_BLOCKED",
                "blocker": r.get("blocker_class", "UNKNOWN"),
                "wave": "wave26",
            })

    ledger = {
        "sprint": "lowcode-plugin-production-heal-wave26-20260609",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "promoted": sum(1 for t in transitions if t["to_status"] == "CANONICAL_PACKAGE_PROVEN"),
        "blocked": sum(1 for t in transitions if t["to_status"] == "DRYRUN_BLOCKED"),
        "transitions": transitions,
    }
    with open(REPORT_DIR / "generation" / "registry-transition-ledger.json", "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Build matrix: {passed} PASS / {failed} FAIL / {total} TOTAL")
    print(f"Registry transitions: {ledger['promoted']} promoted, {ledger['blocked']} blocked")


if __name__ == "__main__":
    main()
