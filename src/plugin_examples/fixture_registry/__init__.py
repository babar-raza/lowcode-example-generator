"""Fixture registry — track test data provenance and availability."""

from plugin_examples.fixture_registry.registry import (
    FixtureRegistry,
    load_fixture_registry,
    write_fixture_registry,
)

__all__ = ["FixtureRegistry", "load_fixture_registry", "write_fixture_registry"]
