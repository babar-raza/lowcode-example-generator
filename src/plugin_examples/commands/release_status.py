"""Command: release-status."""

from __future__ import annotations

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the release-status subcommand."""
    # Release-status command
    parser = subparsers.add_parser(
        "release-status",
        help="Report per-family release state from evidence files (read-only)",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        metavar="FAMILY",
        default=None,
        help="Families to report on (default: cells words pdf diagram email slides)",
    )
    parser.add_argument(
        "--promote-latest",
        action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )
    parser.add_argument(
        "--validate-bundle",
        metavar="BUNDLE_DIR",
        default=None,
        help=(
            "Run EvidenceValidator on a sprint bundle directory after computing release status. "
            "Prints a validation summary; exits 1 if the bundle fails any FAILURE-severity rule."
        ),
    )

    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the release-status command."""
    from pathlib import Path as _Path

    from plugin_examples.publisher.release_status import (
        ALL_RELEASE_FAMILIES,
        compute_release_status,
        write_release_status_report,
    )

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args,
        command="release-status",
        repo_root=repo_root,
    )
    verification_dir = repo_root / "workspace" / "verification"

    families = list(args.families or ALL_RELEASE_FAMILIES)
    status = compute_release_status(families, verification_dir)
    report_path = write_release_status_report(status, verification_dir)

    print(f"Release status: {len(families)} families")
    for rec in status["families"]:
        fam = rec["family"]
        sha = rec["last_merge_sha"] or "not merged"
        validation = rec["last_post_merge_validation_status"]
        count = rec["published_examples_count"]
        scope = rec.get("release_scope_status", "UNKNOWN")
        print(
            f"  {fam}: merged={sha[:12] if rec['last_merge_sha'] else 'no'}, "
            f"examples={count}, post_merge={validation}, scope={scope}"
        )
        print(f"    next: {rec['next_required_action']}")
    print(f"  all_merged: {status['all_merged']}")
    print(f"  all_post_merge_validated: {status['all_post_merge_validated']}")
    print(f"Report: {report_path}")

    # Optional: validate sprint evidence bundle
    if getattr(args, "validate_bundle", None):
        from plugin_examples.evidence_validator import EvidenceValidator as _EV

        _bundle_dir = _Path(args.validate_bundle)
        _source_root = _Path(__file__).resolve().parent
        print(f"\nValidating bundle: {_bundle_dir}")
        _ev_result = _EV(bundle_dir=_bundle_dir, source_root=_source_root).validate()
        print(f"  Rules: {_ev_result.passed} passed, {_ev_result.failed} failed / {_ev_result.total_rules} total")
        for _r in _ev_result.rule_results:
            if not _r.passed:
                print(f"  [FAIL] {_r.rule_id}: {_r.failure_detail[:100]}")
        if not _ev_result.overall_valid:
            print(f"  Bundle INVALID — {_ev_result.failed} rule(s) failed")
            return 1
        print(f"  Bundle VALID — all {_ev_result.total_rules} rules pass")

    _finalize_metrics_session(
        msession,
        items_discovered=len(families),
        items_succeeded=len(families),
        items_failed=0,
    )
    return 0
