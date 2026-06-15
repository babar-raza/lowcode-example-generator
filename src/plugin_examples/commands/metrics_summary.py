"""metrics-summary command — local dashboard for pipeline run metrics.

Reads evidence from the most recent run directory and aggregates LLM
usage, SLO compliance, and doctor check results into a structured
summary suitable for local dashboard display or CI reporting.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _find_latest_run(workspace: Path) -> Path | None:
    runs_dir = workspace / "runs"
    if not runs_dir.is_dir():
        return None
    run_dirs = sorted(
        (d for d in runs_dir.iterdir() if d.is_dir()),
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    return run_dirs[0] if run_dirs else None


def _collect_llm_metrics(run_dir: Path) -> dict:
    metrics = {"total_calls": 0, "total_tokens": 0, "total_duration_ms": 0}
    for f in run_dir.rglob("llm-usage-ledger.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else data.get("entries", [])
            for entry in entries:
                metrics["total_calls"] += 1
                metrics["total_tokens"] += entry.get("tokens", 0)
                metrics["total_duration_ms"] += entry.get("duration_ms", 0)
        except (json.JSONDecodeError, OSError):
            pass
    return metrics


def _collect_doctor_summary(repo_root: Path) -> dict:
    try:
        from plugin_examples.health.doctor import run_all_checks
        checks = run_all_checks(repo_root)
        return {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.status == "PASS"),
            "failed": sum(1 for c in checks if c.status == "FAIL"),
            "warnings": sum(1 for c in checks if c.status == "WARN"),
        }
    except Exception:
        return {"total": 0, "passed": 0, "failed": 0, "warnings": 0}


def _collect_slo_summary(repo_root: Path) -> dict:
    try:
        from plugin_examples.policy.loader import load_slos
        slos = load_slos(repo_root)
        return {"slo_count": len(slos), "loaded": True}
    except Exception:
        return {"slo_count": 0, "loaded": False}


def generate_metrics_summary(repo_root: Path) -> dict:
    """Generate a metrics summary from the current project state."""
    workspace = repo_root / "workspace"
    latest_run = _find_latest_run(workspace)

    summary = {
        "repo_root": str(repo_root),
        "latest_run": str(latest_run) if latest_run else None,
        "llm_metrics": _collect_llm_metrics(latest_run) if latest_run else {},
        "doctor": _collect_doctor_summary(repo_root),
        "slo": _collect_slo_summary(repo_root),
    }
    return summary


def run(args: argparse.Namespace) -> None:
    """Execute the metrics-summary command."""
    repo_root = Path(args.repo_root).resolve() if hasattr(args, "repo_root") and args.repo_root else Path.cwd()
    summary = generate_metrics_summary(repo_root)

    if getattr(args, "json_output", False):
        print(json.dumps(summary, indent=2))
    else:
        print("Pipeline Metrics Summary")
        print("=" * 40)
        if summary["latest_run"]:
            print(f"  Latest run: {summary['latest_run']}")
        else:
            print("  No run data found in workspace/runs/")
        llm = summary.get("llm_metrics", {})
        if llm:
            print(f"  LLM calls: {llm.get('total_calls', 0)}")
            print(f"  LLM tokens: {llm.get('total_tokens', 0)}")
        doc = summary["doctor"]
        print(f"  Doctor: {doc['passed']}/{doc['total']} passed, {doc['failed']} failed, {doc['warnings']} warnings")
        slo = summary["slo"]
        print(f"  SLOs: {slo['slo_count']} defined, loaded={slo['loaded']}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the metrics-summary subcommand."""
    parser = subparsers.add_parser(
        "metrics-summary",
        help="Display aggregated pipeline metrics summary",
    )
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output as JSON")
    parser.set_defaults(func=run)
