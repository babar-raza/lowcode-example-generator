"""Command: version-drift."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the version-drift subcommand."""
    # version-drift command — check NuGet versions against denominators
    parser = subparsers.add_parser(
        "version-drift",
        help="Check NuGet version drift for all confirmed LowCode families",
    )
    parser.add_argument(
        "--family",
        metavar="FAMILY",
        default=None,
        help="Limit check to one family (default: all confirmed LowCode families)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=None,
        help="Write drift report JSON to this path",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Print report as JSON to stdout",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the version-drift command."""
    from pathlib import Path as _Path
    from plugin_examples.publisher.version_drift_checker import run_version_drift_check, LOWCODE_FAMILIES
    import json as _json

    repo_root = _Path(__file__).resolve().parents[3]
    families = [args.family] if args.family else None
    report = run_version_drift_check(families=families, repo_root=repo_root)

    output_path = getattr(args, "output", None)
    if output_path:
        _Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        _Path(output_path).write_text(_json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    if getattr(args, "json_output", False):
        print(_json.dumps(report.to_dict(), indent=2))
    else:
        print(f"version-drift: {report.overall_verdict}")
        for r in report.families:
            drift_info = (
                f"{r.denominator_version} -> {r.latest_nuget_version}"
                if r.drift
                else f"{r.latest_nuget_version} (current)"
            )
            print(f"  {r.family}: {r.status} | {drift_info}")
        print(f"Drifted: {report.drifted_count} | Current: {report.current_count} | Errors: {report.error_count}")

    return 0 if report.overall_verdict in ("ALL_CURRENT", "DRIFT_DETECTED") else 1
