"""Fetch fixture files from configured sources."""

from __future__ import annotations

import logging
from pathlib import Path

from plugin_examples.fixture_registry.registry import FixtureEntry, FixtureRegistry

logger = logging.getLogger(__name__)


class FixtureFetchError(Exception):
    """Raised when fixture fetch fails."""


def fetch_fixtures(
    registry: FixtureRegistry,
    output_dir: Path,
    *,
    dry_run: bool = True,
) -> list[dict]:
    """Fetch fixtures from registry sources to output directory.

    In dry-run mode (default), validates that sources are configured but
    does not actually download files. Live fetching requires GitHub API access.

    Args:
        registry: Fixture registry with source entries.
        output_dir: Directory to write fetched fixtures.
        dry_run: If True, skip actual downloads.

    Returns:
        List of fetch result dicts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for entry in registry.get_available_fixtures():
        result = {
            "filename": entry.filename,
            "source": entry.source_path,
            "provenance": entry.provenance,
        }

        if dry_run:
            result["status"] = "dry_run"
            result["message"] = "Skipped (dry-run mode)"
        else:
            # Live fetch would use GitHub API or local copy
            result["status"] = "not_implemented"
            result["message"] = "Live fixture fetching not yet implemented"

        results.append(result)

    logger.info(
        "Fixture fetch: %d entries processed (dry_run=%s)",
        len(results), dry_run,
    )
    return results


def check_fixture_availability(
    registry: FixtureRegistry,
    required_fixtures: list[str],
) -> dict:
    """Check if required fixtures are available in the registry.

    Args:
        registry: Fixture registry to check against.
        required_fixtures: List of required fixture filenames.

    Returns:
        Dict with available, missing, and blocking info.
    """
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
