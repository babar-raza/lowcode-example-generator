"""new_sprint.py — generate a new sprint coordinator from template.

Usage:
    python scripts/new_sprint.py --sprint wave26 --date 20260610 --lanes A,B,C,Z
    python scripts/new_sprint.py --sprint wave26 --date 20260610 --lanes A,B,Z --force

Generates: scripts/_wave{sprint}_coordinator.py from the template.
Does NOT overwrite unless --force is passed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


_TEMPLATE_PATH = Path(__file__).parent / "templates" / "sprint_coordinator_template.py"
_SCRIPTS_DIR = Path(__file__).parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a new sprint coordinator script.")
    parser.add_argument("--sprint", required=True, help="Sprint/wave identifier (e.g. wave26)")
    parser.add_argument("--date", required=True, help="Sprint date (e.g. 20260610)")
    parser.add_argument("--lanes", required=True, help="Comma-separated lane letters (e.g. A,B,C,Z)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    args = parser.parse_args(argv)

    sprint = args.sprint.strip()
    date = args.date.strip()
    lanes = args.lanes.strip()

    output_path = _SCRIPTS_DIR / f"_{sprint}_coordinator.py"

    if output_path.exists() and not args.force:
        print(
            f"ERROR: {output_path} already exists. "
            f"Pass --force to overwrite.",
            file=sys.stderr,
        )
        return 1

    if not _TEMPLATE_PATH.exists():
        print(f"ERROR: Template not found at {_TEMPLATE_PATH}", file=sys.stderr)
        return 1

    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    content = (
        template
        .replace("$SPRINT", sprint)
        .replace("$DATE", date)
        .replace("$LANES", lanes)
    )

    output_path.write_text(content, encoding="utf-8")
    print(f"Created {output_path}. Add lane implementations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
