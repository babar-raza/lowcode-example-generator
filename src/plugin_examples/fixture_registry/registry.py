"""Fixture registry management — track available test data files."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FixtureEntry:
    """A single fixture file entry."""
    filename: str
    source_type: str  # github, generated, local
    source_path: str
    provenance: str  # e.g. "aspose-cells/Aspose.Cells-for-.NET:master:Examples/Data"
    available: bool = True


@dataclass
class FixtureRegistry:
    """Registry of available fixture files for a family."""
    family: str
    fixtures: list[FixtureEntry] = field(default_factory=list)

    def has_fixture(self, filename: str) -> bool:
        return any(
            f.filename == filename and f.available
            for f in self.fixtures
        )

    def get_available_fixtures(self) -> list[FixtureEntry]:
        return [f for f in self.fixtures if f.available]

    def add_fixture(self, entry: FixtureEntry) -> None:
        # Avoid duplicates by filename
        existing = [f for f in self.fixtures if f.filename == entry.filename]
        if not existing:
            self.fixtures.append(entry)


def build_fixture_registry(
    family: str,
    fixture_sources: list[dict],
) -> FixtureRegistry:
    """Build a fixture registry from family config fixture sources.

    Args:
        family: Family name.
        fixture_sources: List of fixture source dicts from family config.

    Returns:
        FixtureRegistry with discovered fixtures.
    """
    registry = FixtureRegistry(family=family)

    for source in fixture_sources:
        source_type = source.get("type", "unknown")
        owner = source.get("owner", "")
        repo = source.get("repo", "")
        branch = source.get("branch", "main")
        paths = source.get("paths", [])

        provenance = f"{owner}/{repo}:{branch}"

        for path in paths:
            if source_type == "github":
                files = _fetch_github_file_listing(owner, repo, branch, path)
                if files is not None:
                    for fname in files:
                        registry.add_fixture(FixtureEntry(
                            filename=fname,
                            source_type=source_type,
                            source_path=f"{provenance}:{path}/{fname}",
                            provenance=provenance,
                            available=True,
                        ))
                    continue
                # API failed — register path as degraded entry
                logger.warning("GitHub API unavailable for %s/%s:%s, registering path only", owner, repo, path)

            registry.add_fixture(FixtureEntry(
                filename=path,
                source_type=source_type,
                source_path=f"{provenance}:{path}",
                provenance=provenance,
                available=source_type != "github",  # unknown availability when API failed
            ))

    logger.info("Fixture registry built for %s: %d entries", family, len(registry.fixtures))
    return registry


def write_fixture_registry(
    registry: FixtureRegistry,
    manifests_dir: Path,
) -> Path:
    """Write fixture registry to manifests directory."""
    manifests_dir.mkdir(parents=True, exist_ok=True)
    path = manifests_dir / "fixture-registry.json"

    data = {
        "family": registry.family,
        "fixtures": [
            {
                "filename": f.filename,
                "source_type": f.source_type,
                "source_path": f.source_path,
                "provenance": f.provenance,
                "available": f.available,
            }
            for f in registry.fixtures
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Fixture registry written: %s", path)
    return path


def _fetch_github_file_listing(
    owner: str, repo: str, branch: str, path: str,
) -> list[str] | None:
    """Fetch file listing from GitHub API with fallback chain.

    Tries in order:
    1. Contents API (works for small directories)
    2. Trees API (works for large directories, needs GITHUB_TOKEN)
    3. Local cache from previous successful fetch

    Returns list of filenames on success, None on failure (graceful degradation).
    """
    try:
        import requests
    except ImportError:
        logger.warning("requests not installed, cannot fetch GitHub file listing")
        return _load_fixture_cache(owner, repo, branch, path)

    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    # Strategy 1: Contents API
    files = _try_contents_api(owner, repo, branch, path, headers)
    if files is not None:
        _save_fixture_cache(owner, repo, branch, path, files)
        return files

    # Strategy 2: Trees API (gets full tree, filter to path)
    if token:
        files = _try_trees_api(owner, repo, branch, path, headers)
        if files is not None:
            _save_fixture_cache(owner, repo, branch, path, files)
            return files

    # Strategy 3: Local cache fallback
    cached = _load_fixture_cache(owner, repo, branch, path)
    if cached is not None:
        logger.info("Using cached fixture listing for %s/%s:%s/%s", owner, repo, branch, path)
        return cached

    return None


def _try_contents_api(
    owner: str, repo: str, branch: str, path: str, headers: dict,
) -> list[str] | None:
    """Try GitHub Contents API."""
    import requests
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            logger.debug("Contents API returned %d for %s", resp.status_code, url)
            return None
        items = resp.json()
        if not isinstance(items, list):
            return None
        return [item["name"] for item in items if item.get("type") == "file"]
    except Exception as e:
        logger.debug("Contents API request failed: %s", e)
        return None


def _try_trees_api(
    owner: str, repo: str, branch: str, path: str, headers: dict,
) -> list[str] | None:
    """Try GitHub Trees API (recursive) and filter to path prefix."""
    import requests
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.debug("Trees API returned %d", resp.status_code)
            return None
        data = resp.json()
        tree = data.get("tree", [])
        prefix = path.rstrip("/") + "/"
        files = []
        for item in tree:
            if item.get("type") == "blob" and item.get("path", "").startswith(prefix):
                rel = item["path"][len(prefix):]
                if "/" not in rel:  # Only direct children
                    files.append(rel)
        return files if files else None
    except Exception as e:
        logger.debug("Trees API request failed: %s", e)
        return None


_CACHE_DIR = Path.home() / ".cache" / "plugin-examples" / "fixture-listings"


def _cache_key(owner: str, repo: str, branch: str, path: str) -> Path:
    safe = f"{owner}__{repo}__{branch}__{path.replace('/', '__')}.json"
    return _CACHE_DIR / safe


def _save_fixture_cache(owner: str, repo: str, branch: str, path: str, files: list[str]) -> None:
    try:
        key = _cache_key(owner, repo, branch, path)
        key.parent.mkdir(parents=True, exist_ok=True)
        with open(key, "w") as f:
            json.dump(files, f)
    except Exception:
        pass  # Cache write is best-effort


def _load_fixture_cache(owner: str, repo: str, branch: str, path: str) -> list[str] | None:
    try:
        key = _cache_key(owner, repo, branch, path)
        if key.exists():
            with open(key) as f:
                return json.load(f)
    except Exception:
        pass
    return None


def load_fixture_registry(manifests_dir: Path) -> FixtureRegistry | None:
    """Load fixture registry from manifests directory."""
    path = manifests_dir / "fixture-registry.json"
    if not path.exists():
        return None

    with open(path) as f:
        data = json.load(f)

    registry = FixtureRegistry(family=data.get("family", "unknown"))
    for entry in data.get("fixtures", []):
        registry.add_fixture(FixtureEntry(
            filename=entry["filename"],
            source_type=entry["source_type"],
            source_path=entry["source_path"],
            provenance=entry["provenance"],
            available=entry.get("available", True),
        ))

    return registry
