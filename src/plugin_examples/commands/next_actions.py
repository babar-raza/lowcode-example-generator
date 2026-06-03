"""Command: next-actions."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the next-actions subcommand."""
    # next-actions command — compute ranked action board from current state
    parser = subparsers.add_parser(
        "next-actions",
        help="Compute ranked next actions from current pipeline state",
    )
    parser.add_argument(
        "--output", metavar="PATH", default=None,
        help="Write action board JSON to this path",
    )
    parser.add_argument(
        "--markdown", metavar="PATH", default=None,
        help="Write action board markdown to this path",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Print action board as JSON to stdout",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the next-actions command."""
    from pathlib import Path as _Path
    from plugin_examples.portfolio_action_planner import compute_action_board, render_markdown
    import json as _json

    repo_root = _Path(__file__).resolve().parents[2]
    board = compute_action_board(repo_root)

    output_path = getattr(args, "output", None)
    if output_path:
        _Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        _Path(output_path).write_text(board.to_json(), encoding="utf-8")

    md_path = getattr(args, "markdown", None)
    if md_path:
        _Path(md_path).parent.mkdir(parents=True, exist_ok=True)
        _Path(md_path).write_text(render_markdown(board), encoding="utf-8")

    if getattr(args, "json_output", False):
        print(board.to_json())
    else:
        safe = board.safe_actions()
        blocked = board.blocked_actions()
        print(f"next-actions: {len(safe)} safe, {len(blocked)} blocked")
        for a in board.actions:
            marker = "SAFE" if a.safe_to_execute_now else "BLOCKED"
            print(f"  [{marker}] {a.id} ({a.family}) impact={a.impact}: {a.reason or a.current_state}")
    return 0
