"""Command: formimporter-watch."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the formimporter-watch subcommand."""
    # formimporter-watch command — check FormImporter defect status vs NuGet version
    parser = subparsers.add_parser(
        "formimporter-watch",
        help="Check FormImporter defect status against latest NuGet version",
    )
    parser.add_argument(
        "--run-repro", action="store_true",
        help="Run repro harness if version has advanced beyond 26.5.0",
    )
    parser.add_argument(
        "--output", metavar="PATH",
        help="Write JSON report to this path",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the formimporter-watch command."""
    from pathlib import Path as _Path
    from plugin_examples.package_watcher.formimporter_watch import (
        check_formimporter, write_watch_report,
    )

    repo_root = _Path(__file__).resolve().parents[2]
    run_repro = getattr(args, "run_repro", False)
    output = getattr(args, "output", None)
    output_path = (
        _Path(output)
        if output
        else repo_root / "workspace" / "verification" / "latest" / "formimporter-watch-report.json"
    )

    result = check_formimporter(repo_root, run_repro=run_repro)
    write_watch_report(result, output_path)

    print(f"FormImporter Watch — {result.checked_at}")
    print(f"  Installed: {result.current_version or 'unknown'}")
    print(f"  NuGet latest: {result.latest_nuget_version or 'unknown'}")
    print(f"  Defect version: {result.defect_version}")
    print(f"  Version advanced: {result.version_advanced}")
    print(f"  Verdict: {result.verdict}")
    for note in result.notes:
        print(f"  NOTE: {note}")
    print(f"Report: {output_path}")
    return 0
