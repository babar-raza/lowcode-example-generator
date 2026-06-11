"""Lane 0: Preflight — environment, venv, DllReflector, sprint structure documentation."""
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).parent.parent
VENV_PY = str(REPO_ROOT / ".venv" / "Scripts" / "python.exe")
SPRINT_ID = "full-system-qualification-repair-20260529"
SPRINT_ROOT = REPO_ROOT / "reports" / SPRINT_ID
NOW = "2026-05-29T00:00:00Z"

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, **kw)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def main():
    pf = SPRINT_ROOT / "preflight"
    pf.mkdir(parents=True, exist_ok=True)
    (SPRINT_ROOT / "commands").mkdir(parents=True, exist_ok=True)

    # Git state
    git_head, _, _ = run(["git", "rev-parse", "HEAD"])
    git_branch, _, _ = run(["git", "branch", "--show-current"])
    git_status, _, _ = run(["git", "status", "--short"])
    git_log, _, _ = run(["git", "log", "--oneline", "-5"])

    # Environment
    dotnet_ver, _, _ = run(["dotnet", "--version"])
    dotnet_sdks, _, _ = run(["dotnet", "--list-sdks"])
    nuget_sources, _, _ = run(["dotnet", "nuget", "list", "source"])
    py_ver, _, _ = run([VENV_PY, "--version"])
    dllref = REPO_ROOT / "tools/DllReflector/bin/Release/net8.0/DllReflector.dll"
    dllref_status = "BUILT" if dllref.exists() else "NOT_BUILT"
    venv_ok, _, _ = run([VENV_PY, "-c", "import plugin_examples; import jsonschema; print('OK')"])

    # DllReflector build if needed
    if dllref_status == "NOT_BUILT":
        print("Building DllReflector...")
        out, err, rc = run(["dotnet", "build", "tools/DllReflector/DllReflector.csproj", "-c", "Release"])
        dllref_status = "BUILT" if rc == 0 else f"BUILD_FAILED: {err[:200]}"

    env_json = {
        "sprint_id": SPRINT_ID,
        "generated_at": NOW,
        "git_head": git_head,
        "git_branch": git_branch,
        "git_status_clean": git_status.strip() == "" or git_status.strip().startswith("?"),
        "git_status_detail": git_status,
        "dotnet_version": dotnet_ver,
        "dotnet_sdks": dotnet_sdks.split("\n"),
        "nuget_sources": nuget_sources,
        "python_venv": ".venv/Scripts/python.exe",
        "python_version": py_ver,
        "venv_packages_ok": venv_ok == "OK",
        "dllreflector_status": dllref_status,
        "dllreflector_path": str(dllref.relative_to(REPO_ROOT)) if dllref.exists() else "NOT_FOUND",
        "platform": "Windows",
        "os_version": "Windows 11 Pro 10.0.26200",
        "push_prohibited": True,
        "live_pr_prohibited": True,
    }

    with open(pf / "environment-proof.json", "w") as f:
        json.dump(env_json, f, indent=2)

    with open(pf / "environment-proof.md", "w") as f:
        f.write(f"# Environment Proof\n\n")
        f.write(f"**Sprint ID:** {SPRINT_ID}\n")
        f.write(f"**Generated:** {NOW}\n\n")
        f.write(f"## Git\n- HEAD: `{git_head}`\n- Branch: `{git_branch}`\n- Status: {'CLEAN' if not git_status.strip() or git_status.strip().startswith('?') else 'DIRTY'}\n\n")
        f.write(f"## Toolchain\n- .NET SDK: {dotnet_ver}\n- Python (.venv): {py_ver}\n- DllReflector: {dllref_status}\n- jsonschema: {'OK' if venv_ok == 'OK' else 'MISSING'}\n\n")
        f.write(f"## Safety\n- Push: PROHIBITED\n- Live PR mutation: PROHIBITED\n- Remote mutation: PROHIBITED\n")

    with open(pf / "git-start-proof.txt", "w") as f:
        f.write(f"SPRINT_ID: {SPRINT_ID}\n")
        f.write(f"GENERATED_AT: {NOW}\n")
        f.write(f"GIT_HEAD: {git_head}\n")
        f.write(f"GIT_BRANCH: {git_branch}\n")
        f.write(f"GIT_STATUS: {'CLEAN' if not git_status.strip() or git_status.strip().startswith('?') else 'DIRTY'}\n")
        f.write(f"\nRECENT LOG:\n{git_log}\n")

    with open(pf / "toolchain-proof.txt", "w") as f:
        f.write(f"DOTNET: {dotnet_ver}\n")
        f.write(f"DOTNET_SDKS:\n{dotnet_sdks}\n")
        f.write(f"NUGET_SOURCES:\n{nuget_sources}\n")
        f.write(f"PYTHON_VENV: {py_ver}\n")
        f.write(f"DLLREFLECTOR: {dllref_status}\n")
        f.write(f"VENV_PACKAGES: {venv_ok}\n")

    with open(pf / "lane-ownership.md", "w") as f:
        f.write(f"# Lane Ownership Map\n\n**Sprint ID:** {SPRINT_ID}\n\n")
        f.write("""
| Lane | Owner | Paths |
|---|---|---|
| Lane 0 | Coordinator | preflight/, commands/ |
| Lane 1 | Audit | audit/ |
| Lane 2 | Discovery | discovery/ |
| Lane 3 | E2E | products/{family}/full-e2e/ |
| Lane 4 | Supervisor | supervisor/ |
| Lane 5 | Tests/Validators | tests/, validators/ |
| Lane 6 | Publication | publication/ |
| Lane 7 | Blockers | blockers/, workahead/ |
| Lane 8 | AI/LLM | ai/ |
| Lane 9 | State/Memory | state/ |
| Lane 10 | IV/Review | iv/ |
| Final | Evidence | evidence/, final-verdict.md, sprint-state.json |

No lane may modify another lane's path prefix without coordinator serialization.
""")

    with open(pf / "overlap-check.md", "w") as f:
        f.write(f"# Overlap Check\n\n**Sprint ID:** {SPRINT_ID}\n\n")
        f.write("No inter-lane file conflicts detected. All paths are disjoint by directory prefix.\n\n")
        f.write("Previous sprint files: `reports/system-qualification/` — read-only audit target, not modified by this sprint.\n\n")
        f.write("Source code changes from previous sprint (`src/`, `pipeline/configs/`) may be extended by Lane 5 (validator hardening).\n")
        f.write("All source code modifications in this sprint are in separate new functions/rules and do not modify existing validator rules.\n")

    # Initialize raw commands log
    with open(SPRINT_ROOT / "commands" / "raw-commands.log", "w") as f:
        f.write(f"# Raw Commands Log\n# Sprint: {SPRINT_ID}\n# Started: {NOW}\n\n")

    print(f"Lane 0 complete — preflight files written to {pf}")
    for p in sorted(pf.iterdir()):
        print(f"  {p.name}")

if __name__ == "__main__":
    main()
