"""sprint-governance command — run the post-sprint autonomy loop.

Provides summary classification, loop decision, quality scoring,
and evidence bundle validation for sprint governance.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def run(args: argparse.Namespace) -> None:
    """Execute the sprint-governance command."""
    from plugin_examples.sprint_governance.loop_controller import (
        classify_and_decide,
        save_loop_state,
    )
    from plugin_examples.sprint_governance.models import LoopState
    from plugin_examples.sprint_governance.summary_parser import (
        classify_raw_text,
        parse_summary,
    )

    sprint_name = args.sprint_name
    summary_file = getattr(args, "summary_file", None)
    max_iterations = getattr(args, "max_iterations", 3)
    json_output = getattr(args, "json_output", False)
    repo_root = Path(getattr(args, "repo_root", None) or ".").resolve()

    # Load or create loop state
    state_dir = repo_root / ".local" / "sprint-governance"
    state_path = state_dir / f"{sprint_name}-loop-state.json"
    state = LoopState.load(state_path)
    state.sprint_name = sprint_name
    state.max_iterations = max_iterations

    # Parse summary if provided
    summary = None
    if summary_file:
        summary_path = Path(summary_file)
        if summary_path.exists():
            text = summary_path.read_text(encoding="utf-8")
            try:
                summary = parse_summary(text)
            except ValueError as exc:
                classification = classify_raw_text(text)
                result = {
                    "sprint_name": sprint_name,
                    "parse_error": str(exc),
                    "classification": str(classification),
                    "recommendation": "Run plan hardening (P2) then execution (P3)",
                }
                if json_output:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Parse error: {exc}")
                    print(f"Classification: {classification}")
                sys.exit(1)

    # Make decision
    decision = classify_and_decide(summary, state)
    state.iteration += 1
    state.decisions.append(decision)

    # Save state
    save_loop_state(state, state_path)

    result = {
        "sprint_name": sprint_name,
        "iteration": state.iteration,
        "classification": str(decision.summary_classification),
        "next_stage": str(decision.next_stage),
        "reason": decision.reason,
        "loop_state_path": str(state_path),
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"Sprint: {sprint_name}")
        print(f"Iteration: {state.iteration}/{max_iterations}")
        print(f"Classification: {decision.summary_classification}")
        print(f"Next stage: {decision.next_stage}")
        print(f"Reason: {decision.reason}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the sprint-governance subcommand."""
    parser = subparsers.add_parser(
        "sprint-governance",
        help="Run the post-sprint governance loop controller",
    )
    parser.add_argument("--sprint-name", required=True, help="Sprint identifier")
    parser.add_argument("--summary-file", default=None, help="Path to P3 summary YAML")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max loop iterations")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output as JSON")
    parser.set_defaults(func=run)
