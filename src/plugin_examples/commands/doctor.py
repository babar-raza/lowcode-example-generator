"""Command: doctor — startup health check."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the doctor subcommand."""
    parser = subparsers.add_parser("doctor", help="Run startup health checks")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the doctor command."""
    from plugin_examples.health.doctor import (
        format_results_json,
        format_results_text,
        run_all_checks,
    )

    results = run_all_checks()

    if args.json_output:
        print(format_results_json(results))
    else:
        print(format_results_text(results))

    has_failures = any(r.status == "FAIL" and r.required for r in results)
    return 1 if has_failures else 0
