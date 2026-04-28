"""NuGet v3 package fetcher with version resolution and caching."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import requests

from plugin_examples.nuget_fetcher.cache import (
    check_cache,
    compute_sha256,
    read_manifest,
    write_manifest,
)

logger = logging.getLogger(__name__)

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
) -> str:
    """Download a .nupkg from the NuGet flat container. Returns the source URL."""
    base_url = _get_service_url("PackageBaseAddress")
    lower_id = package_id.lower()
    lower_version = version.lower()
    url = f"{base_url}{lower_id}/{lower_version}/{lower_id}.{lower_version}.nupkg"

    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NuGetFetchError(
            f"Failed to download {package_id} {version}: {e}"
        ) from e

    with open(target_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info("Downloaded %s %s → %s", package_id, version, target_path)
    return url


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
            logger.info("Cache hit for %s %s", package_id, version)
            return existing

    # Download
    source_url = _download_nupkg(package_id, version, nupkg_path)
    sha256 = compute_sha256(nupkg_path)

    manifest = {
        "package_id": package_id,
        "version": version,
        "sha256": sha256,
        "source_url": source_url,
        "cached_path": str(nupkg_path),
    }

    write_manifest(manifest_path, manifest)
    return manifest
