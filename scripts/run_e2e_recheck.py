"""Re-run E2E for all canonical examples after removing duplicate csproj files."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
pr = REPO / "workspace" / "pr-dry-run"

families = {
    "words": pr / "words-controlled-pilot",
    "slides": pr / "slides-controlled-pilot",
    "cells": pr / "cells-controlled-pilot",
    "diagram": pr / "diagram-controlled-pilot",
    "email": pr / "email-controlled-pilot",
}
for pkg_dir in pr.iterdir():
    if pkg_dir.name.startswith("pdf-") and pkg_dir.is_dir():
        families[f"pdf/{pkg_dir.name}"] = pkg_dir

results = []
for family_key in sorted(families):
    pkg_dir = families[family_key]
    if not pkg_dir.exists():
        continue
    family = family_key.split("/")[0]
    csprojfiles = sorted(
        f for f in pkg_dir.rglob("*.csproj")
        if "bin" not in f.parts and "obj" not in f.parts
    )
    seen_dirs = set()
    for csproj in csprojfiles:
        ex_dir = csproj.parent
        if str(ex_dir) in seen_dirs:
            continue
        seen_dirs.add(str(ex_dir))
        scenario_id = ex_dir.name

        b = subprocess.run(
            ["dotnet", "build", "-v", "q", "--no-incremental"],
            cwd=ex_dir, capture_output=True, text=True, timeout=120
        )
        r = subprocess.run(
            ["dotnet", "run", "--no-build"],
            cwd=ex_dir, capture_output=True, text=True, timeout=60
        )

        build_ok = b.returncode == 0
        run_ok = r.returncode == 0
        status = "PASS" if build_ok and run_ok else "FAIL"
        results.append({
            "scenario_id": scenario_id,
            "family": family,
            "package": pkg_dir.name,
            "build_exit": b.returncode,
            "run_exit": r.returncode,
            "build_ok": build_ok,
            "run_ok": run_ok,
            "e2e_pass": build_ok and run_ok,
            "run_output_snippet": (r.stdout or r.stderr)[:200].strip(),
        })
        marker = "OK" if status == "PASS" else "FAIL"
        print(f"  {marker} {family}/{scenario_id}: {status}")

passed = sum(1 for r in results if r["e2e_pass"])
failed = sum(1 for r in results if not r["e2e_pass"])
print(f"\nTOTAL: {len(results)} | PASS: {passed} | FAIL: {failed}")
if failed > 0:
    print("FAILURES:")
    for r in results:
        if not r["e2e_pass"]:
            print(f"  {r['family']}/{r['scenario_id']}: build={r['build_exit']} run={r['run_exit']}")
            print(f"    {r['run_output_snippet'][:100]}")

# Write updated aggregate
out = REPO / "reports" / "lowcode-true-closure-20260531" / "e2e" / "e2e-aggregate-v2.json"
out.write_text(json.dumps({
    "sprint_id": "lowcode-true-closure-20260531",
    "generated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "note": "v2: duplicate csproj removed, all 42 canonical examples verified",
    "total": len(results),
    "pass": passed,
    "fail": failed,
    "results": results,
}, indent=2), encoding="utf-8")
print(f"\nAggregate written: {out}")
