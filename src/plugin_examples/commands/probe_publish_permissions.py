"""Command: probe-publish-permissions."""

from __future__ import annotations

import logging

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the probe-publish-permissions subcommand."""
    # Probe-publish-permissions command
    parser = subparsers.add_parser(
        "probe-publish-permissions",
        help="Read-only probe of GitHub push permissions for family publish targets",
    )
    parser.add_argument(
        "--families", nargs="+", metavar="FAMILY", default=["cells", "words", "pdf"],
        help="Families to probe (default: cells words pdf)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Dry-run mode (always on — probe is always read-only)",
    )
    parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the probe-publish-permissions command."""
    from plugin_examples.family_config import load_family_config, DisabledFamilyError
    from plugin_examples.publisher.publish_permission_probe import probe_publish_permissions
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args, command="probe-publish-permissions", repo_root=repo_root,
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

    result = probe_publish_permissions(families_input, verification_dir, dry_run=True, promote_latest=True)

    summary = result["summary"]
    print(f"Permission probe: {summary['permission_ready']}/{summary['total_probed']} families have push permission")
    for rec in result["families"]:
        family = rec["family"]
        status = rec.get("probe_status", "unknown")
        if status == "skipped":
            print(f"  {family}: SKIPPED ({rec.get('skip_reason', '')})")
        elif rec.get("pr_permission_ready"):
            print(f"  {family}: PUSH_READY (can_read={rec.get('can_read')}, can_push={rec.get('can_push')})")
        else:
            print(f"  {family}: NOT_READY ({rec.get('error_classification', 'unknown')})")
    print(f"live_publish_authorized: {summary['live_publish_authorized']}")
    report_path = verification_dir / "latest" / "publish-permission-probe.json"
    print(f"Report: {report_path}")
    _finalize_metrics_session(
        msession,
        items_discovered=summary["total_probed"],
        items_succeeded=summary["permission_ready"],
        items_failed=summary["total_probed"] - summary["permission_ready"],
    )
    return 0 if summary["permission_ready"] > 0 else 1

