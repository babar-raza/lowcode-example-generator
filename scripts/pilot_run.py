#!/usr/bin/env python3
"""Repeatable Aspose.Cells pilot run with diagnostic evidence.

Usage:
    python scripts/pilot_run.py --family cells --skip-run --template-mode
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# Add src/ to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plugin_examples.runner import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repeatable pilot pipeline run with diagnostic evidence.",
    )
    parser.add_argument("--family", default="cells", help="Family name (default: cells)")
    parser.add_argument("--run-id", default=None, help="Run ID (default: auto-generated)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Publisher dry-run mode (default: true)")
    parser.add_argument("--skip-run", action=argparse.BooleanOptionalAction, default=True,
                        help="Skip dotnet run step (default: true, use --no-skip-run to enable)")
    parser.add_argument("--build-only", action="store_true",
                        help="Only restore+build, skip run")
    parser.add_argument("--template-mode", action="store_true",
                        help="Force template generation even if LLM available")
    parser.add_argument("--require-llm", action="store_true",
                        help="Hard-stop if no LLM provider passes preflight")
    parser.add_argument("--require-validation", action="store_true",
                        help="Hard-stop if dotnet build fails")
    parser.add_argument("--require-reviewer", action="store_true",
                        help="Hard-stop if example-reviewer unavailable")
    parser.add_argument("--publish", action="store_true", default=False,
                        help="Enable live publishing (requires GITHUB_TOKEN)")
    parser.add_argument("--promote-latest", action="store_true", default=False,
                        help="Copy run evidence to workspace/verification/latest/")
    parser.add_argument("--clean-run-dir", action="store_true",
                        help="Remove workspace/runs/{run_id}/ before starting")
    parser.add_argument("--allow-cache-only", action="store_true",
                        help="Allow running with cached NuGet packages only")
    parser.add_argument("--tier", type=int, default=5, choices=range(6),
                        help="Run only through tier N (0-5, default: 5)")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    # Clean run dir if requested (ONLY the run dir, never manifests/verification)
    if args.clean_run_dir and args.run_id:
        run_dir = repo_root / "workspace" / "runs" / args.run_id
        if run_dir.exists():
            shutil.rmtree(run_dir)
            print(f"Cleaned: {run_dir}")

    # Build command string for report
    cmd = " ".join(sys.argv)

    # Execute pipeline
    report = run_pipeline(
        family=args.family,
        dry_run=not args.publish,
        skip_run=args.skip_run or args.build_only,
        template_mode=args.template_mode,
        require_llm=args.require_llm,
        require_validation=args.require_validation,
        require_reviewer=args.require_reviewer,
        run_id=args.run_id,
        repo_root=repo_root,
        max_tier=args.tier,
        command=cmd,
    )

    # Promote evidence if requested
    if args.promote_latest:
        _promote_evidence(repo_root, report.get("meta", {}).get("run_id", ""))

    # Print summary
    gs = report.get("gate_summary", {})
    verdict = report.get("verdict", "UNKNOWN")
    run_id = report.get("meta", {}).get("run_id", "unknown")

    print(f"\n{'='*60}")
    print(f"Pilot Run: {run_id}")
    print(f"Verdict: {verdict}")
    print(f"Stages: {gs.get('passed',0)} passed, {gs.get('degraded',0)} degraded, "
          f"{gs.get('failed',0)} failed, {gs.get('skipped',0)} skipped")
    print(f"Duration: {report.get('meta',{}).get('total_duration_ms',0):.0f}ms")
    print(f"Report: workspace/runs/{run_id}/pilot-report.json")
    print(f"{'='*60}\n")

    # Exit code
    if gs.get("hard_stopped"):
        return 1
    return 0


def _promote_evidence(repo_root: Path, run_id: str) -> None:
    """Copy run-scoped evidence to durable workspace locations."""
    evidence_latest = repo_root / "workspace" / "runs" / run_id / "evidence" / "latest"
    if not evidence_latest.exists():
        print("No evidence to promote.")
        return

    # Copy to workspace/verification/latest/
    target_ver = repo_root / "workspace" / "verification" / "latest"
    target_ver.mkdir(parents=True, exist_ok=True)
    for f in evidence_latest.iterdir():
        if f.is_file():
            shutil.copy2(f, target_ver / f.name)

    # Copy manifest-like files to workspace/manifests/
    target_man = repo_root / "workspace" / "manifests"
    target_man.mkdir(parents=True, exist_ok=True)
    manifest_names = {
        "product-inventory.json", "package-lock.json", "fixture-registry.json",
        "existing-examples-index.json", "scenario-catalog.json", "example-index.json",
    }
    evidence_root = repo_root / "workspace" / "runs" / run_id / "evidence"
    for f in evidence_root.iterdir():
        if f.is_file() and f.name in manifest_names:
            shutil.copy2(f, target_man / f.name)

    print(f"Evidence promoted from {run_id} to workspace/verification/latest/ and workspace/manifests/")


if __name__ == "__main__":
    sys.exit(main())
