"""NuGet v3 package fetcher with version resolution, caching, and SHA-256 manifest.

Wave 25 Lane D adds a global SHA-256 manifest at ``.local/nuget-cache/sha-manifest.json``
that records per-package-per-version SHA-256 hashes and revalidates cached files
at most once per 24 hours. This is NOT reliant on ETag or Content-MD5 from CDN headers.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

from plugin_examples.nuget_fetcher.cache import (
    check_cache,
    compute_sha256,
    read_manifest,
    write_manifest,
)

logger = logging.getLogger(__name__)

# SHA manifest location and revalidation TTL
_SHA_MANIFEST_PATH = Path(".local/nuget-cache/sha-manifest.json")
_REVALIDATION_TTL_SECONDS = 24 * 3600


def _load_sha_manifest() -> dict:
    if _SHA_MANIFEST_PATH.exists():
        try:
            return json.loads(_SHA_MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_sha_manifest(manifest: dict) -> None:
    _SHA_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SHA_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _revalidate_sha_manifest(package_id: str, version: str, nupkg_path: Path) -> str | None:
    """Verify cached .nupkg against SHA manifest; re-download if corrupted.

    Returns the verified SHA-256, or None if the file does not exist.
    Only revalidates at most once per 24 hours per package+version.
    """
    import time

    if not nupkg_path.exists():
        return None

    manifest = _load_sha_manifest()
    key = f"{package_id}/{version}"
    entry = manifest.get(key, {})
    stored_sha = entry.get("sha256")
    last_revalidated = entry.get("last_revalidated")

    now = time.time()
    if last_revalidated:
        try:
            last_ts = datetime.fromisoformat(last_revalidated).timestamp()
            if now - last_ts < _REVALIDATION_TTL_SECONDS:
                # Not time to revalidate yet
                return stored_sha
        except Exception:
            pass

    # Revalidate
    actual_sha = compute_sha256(nupkg_path)
    if stored_sha and actual_sha != stored_sha:
        logger.warning(
            "NuGet SHA mismatch for %s %s: expected=%s actual=%s — deleting corrupted file",
            package_id, version, stored_sha, actual_sha,
        )
        nupkg_path.unlink(missing_ok=True)
        return None

    # Update manifest with revalidated timestamp
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest[key] = {
        "sha256": actual_sha,
        "downloaded_at": entry.get("downloaded_at", now_iso),
        "last_revalidated": now_iso,
        "source": f"https://api.nuget.org/v3-flatcontainer/{package_id.lower()}/{version.lower()}/{package_id.lower()}.{version.lower()}.nupkg",
    }
    _save_sha_manifest(manifest)
    return actual_sha


def _record_sha_manifest(package_id: str, version: str, sha256: str, source_url: str) -> None:
    """Record a freshly downloaded package SHA in the global manifest."""
    manifest = _load_sha_manifest()
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    key = f"{package_id}/{version}"
    manifest[key] = {
        "sha256": sha256,
        "downloaded_at": now_iso,
        "last_revalidated": now_iso,
        "source": source_url,
    }
    _save_sha_manifest(manifest)

NUGET_SERVICE_INDEX = "https://api.nuget.org/v3/index.json"

# Semver pre-release indicator: anything with a hyphen after the version core
_PRERELEASE_RE = re.compile(r"^\d+\.\d+\.\d+-.+")


class PackageNotFoundError(Exception):
    """Raised when a NuGet package cannot be found."""


class NuGetFetchError(Exception):
    """Raised on network or API errors during NuGet fetch."""


def _get_service_url(resource_type: str) -> str:
    """Resolve a NuGet v3 service URL from the service index."""
    try:
        resp = requests.get(NUGET_SERVICE_INDEX, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NuGetFetchError(f"Failed to fetch NuGet service index: {e}") from e

    data = resp.json()
    for resource in data.get("resources", []):
        if resource.get("@type", "").startswith(resource_type):
            return resource["@id"]

    raise NuGetFetchError(
        f"NuGet service index missing resource type: {resource_type}"
    )


def resolve_latest_stable(
    package_id: str,
    *,
    allow_prerelease: bool = False,
) -> str:
    """Resolve the latest stable version of a NuGet package.

    Uses the NuGet v3 flat container (PackageBaseAddress) to list versions.
    """
    base_url = _get_service_url("PackageBaseAddress")
    lower_id = package_id.lower()
    url = f"{base_url}{lower_id}/index.json"

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.HTTPError as e:
        if resp.status_code == 404:
            raise PackageNotFoundError(
                f"Package not found on NuGet: {package_id}"
            ) from e
        raise NuGetFetchError(
            f"Failed to list versions for {package_id}: {e}"
        ) from e
    except requests.RequestException as e:
        raise NuGetFetchError(
            f"Network error listing versions for {package_id}: {e}"
        ) from e

    versions: list[str] = resp.json().get("versions", [])
    if not versions:
        raise PackageNotFoundError(
            f"No versions found for package: {package_id}"
        )

    if not allow_prerelease:
        versions = [v for v in versions if not _PRERELEASE_RE.match(v)]

    if not versions:
        raise PackageNotFoundError(
            f"No stable versions found for package: {package_id}"
        )

    return versions[-1]


def _download_nupkg(
    package_id: str,
    version: str,
    target_path: Path,
    *,
    max_retries: int = 3,
) -> str:
    """Download a .nupkg from the NuGet flat container. Returns the source URL."""
    base_url = _get_service_url("PackageBaseAddress")
    lower_id = package_id.lower()
    lower_version = version.lower()
    url = f"{base_url}{lower_id}/{lower_version}/{lower_id}.{lower_version}.nupkg"

    target_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=300, stream=True)
            resp.raise_for_status()

            with open(target_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)

            logger.info("Downloaded %s %s → %s", package_id, version, target_path)
            return url
        except requests.RequestException as e:
            last_error = e
            if attempt < max_retries:
                logger.warning(
                    "Download attempt %d/%d for %s %s failed: %s — retrying",
                    attempt, max_retries, package_id, version, e,
                )
            # Clean up partial download
            if target_path.exists():
                target_path.unlink()

    raise NuGetFetchError(
        f"Failed to download {package_id} {version} after {max_retries} attempts: {last_error}"
    ) from last_error


def fetch_package(
    package_id: str,
    version_policy: str,
    *,
    pinned_version: str | None = None,
    allow_prerelease: bool = False,
    run_dir: Path,
    family: str,
) -> dict:
    """Fetch a NuGet package and write the download manifest.

    Args:
        package_id: NuGet package ID.
        version_policy: "latest-stable" or "pinned".
        pinned_version: Version to use when version_policy is "pinned".
        allow_prerelease: Whether to include pre-release versions.
        run_dir: Path to workspace/runs/{run_id}/.
        family: Family name (e.g., "cells").

    Returns:
        The download manifest dict.
    """
    # Resolve version
    if version_policy == "pinned":
        if not pinned_version:
            raise ValueError(
                "pinned_version is required when version_policy is 'pinned'"
            )
        version = pinned_version
    else:
        version = resolve_latest_stable(
            package_id, allow_prerelease=allow_prerelease
        )

    logger.info("Resolved %s version: %s", package_id, version)

    pkg_dir = run_dir / "packages" / family
    nupkg_path = pkg_dir / f"{package_id}.{version}.nupkg"
    manifest_path = pkg_dir / "download-manifest.json"

    # Check cache
    existing = read_manifest(manifest_path)
    if existing and existing.get("version") == version:
        cached = Path(existing.get("cached_path", ""))
        if check_cache(cached, existing.get("sha256")):
            # Revalidate against SHA manifest (max once per 24h)
            verified_sha = _revalidate_sha_manifest(package_id, version, cached)
            if verified_sha is not None:
                logger.info("Cache hit for %s %s (sha revalidated)", package_id, version)
                return existing
            # SHA mismatch — file was deleted; fall through to re-download
            logger.info("Cache invalidated for %s %s — re-downloading", package_id, version)

    # Download
    source_url = _download_nupkg(package_id, version, nupkg_path)
    sha256 = compute_sha256(nupkg_path)

    # Record in SHA manifest
    _record_sha_manifest(package_id, version, sha256, source_url)

    manifest = {
        "package_id": package_id,
        "version": version,
        "sha256": sha256,
        "source_url": source_url,
        "cached_path": str(nupkg_path),
    }

    write_manifest(manifest_path, manifest)
    return manifest
