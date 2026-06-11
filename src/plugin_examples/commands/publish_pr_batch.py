"""Command: publish-pr-batch."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the publish-pr-batch subcommand."""
    # publish-pr-batch command — orchestrate all PR packages for a family in one command
    parser = subparsers.add_parser(
        "publish-pr-batch",
        help="Batch publish all PR packages for a family (dry-run or live)",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., pdf)")
    batch_publish_mode = parser.add_mutually_exclusive_group()
    batch_publish_mode.add_argument(
        "--publish",
        action="store_true",
        help="Perform live PR creation (requires APPROVE_LIVE_PR gate)",
    )
    batch_publish_mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate publication without creating live PRs (default)",
    )
    parser.add_argument(
        "--approval-token",
        metavar="TOKEN",
        help="Approval token (must be APPROVE_LIVE_PR for live mode)",
    )
    parser.add_argument(
        "--promote-latest",
        action="store_true",
        default=True,
        help="Promote results to verification/latest/ (default: True)",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the publish-pr-batch command."""
    import json as _json
    from pathlib import Path as _Path
    from plugin_examples.publisher.batch_publisher import run_batch_publish, write_batch_report

    repo_root = _Path(__file__).resolve().parents[3]
    family = args.family
    live_mode = getattr(args, "publish", False)
    approval_token = getattr(args, "approval_token", None)

    print(f"publish-pr-batch: family={family}, live_mode={live_mode}")

    result = run_batch_publish(
        family=family,
        repo_root=repo_root,
        live_mode=live_mode,
        approval_token=approval_token,
        promote_latest=True,
    )

    output_path = repo_root / "workspace" / "verification" / "latest" / f"{family}-batch-publish-report.json"
    write_batch_report(result, output_path)

    print(f"Batch result: {result.verdict}")
    print(f"  Total packages: {result.total}")
    print(f"  Succeeded: {result.succeeded}")
    print(f"  Failed: {result.failed}")
    print(f"  Blocked: {result.blocked}")
    for r in result.results:
        status = "PASS" if r.simulation_passed else ("ERROR" if r.error else "BLOCKED")
        print(f"  PR#{r.pr_number} {r.package_name}: {status}")
    print(f"Report: {output_path}")
    return 0 if result.failed == 0 else 1
