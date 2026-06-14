"""Command: validate-publish-targets."""

from __future__ import annotations

import logging

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the validate-publish-targets subcommand."""
    # Validate-publish-targets command
    parser = subparsers.add_parser(
        "validate-publish-targets",
        help="Check publish readiness for family configs",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        metavar="FAMILY",
        default=["cells", "words", "pdf"],
        help="Families to validate (default: cells words pdf)",
    )
    parser.add_argument(
        "--promote-latest",
        action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the validate-publish-targets command."""
    from pathlib import Path as _Path

    from plugin_examples.family_config import DisabledFamilyError, load_family_config
    from plugin_examples.publisher.publish_readiness import (
        check_publish_readiness,
        write_publish_readiness_report,
    )

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args,
        command="validate-publish-targets",
        repo_root=repo_root,
    )
    config_dir = repo_root / "pipeline" / "configs" / "families"
    verification_dir = repo_root / "workspace" / "verification"

    families_input = []
    for fname in args.families:
        config_path = config_dir / f"{fname}.yml"
        try:
            cfg = load_family_config(config_path)
            families_input.append((fname, cfg, str(config_path)))
        except DisabledFamilyError:
            families_input.append((fname, None, str(config_path)))
        except FileNotFoundError:
            families_input.append((fname, None, str(config_path)))
        except Exception as exc:
            logging.getLogger(__name__).warning("Could not load %s: %s", fname, exc)
            families_input.append((fname, None, str(config_path)))

    result = check_publish_readiness(families_input)
    report_path = write_publish_readiness_report(result, verification_dir)

    print(f"Publish readiness: {result['publish_ready_count']}/{result['total_families']} ready")
    for rec in result["families"]:
        status = "READY" if rec["publish_ready"] else f"BLOCKED ({rec['blocked_reason']})"
        print(f"  {rec['family']}: {status}")
    print(f"Report: {report_path}")
    _finalize_metrics_session(
        msession,
        items_discovered=result["total_families"],
        items_succeeded=result["publish_ready_count"],
        items_failed=result["total_families"] - result["publish_ready_count"],
    )
    return 0 if result["publish_ready_count"] > 0 else 1
