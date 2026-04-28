"""Fixture registry management — track available test data files."""

from __future__ import annotations

import json
import logging
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
            # Register the path as a fixture source
            # In a live run, we'd fetch the file listing from GitHub
            # For now, register the path pattern
            registry.add_fixture(FixtureEntry(
                filename=path,
                source_type=source_type,
                source_path=f"{provenance}:{path}",
                provenance=provenance,
                available=True,
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
