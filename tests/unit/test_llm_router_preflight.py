"""Unit tests for LLM router preflight and routing logic."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from plugin_examples.llm_router.router import (
    LLMProviderError,
    LLMRouter,
    PreflightResult,
)


class TestPreflightResult:
    def test_passed_when_all_true(self):
        r = PreflightResult(
            provider="llm_professionalize",
            endpoint_reachable=True,
            model_available=True,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=True,
            latency_ms=100.0,
        )
        assert r.passed is True

    def test_fails_when_endpoint_unreachable(self):
        r = PreflightResult(
            provider="llm_professionalize",
            endpoint_reachable=False,
            model_available=True,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=True,
        )
        assert r.passed is False

    def test_fails_when_model_unavailable(self):
        r = PreflightResult(
            provider="ollama",
            endpoint_reachable=True,
            model_available=False,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=True,
        )
        assert r.passed is False

    def test_fails_when_json_unparseable(self):
        r = PreflightResult(
            provider="ollama",
            endpoint_reachable=True,
            model_available=True,
            json_response=False,
            structured_response_parseable=True,
            timeout_within_limit=True,
        )
        assert r.passed is False

    def test_fails_when_timeout_exceeded(self):
        r = PreflightResult(
            provider="llm_professionalize",
            endpoint_reachable=True,
            model_available=True,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=False,
        )
        assert r.passed is False

    def test_default_values(self):
        r = PreflightResult(provider="test")
        assert r.passed is False
        assert r.error is None
        assert r.latency_ms == 0.0


class TestLLMRouter:
    def test_get_provider_raises_when_none_selected(self):
        router = LLMRouter(provider_order=["llm_professionalize"])
        with pytest.raises(LLMProviderError, match="No LLM provider"):
            router.get_provider()

    def test_get_provider_returns_selected(self):
        router = LLMRouter(provider_order=["llm_professionalize"])
        router.selected_provider = "llm_professionalize"
        assert router.get_provider() == "llm_professionalize"

    def test_run_preflight_selects_first_passing(self):
        passing = PreflightResult(
            provider="llm_professionalize",
            endpoint_reachable=True,
            model_available=True,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=True,
            latency_ms=50.0,
        )

        with patch(
            "plugin_examples.llm_router.router._check_provider",
            return_value=passing,
        ):
            router = LLMRouter(provider_order=["llm_professionalize", "ollama"])
            results = router.run_preflight()
            assert router.selected_provider == "llm_professionalize"
            assert len(results) == 1  # stops after first pass

    def test_run_preflight_falls_through_on_failure(self):
        failing = PreflightResult(provider="llm_professionalize", endpoint_reachable=False)
        passing = PreflightResult(
            provider="ollama",
            endpoint_reachable=True,
            model_available=True,
            json_response=True,
            structured_response_parseable=True,
            timeout_within_limit=True,
            latency_ms=80.0,
        )

        def mock_check(provider, **kwargs):
            if provider == "llm_professionalize":
                return failing
            return passing

        with patch(
            "plugin_examples.llm_router.router._check_provider",
            side_effect=mock_check,
        ):
            router = LLMRouter(provider_order=["llm_professionalize", "ollama"])
            results = router.run_preflight()
            assert router.selected_provider == "ollama"
            assert len(results) == 2

    def test_run_preflight_no_provider_selected_when_all_fail(self):
        failing = PreflightResult(provider="test", endpoint_reachable=False)

        with patch(
            "plugin_examples.llm_router.router._check_provider",
            return_value=failing,
        ):
            router = LLMRouter(provider_order=["llm_professionalize", "ollama"])
            results = router.run_preflight()
            assert router.selected_provider is None
            assert len(results) == 2

    def test_empty_provider_order(self):
        router = LLMRouter(provider_order=[])
        results = router.run_preflight()
        assert results == []
        assert router.selected_provider is None

    def test_metrics_collector_attachment(self):
        collector = object()
        router = LLMRouter(provider_order=["llm_professionalize"], metrics_collector=collector)
        assert router.metrics_collector is collector

    def test_error_message_includes_tried_providers(self):
        router = LLMRouter(provider_order=["llm_professionalize", "ollama"])
        with pytest.raises(LLMProviderError) as exc_info:
            router.get_provider()
        assert "llm_professionalize" in str(exc_info.value)
        assert "ollama" in str(exc_info.value)
