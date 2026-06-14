"""Regression test: EHV-01 must PASS (no silent bare except handlers)."""

from plugin_examples.fixture_factory.engineering_hygiene_validators import (
    check_silent_bare_excepts,
)


def test_ehv01_no_silent_bare_excepts():
    """Assert zero 'except Exception: pass' patterns exist in src/."""
    result = check_silent_bare_excepts()
    assert result.passed, f"EHV-01 regression: {result.message}\n{result.detail}"
