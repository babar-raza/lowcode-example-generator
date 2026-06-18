"""Check that generated documentation files are not stale.

Usage:
    python scripts/check_doc_freshness.py [--max-age-days N]

Exits with code 1 if any checked file exceeds the maximum age in days.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path


# Files to check: relative path -> date pattern to look for in content
_CHECKED_FILES: dict[str, str] = {
    "docs/development/open-taskcard-closure-matrix.md": r"\*\*Matrix date:\*\*\s+(\d{4}-\d{2}-\d{2})",
}


def _extract_date(content: str, pattern: str) -> date | None:
    match = re.search(pattern, content)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated doc freshness")
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=7,
        help="Maximum allowed age in days (default: 7)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    today = date.today()
    cutoff = today - timedelta(days=args.max_age_days)

    failures: list[str] = []
    for rel_path, pattern in _CHECKED_FILES.items():
        path = repo_root / rel_path
        if not path.exists():
            failures.append(f"  MISSING: {rel_path}")
            continue
        content = path.read_text(encoding="utf-8")
        doc_date = _extract_date(content, pattern)
        if doc_date is None:
            failures.append(f"  NO DATE FOUND: {rel_path} (pattern: {pattern})")
            continue
        age = (today - doc_date).days
        if doc_date < cutoff:
            failures.append(
                f"  STALE: {rel_path} (date: {doc_date}, age: {age} days, max: {args.max_age_days})"
            )
        else:
            print(f"  OK: {rel_path} (date: {doc_date}, age: {age} days)")

    if failures:
        print("\nFRESHNESS CHECK FAILED:")
        for f in failures:
            print(f)
        return 1

    print("\nAll generated files are within freshness threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
