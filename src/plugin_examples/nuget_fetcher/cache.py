"""Local cache for downloaded .nupkg files."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def check_cache(target_path: Path, expected_hash: str | None = None) -> bool:
    """Check if a cached file exists and optionally matches the expected hash.

    Returns True if the file exists and (if expected_hash is provided) matches.
    """
    if not target_path.exists():
        return False
    if expected_hash is None:
        return True
    actual = compute_sha256(target_path)
    if actual == expected_hash:
        logger.debug("Cache hit: %s (hash match)", target_path)
        return True
    logger.warning(
        "Cache mismatch: %s expected=%s actual=%s",
        target_path,
        expected_hash,
        actual,
    )
    return False


def read_manifest(manifest_path: Path) -> dict | None:
    """Read a download manifest JSON, returning None if it doesn't exist."""
    if not manifest_path.exists():
        return None
    with open(manifest_path) as f:
        return json.load(f)


def write_manifest(manifest_path: Path, data: dict) -> None:
    """Write a manifest JSON file, creating parent dirs as needed."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Wrote manifest: %s", manifest_path)
