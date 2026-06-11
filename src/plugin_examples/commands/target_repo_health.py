"""Command: target-repo-health."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the target-repo-health subcommand."""
    # target-repo-health command — verify target repos for all LowCode families
    parser = subparsers.add_parser(
        "target-repo-health",
        help="Verify target repos for all confirmed LowCode families",
    )
    parser.add_argument(
        "--family",
        metavar="FAMILY",
        default=None,
        help="Limit check to one family",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=None,
        help="Write health report JSON to this path",
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
    """Handle the target-repo-health command."""
    from pathlib import Path as _Path
    from plugin_examples.publisher.target_repo_health import run_target_repo_health_check
    import json as _json

    repo_root = _Path(__file__).resolve().parents[3]
    families = [args.family] if args.family else None
    report = run_target_repo_health_check(families=families, repo_root=repo_root)

    output_path = getattr(args, "output", None)
    if output_path:
        _Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        _Path(output_path).write_text(_json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    if getattr(args, "json_output", False):
        print(_json.dumps(report.to_dict(), indent=2))
    else:
        print(f"target-repo-health: {report.overall_verdict}")
        for r in report.families:
            print(f"  {r.family}: {r.status} (method={r.verification_method}, expected={r.expected_examples})")
        print(
            f"Healthy: {report.healthy_count} | Evidence-based: {report.evidence_based_count} | Inaccessible: {report.inaccessible_count}"
        )

    return 0 if report.overall_verdict in ("ALL_VERIFIED", "PARTIAL_VERIFICATION") else 1
