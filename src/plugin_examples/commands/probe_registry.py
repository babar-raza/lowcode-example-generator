"""CLI command: probe-registry — probe registry entries and optionally promote results."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the probe-registry sub-command."""
    parser = subparsers.add_parser(
        "probe-registry",
        help="Probe capability-registry entries by generating and running C# code",
        description=(
            "Generate C# probe code from registry entries, optionally execute "
            "dotnet restore/build/run, and promote results back to registry YAML."
        ),
    )
    parser.add_argument(
        "--family",
        required=True,
        help="Family slug to probe (e.g., drawing, finance, page)",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Specific plugin_slug to probe (default: all eligible entries)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Actually run dotnet restore/build/run (default: dry-run only)",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        default=False,
        help="Write probe results back to registry YAML (requires --execute)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Per-phase subprocess timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=False,
        help="Output results as JSON",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Execute the probe-registry command."""
    if args.promote and not args.execute:
        print("ERROR: --promote requires --execute", file=sys.stderr)
        return 1

    repo_root = Path.cwd()

    family = args.family
    registry_path = repo_root / "pipeline" / "plugin-capability-registry" / f"{family}.yaml"

    if not registry_path.exists():
        print(f"ERROR: No registry file at {registry_path}", file=sys.stderr)
        return 1

    if not args.execute:
        return _dry_run(family, registry_path, args)

    return _execute_probes(family, registry_path, repo_root, args)


def _dry_run(family: str, registry_path: Path, args: argparse.Namespace) -> int:
    """Generate probe code without executing."""
    import yaml

    from plugin_examples.probe_generator.registry_probe import generate_probe_from_registry

    text = registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    entries = data.get("entries", [])

    probeable = frozenset({"REFLECTION_CANDIDATE", "WEBSITE_DISCOVERED", "PROBE_CANDIDATE"})
    eligible = [e for e in entries if e.get("status") in probeable]

    if args.slug:
        eligible = [e for e in eligible if e.get("plugin_slug") == args.slug]

    if not eligible:
        print(f"No probeable entries for {family}")
        return 0

    results = []
    for entry in eligible:
        slug = entry.get("plugin_slug", "unknown")
        out_dir = Path(".local/psal/probes") / family / slug
        probe_files = generate_probe_from_registry(entry, out_dir)
        results.append({
            "family": family,
            "slug": slug,
            "status": entry.get("status"),
            "cs_path": str(probe_files.cs_path),
            "csproj_path": str(probe_files.csproj_path),
            "mode": "dry-run",
        })
        if not args.json_output:
            print(f"  {slug}: generated -> {probe_files.cs_path}")

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nGenerated {len(results)} probes for {family} (dry-run, no execution)")

    return 0


def _execute_probes(
    family: str,
    registry_path: Path,
    repo_root: Path,
    args: argparse.Namespace,
) -> int:
    """Execute probes and optionally promote results."""
    from plugin_examples.probe_executor.executor import ProbeExecutor

    try:
        executor = ProbeExecutor(repo_root=repo_root, timeout=args.timeout)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.slug:
        import yaml

        text = registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) or {}
        entries = data.get("entries", [])
        entry = next((e for e in entries if e.get("plugin_slug") == args.slug), None)
        if entry is None:
            print(f"ERROR: slug '{args.slug}' not found in {registry_path}", file=sys.stderr)
            return 1
        outcomes = [executor.probe_entry(family, entry)]
    else:
        outcomes = executor.probe_family(family, registry_path)

    if not outcomes:
        print(f"No probeable entries for {family}")
        return 0

    if args.promote:
        from plugin_examples.probe_executor.promoter import promote_family

        summary = promote_family(family, outcomes, repo_root)
        if not args.json_output:
            print(f"\nPromotion: {summary['promoted']} confirmed, {summary['failed']} failed")

    results = []
    for o in outcomes:
        r = {
            "family": o.family,
            "slug": o.plugin_slug,
            "new_status": o.new_status,
            "duration_ms": o.duration_ms,
        }
        if o.error:
            r["error"] = o.error
        if o.probe_result:
            r["restore_ok"] = o.probe_result.restore_ok
            r["build_ok"] = o.probe_result.build_ok
            r["run_ok"] = o.probe_result.run_ok
            r["output_size"] = o.probe_result.output_size_bytes
        results.append(r)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'Family':<12} {'Slug':<30} {'Status':<25} {'Duration':>10}")
        print("-" * 80)
        for r in results:
            print(f"{r['family']:<12} {r['slug']:<30} {r['new_status']:<25} {r['duration_ms']:>8}ms")

    confirmed = sum(1 for o in outcomes if o.new_status == "PROBE_CONFIRMED")
    failed = sum(1 for o in outcomes if o.new_status != "PROBE_CONFIRMED")
    if not args.json_output:
        print(f"\nSummary: {confirmed} confirmed, {failed} failed, {len(outcomes)} total")

    return 0
