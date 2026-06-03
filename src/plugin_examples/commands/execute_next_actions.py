"""Command: execute-next-actions."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the execute-next-actions subcommand."""
    # execute-next-actions command — planner-driven execution loop
    parser = subparsers.add_parser(
        "execute-next-actions",
        help="Run planner-driven execution loop: plan, execute safe actions, replan",
    )
    parser.add_argument(
        "--max-cycles", type=int, default=5,
        help="Maximum number of plan-execute cycles (default: 5)",
    )
    parser.add_argument(
        "--evidence-dir", metavar="PATH", default=None,
        help="Directory for cycle evidence files",
    )
    parser.add_argument(
        "--dry-run-remote", action="store_true", default=True,
        help="Do not execute remote publish/merge actions (default: true)",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Print loop result as JSON to stdout",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the execute-next-actions command."""
    from pathlib import Path as _Path
    from plugin_examples.planner_loop import run_execution_loop
    import json as _json

    repo_root = _Path(__file__).resolve().parents[2]
    evidence_dir = _Path(args.evidence_dir) if args.evidence_dir else repo_root / "workspace" / "verification" / "latest"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    result = run_execution_loop(
        repo_root=repo_root,
        evidence_dir=evidence_dir,
        max_cycles=args.max_cycles,
        dry_run_remote=args.dry_run_remote,
    )

    if getattr(args, "json_output", False):
        print(_json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Execution loop: {len(result.cycles)} cycles, "
              f"{result.total_executed} executed, {result.total_deferred} deferred")
        print(f"Stop reason: {result.stop_reason}")
        for c in result.cycles:
            print(f"  Cycle {c.cycle}: HEAD={c.generated_from_head} "
                  f"executed={c.executed} deferred={len(c.deferred)}")
        if result.final_board:
            safe = result.final_board.safe_actions()
            blocked = result.final_board.blocked_actions()
            print(f"Final board: {len(safe)} safe, {len(blocked)} blocked "
                  f"(HEAD={result.final_board.generated_from_head})")
    return 0
