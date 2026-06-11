"""Command: resolve-repo-access."""

from __future__ import annotations

import logging

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the resolve-repo-access subcommand."""
    # Resolve-repo-access command
    parser = subparsers.add_parser(
        "resolve-repo-access",
        help="Probe GitHub API access for family publish targets (read-only)",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        metavar="FAMILY",
        default=["cells", "words", "pdf"],
        help="Families to probe (default: cells words pdf)",
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
    """Handle the resolve-repo-access command."""
    from plugin_examples.family_config import load_family_config, DisabledFamilyError
    from plugin_examples.publisher.repo_access_resolver import resolve_repo_access
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args,
        command="resolve-repo-access",
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

    result = resolve_repo_access(families_input, verification_dir, promote_latest=True)

    summary = result["summary"]
    print(f"Repo access: {summary['accessible']}/{summary['total_checked']} accessible")
    for rec in result["families"]:
        family = rec["family"]
        ec = rec.get("error_classification", "unknown")
        can_read = rec.get("can_read", False)
        can_push = rec.get("can_push")
        status = "ACCESSIBLE" if can_read else f"BLOCKED ({ec})"
        perm = f", can_push={can_push}" if can_read else ""
        print(f"  {family}: {status}{perm}")
    print(f"live_publish_allowed: {summary['live_publish_allowed']}")
    report_path = verification_dir / "latest" / "family-repo-access-resolution.json"
    print(f"Report: {report_path}")
    _finalize_metrics_session(
        msession,
        items_discovered=summary["total_checked"],
        items_succeeded=summary["accessible"],
        items_failed=summary["total_checked"] - summary["accessible"],
    )
    return 0 if summary["accessible"] > 0 else 1
