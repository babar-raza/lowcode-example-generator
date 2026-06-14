"""Tests for EHV-06 (version/changelog sync) and EHV-07 (semver format)."""

import textwrap
from pathlib import Path

from plugin_examples.fixture_factory.engineering_hygiene_validators import (
    check_semver_version,
    check_version_changelog_sync,
)


def test_ehv06_passes_with_current_project():
    """EHV-06 should pass against the actual project root."""
    result = check_version_changelog_sync()
    assert result.passed, f"EHV-06 failed on real project: {result.message}"


def test_ehv07_passes_with_current_project():
    """EHV-07 should pass against the actual project root."""
    result = check_semver_version()
    assert result.passed, f"EHV-07 failed on real project: {result.message}"


def test_ehv06_fails_on_mismatch(tmp_path):
    """EHV-06 should fail when versions don't match."""
    (tmp_path / "pyproject.toml").write_text('version = "1.2.3"\n')
    (tmp_path / "CHANGELOG.md").write_text("## [1.0.0] - 2026-01-01\n")
    result = check_version_changelog_sync(tmp_path)
    assert not result.passed
    assert "mismatch" in result.message.lower()


def test_ehv06_passes_on_match(tmp_path):
    """EHV-06 should pass when versions match."""
    (tmp_path / "pyproject.toml").write_text('version = "2.0.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [2.0.0] - 2026-06-13\n")
    result = check_version_changelog_sync(tmp_path)
    assert result.passed


def test_ehv07_fails_on_non_semver(tmp_path):
    """EHV-07 should fail on non-semver version."""
    (tmp_path / "pyproject.toml").write_text('version = "1.2"\n')
    result = check_semver_version(tmp_path)
    assert not result.passed
    assert "semver" in result.message.lower()


def test_ehv07_passes_on_valid_semver(tmp_path):
    """EHV-07 should pass on valid semver."""
    (tmp_path / "pyproject.toml").write_text('version = "1.2.3"\n')
    result = check_semver_version(tmp_path)
    assert result.passed
