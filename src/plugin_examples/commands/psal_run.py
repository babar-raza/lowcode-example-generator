"""psal-run command — run the PSAL multi-family autonomous execution loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def run(args: argparse.Namespace) -> None:
    """Execute the psal-run command."""
    from plugin_examples.psal.orchestrator import NON_LOWCODE_FAMILIES, run_all_families

    families = None
    if getattr(args, "families", None):
        families = list(args.families)

    max_iterations = getattr(args, "max_iterations", 3)
    dry_run = getattr(args, "dry_run", True)
    template_mode = getattr(args, "template_mode", False)
    json_output = getattr(args, "json_output", False)
    repo_root = Path(getattr(args, "repo_root", None) or ".").resolve()

    result = run_all_families(
        families=families,
        max_iterations=max_iterations,
        dry_run=dry_run,
        template_mode=template_mode,
        repo_root=repo_root,
    )

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        completeness = result.get("completeness", {})
        print(f"PSAL Run Complete")
        print(f"  Families: {result['total_families']}")
        print(f"  Accepted: {result['accepted']}")
        print(f"  Blocked: {result['blocked']}")
        print(f"  Escalated: {result['escalated']}")
        print(f"  Errors: {result['errors']}")
        print(f"  Completeness: {'PASS' if completeness.get('passed') else 'FAIL'}")
        if completeness.get("missing"):
            print(f"  Missing: {', '.join(completeness['missing'])}")
        print()
        for fam, rec in result.get("families", {}).items():
            print(f"  {fam:12s} {rec['terminal_state']:30s} iter={rec['iterations']} verdict={rec.get('verdict', '')}")


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the psal-run subcommand."""
    parser = subparsers.add_parser(
        "psal-run",
        help="Run the PSAL multi-family autonomous execution loop",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        metavar="FAMILY",
        help="Specific family slugs to run (default: all non-LowCode)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Max governance loop iterations per family (default: 3)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run pipeline in dry-run mode (default: true)",
    )
    parser.add_argument(
        "--template-mode",
        action="store_true",
        default=False,
        help="Use template code generation instead of LLM",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root path",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON",
    )
    parser.set_defaults(func=run)
