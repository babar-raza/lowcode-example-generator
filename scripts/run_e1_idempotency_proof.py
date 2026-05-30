"""E1/E2 idempotency proof: run canonical_packager A/B across LOWCODE families.

Runs canonical_packager twice for each family. After run A, copies output to tmp/run-a/.
After run B, copies to tmp/run-b/. Compares SHA-256 of all source files.

Output: reports/lowcode-systemization-pass2-20260530/idempotency/idempotency-summary.json
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-systemization-pass2-20260530"
OUT_DIR = REPO_ROOT / "reports" / SPRINT_ID / "idempotency"
PR_DRY_RUN = REPO_ROOT / "workspace" / "pr-dry-run"

MANIFESTS_TO_TEST = [
    "cells-controlled-pilot.json",
    "diagram-controlled-pilot.json",
    "email-controlled-pilot.json",
    "slides-controlled-pilot.json",
    "words-controlled-pilot.json",
    "pdf-controlled-pilot-pr10.json",
]

SKIP_DIRS = {"bin", "obj", ".vs"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def collect_source_files(pkg_dir: Path) -> dict[str, str]:
    result = {}
    for f in sorted(pkg_dir.rglob("*")):
        if not f.is_file():
            continue
        rel_parts = f.relative_to(pkg_dir).parts
        if any(p in SKIP_DIRS for p in rel_parts):
            continue
        rel = "/".join(rel_parts)
        result[rel] = sha256_file(f)
    return result


def run_packager_no_verify(manifest_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "canonical_packager.py"),
         "--manifest", str(manifest_path)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=60,
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_dir = REPO_ROOT / "pipeline" / "configs" / "assembly-manifests"

    print(f"\n=== E1/E2 idempotency proof: {SPRINT_ID} ===\n")

    results = {}
    all_pass = True

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        for manifest_name in MANIFESTS_TO_TEST:
            manifest_path = manifest_dir / manifest_name
            if not manifest_path.exists():
                print(f"  SKIP {manifest_name} (manifest not found)")
                continue

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            package_name = manifest["package_name"]
            source_run = manifest.get("source_run")

            if not source_run:
                print(f"  SKIP {package_name} (source_run=null)")
                results[package_name] = {"status": "SKIPPED", "reason": "source_run=null"}
                continue

            source_root = REPO_ROOT / source_run
            if not source_root.exists():
                print(f"  SKIP {package_name} (source_run not found: {source_run})")
                results[package_name] = {"status": "SKIPPED", "reason": f"source_run not found: {source_run}"}
                continue

            pkg_dir = PR_DRY_RUN / package_name
            print(f"  [{package_name}]", end=" ", flush=True)

            # Run A
            r_a = run_packager_no_verify(manifest_path)
            if r_a.returncode != 0:
                print(f"FAIL (run A rc={r_a.returncode})")
                results[package_name] = {"status": "FAIL", "reason": f"run A failed"}
                all_pass = False
                continue

            snap_a = tmp / "run-a" / package_name
            snap_a.parent.mkdir(parents=True, exist_ok=True)
            if snap_a.exists():
                shutil.rmtree(snap_a)
            shutil.copytree(pkg_dir, snap_a, ignore=shutil.ignore_patterns("bin", "obj", ".vs"))

            # Run B
            r_b = run_packager_no_verify(manifest_path)
            if r_b.returncode != 0:
                print(f"FAIL (run B rc={r_b.returncode})")
                results[package_name] = {"status": "FAIL", "reason": "run B failed"}
                all_pass = False
                continue

            snap_b = tmp / "run-b" / package_name
            snap_b.parent.mkdir(parents=True, exist_ok=True)
            if snap_b.exists():
                shutil.rmtree(snap_b)
            shutil.copytree(pkg_dir, snap_b, ignore=shutil.ignore_patterns("bin", "obj", ".vs"))

            sha_a = collect_source_files(snap_a)
            sha_b = collect_source_files(snap_b)
            files_a = set(sha_a)
            files_b = set(sha_b)
            only_a = sorted(files_a - files_b)
            only_b = sorted(files_b - files_a)
            common = files_a & files_b
            mismatches = sorted(f for f in common if sha_a[f] != sha_b[f])

            total = len(common)
            identical = total - len(mismatches)

            if not only_a and not only_b and not mismatches:
                status = "PASS"
                print(f"PASS ({total}/{total} SHA-identical)")
            else:
                status = "FAIL"
                all_pass = False
                print(f"FAIL ({identical}/{total} identical, {len(mismatches)} mismatches)")

            results[package_name] = {
                "status": status,
                "total_source_files": total,
                "sha_identical": identical,
                "sha_mismatches": len(mismatches),
                "only_in_a": only_a,
                "only_in_b": only_b,
                "mismatch_files": mismatches,
                "run_a_rc": r_a.returncode,
                "run_b_rc": r_b.returncode,
            }

    pass_count = sum(1 for r in results.values() if r["status"] == "PASS")
    skip_count = sum(1 for r in results.values() if r["status"] == "SKIPPED")
    fail_count = sum(1 for r in results.values() if r["status"] == "FAIL")

    verdict = "IDEMPOTENCY_PROVEN" if fail_count == 0 and pass_count > 0 else "IDEMPOTENCY_FAILED"

    summary = {
        "sprint_id": SPRINT_ID,
        "lane": "E1/E2 — A/B idempotency proof across 6 LOWCODE families",
        "generated_at": "2026-05-30",
        "packages_tested": len(results),
        "pass": pass_count,
        "skip": skip_count,
        "fail": fail_count,
        "verdict": verdict,
        "results": results,
    }
    summary_path = OUT_DIR / "idempotency-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\n=== Idempotency: PASS={pass_count} SKIP={skip_count} FAIL={fail_count} ===")
    print(f"Verdict: {verdict}")
    print(f"Summary: {summary_path}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
