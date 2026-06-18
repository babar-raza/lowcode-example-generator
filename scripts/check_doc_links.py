"""Check relative Markdown links in docs/ for broken targets.

Checks only local relative file links (not external URLs). Ignores archive
and audit directories by default to avoid noise from historical files.

Usage:
    python scripts/check_doc_links.py [--root docs/] [--include-archive] [--include-root]

Exits with code 1 if any broken relative links are found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_ANCHOR_PATTERN = re.compile(r"^#")
_CODE_FENCE = re.compile(r"^```")

_SKIP_DIRS = {"_archive", "_audit"}


def _strip_code_blocks(content: str) -> str:
    """Remove content inside fenced code blocks to avoid false positives from examples."""
    lines = content.splitlines()
    result = []
    in_fence = False
    for line in lines:
        if _CODE_FENCE.match(line):
            in_fence = not in_fence
            result.append("")
            continue
        result.append("" if in_fence else line)
    return "\n".join(result)


def _is_external(href: str) -> bool:
    parsed = urlparse(href)
    return bool(parsed.scheme) and parsed.scheme in ("http", "https", "ftp", "mailto")


def _resolve(source_file: Path, href: str, repo_root: Path) -> Path | None:
    """Resolve a relative href from source_file to an absolute path."""
    # Strip anchor fragment
    href = href.split("#")[0]
    if not href:
        return None  # anchor-only link; skip
    target = (source_file.parent / href).resolve()
    return target


_ROOT_FILES = ("AGENTS.md", "README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md")


def check_links(
    root: Path, include_archive: bool = False, extra_files: list[Path] | None = None
) -> list[str]:
    """Return a list of broken-link error messages."""
    errors: list[str] = []
    md_files = sorted(root.rglob("*.md"))
    if extra_files:
        md_files = sorted(set(md_files) | set(extra_files))

    for md_file in md_files:
        # Skip archive/audit unless explicitly included
        parts = set(md_file.parts)
        if not include_archive and any(skip in parts for skip in _SKIP_DIRS):
            continue

        raw = md_file.read_text(encoding="utf-8", errors="replace")
        content = _strip_code_blocks(raw)
        for match in _LINK_PATTERN.finditer(content):
            href = match.group(2).strip()
            if _is_external(href):
                continue
            if _ANCHOR_PATTERN.match(href):
                continue  # same-page anchor; skip

            target = _resolve(md_file, href, root)
            if target is None:
                continue

            if not target.exists():
                rel_source = md_file.relative_to(root.parent)
                errors.append(f"  BROKEN: [{match.group(1)}]({href}) in {rel_source}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check relative Markdown links in docs/")
    parser.add_argument(
        "--root",
        default="docs",
        help="Root directory to scan (default: docs/)",
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        default=False,
        help="Include _archive/ and _audit/ directories in link check",
    )
    parser.add_argument(
        "--include-root",
        action="store_true",
        default=False,
        help="Also check root-level .md files (AGENTS.md, README.md, CONTRIBUTING.md, etc.)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    docs_root = repo_root / args.root

    if not docs_root.exists():
        print(f"ERROR: directory not found: {docs_root}", file=sys.stderr)
        return 1

    extra: list[Path] = []
    if args.include_root:
        extra = [repo_root / f for f in _ROOT_FILES if (repo_root / f).exists()]

    print(f"Checking relative links in {docs_root} ...")
    if extra:
        print(f"  + root files: {[f.name for f in extra]}")
    errors = check_links(docs_root, include_archive=args.include_archive, extra_files=extra)

    if errors:
        print(f"\nLINK CHECK FAILED ({len(errors)} broken links):")
        for e in errors:
            print(e)
        return 1

    print(f"OK: 0 broken relative links found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
