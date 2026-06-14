"""Tests for EHV-08 (dependency license policy)."""

from plugin_examples.fixture_factory.engineering_hygiene_validators import (
    check_dependency_licenses,
)


def test_ehv08_passes_with_current_project():
    """EHV-08 should pass — all declared dependencies must have approved licenses."""
    result = check_dependency_licenses()
    assert result.passed, f"EHV-08 failed: {result.message}\n{result.detail}"


def test_ehv08_skip_when_no_pyproject(tmp_path):
    """EHV-08 should fail gracefully when pyproject.toml is missing."""
    result = check_dependency_licenses(tmp_path)
    assert not result.passed
    assert "pyproject.toml" in result.message


def test_ehv08_skip_when_no_deps(tmp_path):
    """EHV-08 should skip when no dependencies section exists."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    result = check_dependency_licenses(tmp_path)
    assert result.passed
    assert "SKIP" in result.message
