"""Unit tests for approved provider family enforcement in llm_router.

Verifies that _call_provider and _check_provider both reject unapproved
provider families, satisfying the policy guard in router.py.

AUTH-HARDEN-004 — plan Lane 1C requirement.
"""

from __future__ import annotations

import pytest


class TestApprovedProviderFamiliesConstant:
    """Verify _APPROVED_PROVIDER_FAMILIES contains expected entries."""

    def test_approved_families_constant_is_frozenset(self):
        """_APPROVED_PROVIDER_FAMILIES must be a frozenset (immutable policy)."""
        from plugin_examples.llm_router.router import _APPROVED_PROVIDER_FAMILIES
        assert isinstance(_APPROVED_PROVIDER_FAMILIES, frozenset)

    def test_approved_families_includes_professionalize(self):
        """llm_professionalize must be in approved families."""
        from plugin_examples.llm_router.router import _APPROVED_PROVIDER_FAMILIES
        assert "llm_professionalize" in _APPROVED_PROVIDER_FAMILIES

    def test_approved_families_non_empty(self):
        """Approved families set must not be empty."""
        from plugin_examples.llm_router.router import _APPROVED_PROVIDER_FAMILIES
        assert len(_APPROVED_PROVIDER_FAMILIES) >= 1


class TestCallProviderEnforcesApprovedFamily:
    """Verify _call_provider raises LLMProviderError for unapproved families."""

    def test_unapproved_provider_raises_llm_provider_error(self):
        """Calling _call_provider with an unapproved family raises LLMProviderError."""
        from plugin_examples.llm_router.router import _call_provider, LLMProviderError
        with pytest.raises(LLMProviderError) as exc_info:
            _call_provider("unapproved_vendor_xyz", "test prompt")
        assert "not approved by policy" in str(exc_info.value)
        assert "unapproved_vendor_xyz" in str(exc_info.value)

    def test_unapproved_provider_error_lists_approved_families(self):
        """Error message from unapproved provider lists the approved families."""
        from plugin_examples.llm_router.router import _call_provider, LLMProviderError
        with pytest.raises(LLMProviderError) as exc_info:
            _call_provider("openai_generic", "test prompt")
        # The error should hint at what IS approved
        assert "Approved" in str(exc_info.value)

    def test_approved_provider_does_not_raise_on_guard(self, monkeypatch):
        """Approved provider passes the guard check (may fail later on network)."""
        from plugin_examples.llm_router import router
        # Patch _call_ollama to avoid real network call
        monkeypatch.setattr(router, "_call_ollama", lambda *a, **kw: "mocked response")
        # Should not raise LLMProviderError at the guard stage
        result = router._call_provider("ollama", "test prompt")
        assert result == "mocked response"


class TestCheckProviderEnforcesApprovedFamily:
    """Verify _check_provider rejects unapproved families at preflight."""

    def test_unapproved_provider_preflight_returns_error(self):
        """_check_provider with unapproved family returns PreflightResult with error set."""
        from plugin_examples.llm_router.router import _check_provider
        result = _check_provider("unapproved_vendor_abc")
        assert result.passed is False
        assert result.error is not None
        assert "not approved by policy" in result.error

    def test_unapproved_provider_preflight_does_not_raise(self):
        """_check_provider must not raise — it returns a result object."""
        from plugin_examples.llm_router.router import _check_provider
        # Should return a result, not raise
        result = _check_provider("some_random_vendor")
        assert hasattr(result, "passed")
        assert hasattr(result, "error")
