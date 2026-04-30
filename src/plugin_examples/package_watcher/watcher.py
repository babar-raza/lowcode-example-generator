"""Watch NuGet packages for version updates."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UpdateCheck:
    """Result of checking for package updates."""
    family: str
    package_id: str
    current_version: str | None
    latest_version: str | None
    has_update: bool = False
    skipped: bool = False
    skip_reason: str | None = None


def check_for_updates(
    families: list[dict],
    manifests_dir: Path,
) -> list[UpdateCheck]:
    """Check configured families for NuGet package updates.

    Args:
        families: List of family config dicts.
        manifests_dir: Path to manifests directory.

    Returns:
        List of update check results.
    """
    results = []

    # Load current package lock
    lock_path = manifests_dir / "package-lock.json"
    lock: dict = {}
    if lock_path.exists():
        with open(lock_path) as f:
            lock = json.load(f)

    for family_cfg in families:
        family = family_cfg.get("family", "unknown")
        enabled = family_cfg.get("enabled", False)
        status = family_cfg.get("status", "disabled")

        if not enabled or status == "disabled":
            results.append(UpdateCheck(
                family=family,
                package_id=family_cfg.get("nuget", {}).get("package_id", ""),
                current_version=None,
                latest_version=None,
                skipped=True,
                skip_reason="Family is disabled",
            ))
            continue

        package_id = family_cfg.get("nuget", {}).get("package_id", "")
        current = lock.get("packages", {}).get(package_id, {}).get("version")

        latest = _resolve_latest_nuget_version(package_id)
        has_update = bool(latest and current and latest != current)

        results.append(UpdateCheck(
            family=family,
            package_id=package_id,
            current_version=current,
            latest_version=latest,
            has_update=has_update,
        ))

    logger.info("Update check: %d families checked", len(results))
    return results


def _resolve_latest_nuget_version(package_id: str) -> str | None:
    """Resolve the latest stable version from NuGet v3 API.

    Returns None on failure (graceful degradation).
    """
    try:
        import requests
    except ImportError:
        logger.warning("requests not installed, cannot resolve NuGet version")
        return None

    url = f"https://api.nuget.org/v3-flatcontainer/{package_id.lower()}/index.json"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            logger.warning("NuGet API returned %d for %s", resp.status_code, package_id)
            return None
        data = resp.json()
        versions = data.get("versions", [])
        if not versions:
            return None
        # Filter to stable versions (no '-' in version string)
        stable = [v for v in versions if "-" not in v]
        return stable[-1] if stable else versions[-1]
    except Exception as e:
        logger.warning("NuGet API request failed: %s", e)
        return None


def write_monthly_report(
    results: list[UpdateCheck],
    verification_dir: Path,
) -> Path:
    """Write monthly run report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "monthly-run-report.json"

    data = {
        "families_checked": len(results),
        "updates_found": len([r for r in results if r.has_update]),
        "skipped": len([r for r in results if r.skipped]),
        "results": [
            {
                "family": r.family,
                "package_id": r.package_id,
                "current_version": r.current_version,
                "latest_version": r.latest_version,
                "has_update": r.has_update,
                "skipped": r.skipped,
                "skip_reason": r.skip_reason,
            }
            for r in results
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Monthly report written: %s", path)
    return path
