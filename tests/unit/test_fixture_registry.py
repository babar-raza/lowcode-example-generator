"""Unit tests for fixture_registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.fixture_registry.registry import (
    FixtureEntry,
    FixtureRegistry,
    build_fixture_registry,
    load_fixture_registry,
    write_fixture_registry,
)
from plugin_examples.fixture_registry.fixture_fetcher import (
    check_fixture_availability,
    fetch_fixtures,
)


CELLS_SOURCES = [
    {
        "type": "github",
        "owner": "aspose-cells",
        "repo": "Aspose.Cells-for-.NET",
        "branch": "master",
        "paths": ["Examples/Data"],
    }
]


class TestFixtureRegistry:
    def test_build_from_config(self):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        assert registry.family == "cells"
        assert len(registry.fixtures) == 1

    def test_has_fixture(self):
        registry = FixtureRegistry(family="cells")
        registry.add_fixture(FixtureEntry(
            filename="test.xlsx",
            source_type="local",
            source_path="local:test.xlsx",
            provenance="local",
        ))
        assert registry.has_fixture("test.xlsx")
        assert not registry.has_fixture("missing.xlsx")

    def test_no_duplicates(self):
        registry = FixtureRegistry(family="cells")
        entry = FixtureEntry(
            filename="test.xlsx",
            source_type="local",
            source_path="local:test.xlsx",
            provenance="local",
        )
        registry.add_fixture(entry)
        registry.add_fixture(entry)
        assert len(registry.fixtures) == 1

    def test_provenance_preserved(self):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        assert registry.fixtures[0].provenance == "aspose-cells/Aspose.Cells-for-.NET:master"

    def test_write_and_load(self, tmp_path):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        manifests_dir = tmp_path / "workspace" / "manifests"
        path = write_fixture_registry(registry, manifests_dir)
        assert path.exists()
        assert path.name == "fixture-registry.json"

        loaded = load_fixture_registry(manifests_dir)
        assert loaded is not None
        assert loaded.family == "cells"
        assert len(loaded.fixtures) == len(registry.fixtures)

    def test_load_missing_returns_none(self, tmp_path):
        assert load_fixture_registry(tmp_path) is None

    def test_path_uses_workspace(self, tmp_path):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        path = write_fixture_registry(registry, tmp_path / "workspace" / "manifests")
        assert "workspace" in str(path)
        assert "manifests" in str(path)


class TestFixtureFetcher:
    def test_dry_run_mode(self):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        results = fetch_fixtures(registry, Path("/tmp/fixtures"), dry_run=True)
        assert len(results) > 0
        assert results[0]["status"] == "dry_run"

    def test_availability_check_found(self):
        registry = FixtureRegistry(family="cells")
        registry.add_fixture(FixtureEntry(
            filename="test.xlsx", source_type="local",
            source_path="local:test.xlsx", provenance="local",
        ))
        result = check_fixture_availability(registry, ["test.xlsx"])
        assert not result["blocked"]
        assert "test.xlsx" in result["available"]

    def test_availability_check_missing(self):
        registry = FixtureRegistry(family="cells")
        result = check_fixture_availability(registry, ["missing.xlsx"])
        assert result["blocked"]
        assert "missing.xlsx" in result["missing"]
