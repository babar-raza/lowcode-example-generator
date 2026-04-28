"""NuGet dependency resolution from .nuspec inside .nupkg files."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from plugin_examples.nuget_fetcher.cache import (
    check_cache,
    compute_sha256,
    write_manifest,
)
from plugin_examples.nuget_fetcher.fetcher import (
    NuGetFetchError,
    _download_nupkg,
)

logger = logging.getLogger(__name__)

# NuGet .nuspec XML namespace
_NUSPEC_NS = "http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd"
_NS_VARIANTS = [
    "http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd",
    "http://schemas.microsoft.com/packaging/2012/06/nuspec.xsd",
    "http://schemas.microsoft.com/packaging/2011/08/nuspec.xsd",
    "http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd",
    "",  # no namespace fallback
]


def _find_nuspec(nupkg_path: Path) -> str:
    """Extract the .nuspec XML string from a .nupkg zip file."""
    with zipfile.ZipFile(nupkg_path) as zf:
        nuspec_names = [n for n in zf.namelist() if n.endswith(".nuspec")]
        if not nuspec_names:
            raise NuGetFetchError(
                f"No .nuspec found inside {nupkg_path}"
            )
        return zf.read(nuspec_names[0]).decode("utf-8-sig")


def _parse_dependencies(
    nuspec_xml: str,
    target_frameworks: list[str],
) -> list[dict]:
    """Parse dependency entries from .nuspec XML for the best matching framework.

    Returns a list of dicts with 'id' and 'version' keys.
    """
    root = ET.fromstring(nuspec_xml)

    for ns in _NS_VARIANTS:
        prefix = f"{{{ns}}}" if ns else ""
        metadata = root.find(f"{prefix}metadata")
        if metadata is not None:
            deps_elem = metadata.find(f"{prefix}dependencies")
            if deps_elem is not None:
                return _extract_deps(deps_elem, prefix, target_frameworks)

    return []


def _extract_deps(
    deps_elem: ET.Element,
    prefix: str,
    target_frameworks: list[str],
) -> list[dict]:
    """Extract dependencies from a <dependencies> element."""
    # Try framework-specific groups first
    groups = deps_elem.findall(f"{prefix}group")
    if groups:
        return _match_framework_group(groups, prefix, target_frameworks)

    # Fall back to flat dependency list (no groups)
    result = []
    for dep in deps_elem.findall(f"{prefix}dependency"):
        dep_id = dep.get("id")
        dep_ver = dep.get("version", "")
        if dep_id:
            result.append({"id": dep_id, "version": _clean_version(dep_ver)})
    return result


def _match_framework_group(
    groups: list[ET.Element],
    prefix: str,
    target_frameworks: list[str],
) -> list[dict]:
    """Find the best matching framework group from the .nuspec."""
    # Build lookup: lowercase tfm → group element
    group_map: dict[str, ET.Element] = {}
    no_tfm_group: ET.Element | None = None

    for g in groups:
        tfm = (g.get("targetFramework") or "").strip()
        if tfm:
            group_map[tfm.lower()] = g
        else:
            no_tfm_group = g

    # Try each preferred TFM in order
    # Map common short names to .nuspec conventions
    tfm_aliases = {
        "netstandard2.0": [".netstandard2.0", "netstandard2.0"],
        "netstandard2.1": [".netstandard2.1", "netstandard2.1"],
        "net8.0": [".netcoreapp8.0", "net8.0"],
        "net6.0": [".netcoreapp6.0", "net6.0"],
        "net48": [".netframework4.8", "net48"],
    }

    for tfm in target_frameworks:
        candidates = tfm_aliases.get(tfm, [tfm])
        for candidate in candidates:
            matched = group_map.get(candidate.lower())
            if matched is not None:
                return _deps_from_group(matched, prefix)

    # Fall back to the group with no targetFramework (generic deps)
    if no_tfm_group is not None:
        return _deps_from_group(no_tfm_group, prefix)

    # No match at all — return empty
    logger.warning(
        "No matching dependency group for frameworks: %s", target_frameworks
    )
    return []


def _deps_from_group(group: ET.Element, prefix: str) -> list[dict]:
    result = []
    for dep in group.findall(f"{prefix}dependency"):
        dep_id = dep.get("id")
        dep_ver = dep.get("version", "")
        if dep_id:
            result.append({"id": dep_id, "version": _clean_version(dep_ver)})
    return result


def _clean_version(version_range: str) -> str:
    """Extract the minimum version from a NuGet version range.

    E.g., "[4.0.0, )" → "4.0.0", "(, 5.0.0]" → "5.0.0", "4.0.0" → "4.0.0"
    """
    v = version_range.strip().strip("[]() ")
    parts = v.split(",")
    # Take the first non-empty part (minimum version)
    for part in parts:
        part = part.strip()
        if part:
            return part
    return version_range.strip()


def resolve_dependencies(
    nupkg_path: Path,
    *,
    target_frameworks: list[str],
    max_depth: int = 2,
    run_dir: Path,
    family: str,
    _current_depth: int = 1,
    _seen: set[str] | None = None,
) -> list[dict]:
    """Resolve dependencies from a .nupkg file.

    Downloads dependency packages and recursively resolves their deps
    up to max_depth.

    Returns a list of dependency records for the dependency manifest.
    """
    if _seen is None:
        _seen = set()

    nuspec_xml = _find_nuspec(nupkg_path)
    direct_deps = _parse_dependencies(nuspec_xml, target_frameworks)

    all_deps: list[dict] = []
    deps_dir = run_dir / "packages" / family / "deps"

    for dep_info in direct_deps:
        dep_id = dep_info["id"]
        dep_version = dep_info["version"]
        dep_key = f"{dep_id}:{dep_version}".lower()

        if dep_key in _seen:
            continue
        _seen.add(dep_key)

        dep_path = deps_dir / f"{dep_id}.{dep_version}.nupkg"

        # Check cache
        if check_cache(dep_path):
            sha256 = compute_sha256(dep_path)
            source_url = ""
            logger.info("Cache hit for dependency %s %s", dep_id, dep_version)
        else:
            try:
                source_url = _download_nupkg(dep_id, dep_version, dep_path)
                sha256 = compute_sha256(dep_path)
            except Exception as e:
                logger.warning(
                    "Failed to download dependency %s %s: %s",
                    dep_id,
                    dep_version,
                    e,
                )
                all_deps.append({
                    "package_id": dep_id,
                    "version": dep_version,
                    "sha256": "",
                    "source_url": "",
                    "cached_path": "",
                    "depth": _current_depth,
                    "status": "failed",
                    "error": str(e),
                })
                continue

        record = {
            "package_id": dep_id,
            "version": dep_version,
            "sha256": sha256,
            "source_url": source_url,
            "cached_path": str(dep_path),
            "depth": _current_depth,
            "status": "ok",
        }
        all_deps.append(record)

        # Recurse if within depth limit
        if _current_depth < max_depth:
            transitive = resolve_dependencies(
                dep_path,
                target_frameworks=target_frameworks,
                max_depth=max_depth,
                run_dir=run_dir,
                family=family,
                _current_depth=_current_depth + 1,
                _seen=_seen,
            )
            all_deps.extend(transitive)

    return all_deps


def write_dependency_manifest(
    deps: list[dict],
    run_dir: Path,
    family: str,
) -> Path:
    """Write the dependency manifest JSON."""
    manifest_path = run_dir / "packages" / family / "dependency-manifest.json"
    write_manifest(manifest_path, {"dependencies": deps})
    return manifest_path


def update_package_lock(
    download_manifest: dict,
    deps: list[dict],
    manifests_dir: Path,
) -> Path:
    """Update workspace/manifests/package-lock.json with primary + dependency records."""
    lock_path = manifests_dir / "package-lock.json"

    if lock_path.exists():
        import json
        with open(lock_path) as f:
            lock = json.load(f)
    else:
        lock = {"packages": {}}

    pkg_id = download_manifest["package_id"]
    lock["packages"][pkg_id] = {
        "version": download_manifest["version"],
        "sha256": download_manifest["sha256"],
        "source_url": download_manifest["source_url"],
    }

    for dep in deps:
        if dep.get("status") == "ok":
            dep_id = dep["package_id"]
            lock["packages"][dep_id] = {
                "version": dep["version"],
                "sha256": dep["sha256"],
                "source_url": dep.get("source_url", ""),
                "is_dependency": True,
            }

    write_manifest(lock_path, lock)
    return lock_path
