#!/usr/bin/env python
"""TC-G2 / TC-J5: Detect CLI commands in source that are not documented in docs/reference/cli.md.

Returns exit code 0 when all commands are documented, exit code 1 when gaps are found.

Usage:
    python scripts/check_cli_docs_drift.py [--json]

Source of truth: src/plugin_examples/commands/__init__.py  (register_all function)
Documentation target: docs/reference/cli.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_INIT = REPO_ROOT / "src" / "plugin_examples" / "commands" / "__init__.py"
CLI_MD = REPO_ROOT / "docs" / "reference" / "cli.md"


def extract_source_commands(path: Path) -> list[str]:
    """Extract command names from register_all() in commands/__init__.py.

    Looks for:
        from plugin_examples.commands.some_command import add_parser as _name
    and converts module names (snake_case) to CLI names (kebab-case).
    Also handles the `register` pattern used by probe_registry.
    """
    content = path.read_text(encoding="utf-8")
    # Match both patterns:
    #   from plugin_examples.commands.MODULE import add_parser as _alias
    #   from plugin_examples.commands.MODULE import register as _alias
    pattern = re.compile(
        r"from plugin_examples\.commands\.(\w+)\s+import\s+(?:add_parser|register)\s+as\s+\w+"
    )
    modules = pattern.findall(content)
    # Convert snake_case module name → kebab-case CLI name
    return [m.replace("_", "-") for m in modules]


def extract_documented_commands(path: Path) -> set[str]:
    """Extract command names documented in cli.md.

    Looks for backtick-quoted command names in the Commands table rows:
        | `command-name` | Description | ...

    Only matches kebab-case names that start with a letter (not -- flags or digits).
    Command names must contain at least one letter and no leading dashes.
    """
    content = path.read_text(encoding="utf-8")
    # Match backtick-quoted tokens at start of table rows where the token:
    # - starts with a lowercase letter
    # - contains only letters, digits, and hyphens (kebab-case command names)
    # - is at least 2 chars (rules out single-digit tier numbers)
    pattern = re.compile(r"^\|\s*`([a-z][a-z0-9-]+)`", re.MULTILINE)
    return set(pattern.findall(content))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", dest="use_json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    source_commands = extract_source_commands(COMMANDS_INIT)
    documented_commands = extract_documented_commands(CLI_MD)

    missing_from_docs = [c for c in source_commands if c not in documented_commands]
    phantom_in_docs = [c for c in documented_commands if c not in source_commands]

    result = {
        "source_command_count": len(source_commands),
        "documented_command_count": len(documented_commands),
        "missing_from_docs": sorted(missing_from_docs),
        "phantom_in_docs": sorted(phantom_in_docs),
        "drift_detected": bool(missing_from_docs or phantom_in_docs),
    }

    if args.use_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Source commands:     {result['source_command_count']}")
        print(f"Documented commands: {result['documented_command_count']}")
        if missing_from_docs:
            print(f"\nMISSING from docs/reference/cli.md ({len(missing_from_docs)}):")
            for cmd in sorted(missing_from_docs):
                print(f"  - {cmd}")
        if phantom_in_docs:
            print(f"\nPHANTOM in docs (not in source) ({len(phantom_in_docs)}):")
            for cmd in sorted(phantom_in_docs):
                print(f"  - {cmd}")
        if not missing_from_docs and not phantom_in_docs:
            print("\nNo drift detected — all source commands are documented.")

    return 1 if result["drift_detected"] else 0


if __name__ == "__main__":
    sys.exit(main())
