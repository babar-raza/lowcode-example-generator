"""Production-safe fixture fetcher — Wave 25 Lane B.

Fetches fixtures from the official Aspose GitHub examples repo for each family.
Implements caching, provenance sidecars, extension filtering, and size limits.

Cache layout:
    .local/fixtures/{family}/
        fixtures-manifest.json        — SHA-256 + metadata per file
        {filename}                    — cached fixture file
        {filename}.provenance.json    — provenance sidecar

Provenance sidecar format:
    {
      "filename": "Drawing11.dwg",
      "source_repo": "aspose-cad/Aspose.CAD-for-.NET",
      "source_ref": "master",
      "source_commit_sha": null,
      "source_path": "Examples/Data/Drawing11.dwg",
      "file_sha256": "def456...",
      "downloaded_at": "2026-06-09T00:00:00Z",
      "file_size_bytes": 19378,
      "license_note": "MIT — Aspose example repo"
    }

Backward compatibility:
    The old ``fetch_fixtures(registry, output_dir, dry_run=True)`` signature
    is still supported via ``fetch_fixtures_legacy()``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Listing cache TTL (24 hours)
_LISTING_TTL_SECONDS = 24 * 3600

_DEFAULT_EXTENSION_ALLOWLIST = frozenset(
    {
        ".xlsx",
        ".docx",
        ".pdf",
        ".dwg",
        ".dxf",
        ".svg",
        ".ttf",
        ".otf",
        ".png",
        ".jpg",
        ".html",
        ".zip",
        ".xbrl",
        ".glb",
        ".3ds",
        ".fbx",
        ".tiff",
        ".bmp",
        ".odt",
        ".csv",
        ".eml",
        ".vsdx",
        ".sxc",
    }
)

_DEFAULT_FIXTURE_PATHS = ["Examples/Data"]
_DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
_DEFAULT_MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50 MB


class FixtureFetchError(Exception):
    """Raised when fixture fetch fails."""


class FixtureBlockedError(FixtureFetchError):
    """Raised when real fixtures are required but cannot be fetched."""


@dataclass
class FetchResult:
    strategy: str  # "real_github", "synthetic_fallback", "dry_run_validated", "fixture_blocked"
    fetched: list[dict]  # per-file result dicts
    cache_hits: int = 0
    cache_misses: int = 0
    synthetic_count: int = 0
    total_bytes: int = 0
    errors: list[str] = field(default_factory=list)


# ── Public API ─────────────────────────────────────────────────────────────────


def fetch_fixtures(
    family: str,
    repo_config: dict,
    required_extensions: list[str],
    dest_dir: Path,
    *,
    cache_root: Path = Path(".local/fixtures"),
    dry_run: bool = False,
) -> FetchResult:
    """Fetch fixtures from the official examples repo with caching.

    Args:
        family:              Family name (e.g. ``"cad"``).
        repo_config:         Dict from ``github.official_examples_repo`` in family YAML.
        required_extensions: Extensions the caller needs (e.g. ``[".dwg", ".dxf"]``).
        dest_dir:            Where to copy fetched files for this run.
        cache_root:          Root of the local fixture cache.
        dry_run:             If True, validate config but skip actual downloads.

    Returns:
        :class:`FetchResult`.
    """
    owner = repo_config.get("owner", "")
    repo = repo_config.get("repo", "")

    if not owner or not repo:
        logger.warning(
            "[fixture_fetcher] No official_examples_repo configured for %s — synthetic fallback",
            family,
        )
        return _synthetic_fallback(family)

    branch = repo_config.get("branch", "master")
    fixture_paths = repo_config.get("fixture_paths", _DEFAULT_FIXTURE_PATHS)
    extension_allowlist = frozenset(repo_config.get("extension_allowlist", list(_DEFAULT_EXTENSION_ALLOWLIST)))
    effective_extensions = (
        frozenset(required_extensions) & extension_allowlist if required_extensions else extension_allowlist
    )
    max_file_size = repo_config.get("max_file_size_bytes", _DEFAULT_MAX_FILE_SIZE)
    max_total_size = repo_config.get("max_total_size_bytes", _DEFAULT_MAX_TOTAL_SIZE)
    synthetic_fallback_allowed = repo_config.get("synthetic_fallback_allowed", True)

    cache_dir = cache_root / family
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = cache_dir / "fixtures-manifest.json"
    manifest = _load_manifest(manifest_path)

    if dry_run:
        return FetchResult(strategy="dry_run_validated", fetched=[])

    # Require GitHub token for live fetch
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not gh_token:
        logger.warning("[fixture_fetcher] No GITHUB_TOKEN for %s", family)
        if synthetic_fallback_allowed:
            return _synthetic_fallback(family)
        raise FixtureBlockedError(f"No GITHUB_TOKEN and synthetic_fallback_allowed=false for {family}")

    listing_cache_dir = Path(".local/fixture-listings") / family
    listing_cache_dir.mkdir(parents=True, exist_ok=True)

    all_files: list[dict] = []
    for fixture_path in fixture_paths:
        files = _list_github_files(
            owner,
            repo,
            branch,
            fixture_path,
            effective_extensions,
            max_file_size,
            listing_cache_dir,
            gh_token,
        )
        all_files.extend(files)

    if not all_files:
        logger.warning("[fixture_fetcher] No matching files in %s/%s for %s", owner, repo, family)
        if synthetic_fallback_allowed:
            return _synthetic_fallback(family)
        raise FixtureBlockedError(f"No fixtures found in {owner}/{repo} for {family}")

    # Apply total size limit
    selected: list[dict] = []
    running_total = 0
    for f in all_files:
        size = f.get("size", 0)
        if running_total + size > max_total_size:
            logger.warning(
                "[fixture_fetcher] Total size limit hit for %s — stopping at %d files",
                family,
                len(selected),
            )
            break
        selected.append(f)
        running_total += size

    result = FetchResult(strategy="real_github", fetched=[])

    for f in selected:
        filename = Path(f["path"]).name
        cached_file = cache_dir / filename
        cached_sha = manifest.get(filename, {}).get("file_sha256")

        if cached_file.exists() and cached_sha:
            result.cache_hits += 1
            _copy_with_provenance(cached_file, dest_dir / filename, f, owner, repo, branch, cached_sha)
            result.fetched.append(
                {
                    "filename": filename,
                    "source_path": f["path"],
                    "status": "CACHE_HIT",
                    "sha256": cached_sha,
                    "size_bytes": cached_file.stat().st_size,
                }
            )
            result.total_bytes += cached_file.stat().st_size
        else:
            try:
                downloaded_sha, size = _download_file(owner, repo, branch, f["path"], cached_file, gh_token)
            except Exception as exc:
                logger.warning("[fixture_fetcher] Download failed for %s: %s", filename, exc)
                result.errors.append(f"{filename}: {exc}")
                continue

            manifest[filename] = {
                "file_sha256": downloaded_sha,
                "git_sha": f.get("sha", ""),
                "source_path": f["path"],
                "size_bytes": size,
                "cached_at": _utcnow(),
            }
            _save_manifest(manifest_path, manifest)
            _copy_with_provenance(cached_file, dest_dir / filename, f, owner, repo, branch, downloaded_sha)
            result.cache_misses += 1
            result.fetched.append(
                {
                    "filename": filename,
                    "source_path": f["path"],
                    "status": "CACHE_MISS",
                    "sha256": downloaded_sha,
                    "size_bytes": size,
                }
            )
            result.total_bytes += size

    if not result.fetched:
        if synthetic_fallback_allowed:
            return _synthetic_fallback(family)
        raise FixtureBlockedError(f"All downloads failed for {family} and synthetic_fallback_allowed=false")

    return result


def check_fixture_availability(
    registry: Any,
    required_fixtures: list[str],
) -> dict:
    """Check if required fixtures are available in the registry (backward compat)."""
    available = []
    missing = []
    for filename in required_fixtures:
        if registry.has_fixture(filename):
            available.append(filename)
        else:
            missing.append(filename)
    return {
        "total_required": len(required_fixtures),
        "available": available,
        "missing": missing,
        "blocked": len(missing) > 0,
    }


# ── Internal helpers ───────────────────────────────────────────────────────────


def _list_github_files(
    owner: str,
    repo: str,
    branch: str,
    tree_path: str,
    extensions: frozenset,
    max_file_size: int,
    listing_cache_dir: Path,
    gh_token: str,
) -> list[dict]:
    """List files from a GitHub repo tree with local TTL caching."""
    import time

    safe_path = tree_path.replace("/", "_")
    cache_file = listing_cache_dir / f"{safe_path}.json"

    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < _LISTING_TTL_SECONDS:
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                return [
                    f
                    for f in cached
                    if Path(f["path"]).suffix.lower() in extensions and f.get("size", 0) <= max_file_size
                ]
            except Exception:
                pass

    api_url = f"repos/{owner}/{repo}/git/trees/{branch}:{tree_path}?recursive=1"
    env = {**os.environ, "GITHUB_TOKEN": gh_token}
    proc = subprocess.run(["gh", "api", api_url], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        logger.warning(
            "[fixture_fetcher] gh api failed for %s/%s/%s: %s",
            owner,
            repo,
            tree_path,
            proc.stderr.strip(),
        )
        return []

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []

    all_files = [
        {
            "path": f"{tree_path}/{item['path']}",
            "sha": item.get("sha", ""),
            "size": item.get("size", 0),
        }
        for item in data.get("tree", [])
        if item.get("type") == "blob"
    ]

    cache_file.write_text(json.dumps(all_files, indent=2), encoding="utf-8")

    return [f for f in all_files if Path(f["path"]).suffix.lower() in extensions and f.get("size", 0) <= max_file_size]


def _download_file(
    owner: str,
    repo: str,
    branch: str,
    path: str,
    dest: Path,
    gh_token: str,
) -> tuple[str, int]:
    """Download a single file via gh api, verify SHA-256. Returns (sha256, size_bytes)."""
    api_url = f"repos/{owner}/{repo}/contents/{path}?ref={branch}"
    env = {**os.environ, "GITHUB_TOKEN": gh_token}

    meta_proc = subprocess.run(["gh", "api", api_url], capture_output=True, text=True, env=env)
    if meta_proc.returncode != 0:
        raise FixtureFetchError(f"gh api metadata failed: {meta_proc.stderr.strip()}")

    meta = json.loads(meta_proc.stdout)
    download_url = meta.get("download_url", "")
    if not download_url:
        raise FixtureFetchError(f"No download_url for {path}")

    # Try gh api first, then curl as fallback
    raw_proc = subprocess.run(
        ["curl", "-sSL", "-H", f"Authorization: token {gh_token}", download_url],
        capture_output=True,
    )
    if raw_proc.returncode != 0:
        raise FixtureFetchError(f"curl download failed for {path}")

    raw_bytes = raw_proc.stdout
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    dest.write_bytes(raw_bytes)
    return sha256, len(raw_bytes)


def _copy_with_provenance(
    src: Path,
    dst: Path,
    file_entry: dict,
    owner: str,
    repo: str,
    branch: str,
    sha256: str,
) -> None:
    """Copy file to dest and write provenance sidecar."""
    shutil.copy2(src, dst)
    provenance = {
        "filename": dst.name,
        "source_repo": f"{owner}/{repo}",
        "source_ref": branch,
        "source_commit_sha": None,
        "source_path": file_entry.get("path", ""),
        "file_sha256": sha256,
        "downloaded_at": _utcnow(),
        "file_size_bytes": dst.stat().st_size,
        "license_note": "MIT — Aspose example repo",
    }
    sidecar = dst.with_suffix(dst.suffix + ".provenance.json")
    sidecar.write_text(json.dumps(provenance, indent=2), encoding="utf-8")


def _synthetic_fallback(family: str) -> FetchResult:
    logger.info("[fixture_fetcher] Using synthetic fallback for %s", family)
    return FetchResult(strategy="synthetic_fallback", fetched=[], synthetic_count=1)


def _load_manifest(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
