"""Mine existing C# examples from configured source repositories."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MinedExample:
    """An existing example discovered from source repos."""
    example_id: str
    source_path: str
    provenance: str
    used_symbols: list[str] = field(default_factory=list)
    validated: bool = False
    stale: bool = False
    stale_reason: str | None = None


@dataclass
class MiningResult:
    """Result of example mining."""
    family: str
    examples: list[MinedExample] = field(default_factory=list)
    stale_examples: list[MinedExample] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.examples)

    @property
    def stale_count(self) -> int:
        return len(self.stale_examples)


def mine_examples(
    family: str,
    example_sources: list[dict],
    *,
    catalog: dict | None = None,
) -> MiningResult:
    """Mine existing examples from configured sources.

    In the current implementation, this registers the configured source
    paths. Live mining would clone/fetch from GitHub and parse .cs files.

    Args:
        family: Family name.
        example_sources: List of example source dicts from family config.
        catalog: Optional API catalog for symbol validation.

    Returns:
        MiningResult with discovered examples.
    """
    result = MiningResult(family=family)

    catalog_symbols = set()
    if catalog:
        for ns in catalog.get("namespaces", []):
            for t in ns.get("types", []):
                catalog_symbols.add(t.get("full_name", ""))

    for source in example_sources:
        source_type = source.get("type", "unknown")
        owner = source.get("owner", "")
        repo = source.get("repo", "")
        branch = source.get("branch", "main")
        paths = source.get("paths", [])

        provenance = f"{owner}/{repo}:{branch}"

        if source_type == "github":
            files = _fetch_github_cs_files(owner, repo, branch, paths)
            if files:
                for file_info in files:
                    symbols = extract_symbols_from_code(file_info["content"]) if file_info.get("content") else []
                    stale = bool(catalog_symbols and symbols and not catalog_symbols.intersection(symbols))
                    example = MinedExample(
                        example_id=f"{family}:{file_info['path']}",
                        source_path=file_info["path"],
                        provenance=provenance,
                        used_symbols=symbols,
                        validated=bool(symbols),
                        stale=stale,
                        stale_reason="No matched API symbols" if stale else None,
                    )
                    result.examples.append(example)
                    if stale:
                        result.stale_examples.append(example)
                continue

        for path in paths:
            example = MinedExample(
                example_id=f"{family}:{path}",
                source_path=path,
                provenance=provenance,
            )
            result.examples.append(example)

    logger.info("Mined %d example sources for %s", result.total, family)
    return result


def _fetch_github_cs_files(
    owner: str, repo: str, branch: str, paths: list[str],
) -> list[dict] | None:
    """Fetch .cs file listings from GitHub. Returns None on failure."""
    try:
        import requests
    except ImportError:
        return None

    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    results = []
    for path in paths:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            items = resp.json()
            if not isinstance(items, list):
                continue
            for item in items:
                if item.get("type") == "file" and item.get("name", "").endswith(".cs"):
                    results.append({"path": item["path"], "name": item["name"], "content": None})
        except Exception as e:
            logger.warning("GitHub API failed for %s: %s", path, e)
            continue

    return results if results else None


def extract_symbols_from_code(code: str) -> list[str]:
    """Extract potential type/method references from C# code.

    Simple regex-based extraction — not a full parser.

    Args:
        code: C# source code string.

    Returns:
        List of extracted symbol references.
    """
    symbols = set()

    # Match qualified type names (Aspose.Cells.LowCode.SpreadsheetLocker)
    qualified = re.findall(r'\b(Aspose\.\w+(?:\.\w+)*)\b', code)
    symbols.update(qualified)

    # Match new ClassName() instantiations
    new_instances = re.findall(r'\bnew\s+(\w+(?:\.\w+)*)\s*\(', code)
    symbols.update(new_instances)

    return sorted(symbols)


def write_examples_index(
    result: MiningResult,
    manifests_dir: Path,
) -> Path:
    """Write existing examples index to manifests."""
    manifests_dir.mkdir(parents=True, exist_ok=True)
    path = manifests_dir / "existing-examples-index.json"

    data = {
        "family": result.family,
        "total_examples": result.total,
        "stale_count": result.stale_count,
        "examples": [
            {
                "example_id": ex.example_id,
                "source_path": ex.source_path,
                "provenance": ex.provenance,
                "used_symbols": ex.used_symbols,
                "validated": ex.validated,
                "stale": ex.stale,
                "stale_reason": ex.stale_reason,
            }
            for ex in result.examples
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Examples index written: %s", path)
    return path


def write_stale_report(
    result: MiningResult,
    verification_dir: Path,
) -> Path:
    """Write stale examples report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "stale-existing-examples.json"

    data = {
        "family": result.family,
        "stale_count": result.stale_count,
        "stale_examples": [
            {
                "example_id": ex.example_id,
                "source_path": ex.source_path,
                "stale_reason": ex.stale_reason,
                "used_symbols": ex.used_symbols,
            }
            for ex in result.stale_examples
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Stale report written: %s", path)
    return path
