"""Command: sync-taskcard-docs."""

from __future__ import annotations

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the sync-taskcard-docs subcommand."""
    # Sync-taskcard-docs command
    parser = subparsers.add_parser(
        "sync-taskcard-docs",
        help="Generate docs/development/open-taskcard-closure-matrix.md from JSON matrix (read-only)",
    )
    parser.add_argument(
        "--promote-latest", action="store_true",
        help="No-op (included for CLI consistency; output always written to docs/development/)",
    )
    
    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the sync-taskcard-docs command."""
    import json as _json
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[2]
    msession, mcollector = _create_metrics_session(
        args, command="sync-taskcard-docs", repo_root=repo_root,
    )
    matrix_path = repo_root / "workspace" / "verification" / "latest" / "open-taskcard-closure-matrix.json"
    output_path = repo_root / "docs" / "development" / "open-taskcard-closure-matrix.md"

    if not matrix_path.exists():
        print(f"ERROR: Taskcard matrix not found: {matrix_path}")
        print("  Run discover-lowcode or create the matrix first.")
        return 1

    try:
        matrix = _json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, _json.JSONDecodeError) as exc:
        print(f"ERROR: Cannot read taskcard matrix: {exc}")
        return 1

    taskcards = matrix.get("taskcards", [])
    matrix_date = matrix.get("matrix_date", "unknown")
    sprint = matrix.get("sprint", "unknown")

    open_cards = [tc for tc in taskcards if tc.get("status") == "OPEN"]
    closed_cards = [tc for tc in taskcards if tc.get("status") in ("CLOSED", "CLOSED_VERIFIED")]
    total = len(taskcards)
    open_count = len(open_cards)
    closed_count = len(closed_cards)

    lines = [
        "<!-- GENERATED — do not edit manually. Run: python -m plugin_examples sync-taskcard-docs -->",
        f"# Open Taskcard Closure Matrix",
        "",
        f"**Matrix date:** {matrix_date}",
        f"**Sprint:** {sprint}",
        f"**Total:** {total} | **Open:** {open_count} | **Closed:** {closed_count}",
        "",
        "---",
        "",
        "## Open Taskcards",
        "",
        "| ID | Title | Blocking |",
        "|----|-------|----------|",
    ]
    if open_cards:
        for tc in open_cards:
            tc_id = tc.get("id", "")
            title = tc.get("title", "")
            blocking = tc.get("blocking") or ""
            lines.append(f"| `{tc_id}` | {title} | {blocking} |")
    else:
        lines.append("| — | No open taskcards | — |")

    lines += [
        "",
        "---",
        "",
        "## Closed Taskcards",
        "",
        "| ID | Title | Closed In |",
        "|----|-------|-----------|",
    ]
    for tc in closed_cards:
        tc_id = tc.get("id", "")
        title = tc.get("title", "")
        closed_in = tc.get("closed_in") or ""
        lines.append(f"| `{tc_id}` | {title} | {closed_in} |")

    content = "\n".join(lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    print(f"sync-taskcard-docs: {total} taskcards ({open_count} open, {closed_count} closed)")
    print(f"  Source: {matrix_path}")
    print(f"  Output: {output_path}")
    _finalize_metrics_session(
        msession, items_discovered=total, items_succeeded=total, items_failed=0,
    )
    return 0

