"""Command: verify-remote — post-merge remote truth verification."""

from __future__ import annotations

import json
import os


def add_parser(subparsers):
    """Register the verify-remote subcommand."""
    parser = subparsers.add_parser(
        "verify-remote",
        help="Verify publication state against GitHub remote (read-only)",
    )
    parser.add_argument(
        "--publication-record", metavar="PATH", required=True,
        help="Path to publication record JSON file",
    )
    parser.add_argument(
        "--output", metavar="PATH", default=None,
        help="Path to write verification results JSON",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the verify-remote command."""
    from pathlib import Path
    from plugin_examples.publisher.remote_truth_verifier import (
        run_remote_truth_check,
        write_remote_truth_report,
    )

    record_path = Path(args.publication_record)
    if not record_path.exists():
        print(f"ERROR: Publication record not found: {record_path}")
        return 1

    records = json.loads(record_path.read_text(encoding="utf-8"))
    if isinstance(records, dict):
        records = [records]

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    results = run_remote_truth_check(records, token)

    if args.output:
        output_path = Path(args.output)
        write_remote_truth_report(results, output_path)
        print(f"Results written to {output_path}")
    else:
        for r in results:
            status = "MERGED" if r.pr_merged else r.pr_state
            err = f" (error: {r.error})" if r.error else ""
            print(f"  {r.owner}/{r.repo}#{r.pr_number}: {status}{err}")

    errors = sum(1 for r in results if r.error)
    return 1 if errors > 0 else 0
