"""Command: post-publication-verify."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the post-publication-verify subcommand."""
    # post-publication-verify command — verify published PR packages
    parser = subparsers.add_parser(
        "post-publication-verify",
        help="Verify published examples in local PR dry-run packages",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., pdf)")
    parser.add_argument(
        "--output", metavar="PATH",
        help="Write verification report to this path",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the post-publication-verify command."""
    from pathlib import Path as _Path
    from plugin_examples.publisher.batch_publisher import PDF_PR_PACKAGES
    from plugin_examples.publisher.post_publication_verifier import (
        run_post_publication_verification, write_verification_report,
    )

    repo_root = _Path(__file__).resolve().parents[3]
    family = args.family
    output = getattr(args, "output", None)
    output_path = (
        _Path(output)
        if output
        else repo_root / "workspace" / "verification" / "latest" / f"{family}-post-publication-verification.json"
    )

    # Resolve packages for family
    if family == "pdf":
        packages = PDF_PR_PACKAGES
    else:
        # Single-package family
        packages = [(1, f"{family}-controlled-pilot")]

    packages_base = repo_root / "workspace" / "pr-dry-run"
    report = run_post_publication_verification(family, packages, packages_base)
    write_verification_report(report, output_path)

    print(f"Post-publication verification: {family}")
    print(f"  Verdict: {report.verdict}")
    print(f"  Packages: {report.total_packages}")
    for p in report.packages:
        print(f"  PR#{p.pr_number} {p.package_name}: {p.verdict} ({p.verified_examples}/{p.total_examples})")
    print(f"Report: {output_path}")
    return 0 if report.all_verified else 1
