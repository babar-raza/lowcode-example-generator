"""Command: discover-lowcode."""

from __future__ import annotations

import logging

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the discover-lowcode subcommand."""
    # Discover-LowCode command
    parser = subparsers.add_parser("discover-lowcode",
                                             help="Discovery-only sweep for all families")
    parser.add_argument("--all-families", action="store_true",
                                  help="Discover all enabled families")
    parser.add_argument("--family", help="Specific family to discover (single)")
    parser.add_argument("--families", nargs="+", metavar="FAMILY",
                                  help="Specific families to discover (list)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                                  help="Dry-run mode (default)")
    parser.add_argument("--promote-latest", action="store_true",
                                  help="Copy evidence to workspace/verification/latest/")
    parser.add_argument("--allow-experimental", action="store_true",
                                  help="Include experimental families")
    parser.add_argument("--rank", action="store_true",
                                  help="Compute and write generation readiness ranking")
    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the discover-lowcode command."""
    from plugin_examples.discovery_sweep import run_discovery_sweep, compute_generation_readiness
    from pathlib import Path as _Path

    # Resolve family list: --families list > --family single > --all-families
    families = None
    if getattr(args, "families", None):
        families = list(args.families)
    elif args.family:
        families = [args.family]

    repo_root = _Path(__file__).resolve().parents[3]

    msession, mcollector = _create_metrics_session(
        args, command="discover-lowcode",
        family=",".join(families) if families else "all",
        repo_root=repo_root,
    )

    result = run_discovery_sweep(
        families=families,
        all_families=args.all_families,
        promote_latest=args.promote_latest,
        allow_experimental=args.allow_experimental,
        repo_root=repo_root,
    )

    total = result.get("total_families", 0)
    eligible = result.get("eligible_count", 0)
    print(f"Discovery sweep: {total} families scanned, {eligible} with LowCode namespaces")
    for f in result.get("families", []):
        print(f"  {f['family']}: {f['status']}")

    # Compute and write generation readiness ranking
    if getattr(args, "rank", False) or True:  # always compute ranking after discovery
        import json as _json
        ranking_new = compute_generation_readiness(result.get("families", []), repo_root)
        ranking_path = (repo_root / "workspace" / "verification" / "latest"
                       / "family-generation-readiness-rank.json")
        ranking_path.parent.mkdir(parents=True, exist_ok=True)

        # Merge with existing entries to preserve families not in this run.
        # Single-family runs must not destroy multi-family data (GAP-NEW-01).
        existing_by_family: dict = {}
        if ranking_path.exists():
            try:
                _existing = _json.loads(ranking_path.read_text(encoding="utf-8", errors="replace"))
                if isinstance(_existing, list):
                    existing_by_family = {e["family"]: e for e in _existing if "family" in e}
            except (OSError, _json.JSONDecodeError, KeyError):
                pass

        # Update only the families from this run; preserve others
        for entry in ranking_new:
            existing_by_family[entry["family"]] = entry

        # Determine scope: complete when all enabled families were discovered
        _run_families = {f["family"] for f in result.get("families", [])}
        _scope = "complete" if _run_families >= set(existing_by_family.keys()) else "partial"

        merged = list(existing_by_family.values())
        ranking_path.write_text(_json.dumps(merged, indent=2), encoding="utf-8")
        logging.getLogger(__name__).info(
            "Generation readiness ranking written (scope=%s): %s", _scope, ranking_path
        )
        print(f"  readiness ranking: {len(merged)} families (scope={_scope})")

    _finalize_metrics_session(
        msession,
        items_discovered=total,
        items_succeeded=eligible,
        items_failed=total - eligible,
    )
    return 0

