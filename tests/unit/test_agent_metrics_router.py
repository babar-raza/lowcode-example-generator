"""Tests for metrics instrumentation in LLM router."""

from unittest.mock import MagicMock, patch

import pytest


class TestOpenAICompatibleMetrics:
    def test_usage_captured(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_openai_compatible

        mc = MetricsCollector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            result = _call_openai_compatible(
                "http://fake/chat/completions",
                "test prompt",
                metrics_collector=mc,
                metrics_provider="llm_professionalize",
                metrics_model="recommended",
            )

        assert result == "hello"
        assert mc.api_calls_count == 1
        assert mc.token_usage == 15
        assert mc.calls[0].token_usage_available is True
        assert mc.calls[0].prompt_tokens == 10
        assert mc.calls[0].completion_tokens == 5

    def test_missing_usage_handled(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_openai_compatible

        mc = MetricsCollector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "hi"}}],
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            result = _call_openai_compatible(
                "http://fake/v1",
                "p",
                metrics_collector=mc,
                metrics_provider="test",
            )

        assert result == "hi"
        assert mc.api_calls_count == 1
        assert mc.token_usage == 0
        assert mc.calls[0].token_usage_available is False

    def test_failed_request_counted_after_send(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_openai_compatible

        mc = MetricsCollector()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = Exception("Server error")

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            with pytest.raises(Exception, match="Server error"):
                _call_openai_compatible(
                    "http://fake/v1",
                    "p",
                    metrics_collector=mc,
                    metrics_provider="test",
                )

        assert mc.api_calls_count == 1
        assert mc.calls[0].success is False
        assert mc.calls[0].http_status == 500

    def test_no_collector_still_works(self):
        from plugin_examples.llm_router.router import _call_openai_compatible

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "ok"}}],
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            result = _call_openai_compatible("http://fake/v1", "p")

        assert result == "ok"

    def test_generate_returns_str(self):
        from plugin_examples.llm_router.router import LLMRouter
        from plugin_examples.metrics.models import MetricsCollector

        mc = MetricsCollector()
        router = LLMRouter(
            provider_order=["llm_professionalize"],
            selected_provider="llm_professionalize",
            metrics_collector=mc,
        )

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "generated"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            with patch("plugin_examples.llm_router.router._resolve_api_key", return_value="fake"):
                result = router.generate("test prompt")

        assert isinstance(result, str)
        assert result == "generated"
        assert mc.api_calls_count == 1
        assert mc.token_usage == 8


class TestOllamaMetrics:
    def test_ollama_usage_captured(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_ollama

        mc = MetricsCollector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "response": "ollama says hi",
            "eval_count": 20,
            "prompt_eval_count": 10,
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            result = _call_ollama("p", metrics_collector=mc)

        assert result == "ollama says hi"
        assert mc.api_calls_count == 1
        assert mc.token_usage == 30
        assert mc.calls[0].token_usage_available is True

    def test_ollama_missing_eval_count(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_ollama

        mc = MetricsCollector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "ok"}

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            result = _call_ollama("p", metrics_collector=mc)

        assert result == "ok"
        assert mc.token_usage == 0
        assert mc.calls[0].token_usage_available is False


class TestPreflightNotCounted:
    def test_preflight_get_not_counted(self):
        """Preflight uses GET to /models — must not be counted as LLM call."""
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import LLMRouter

        mc = MetricsCollector()
        router = LLMRouter(
            provider_order=["llm_professionalize"],
            metrics_collector=mc,
        )

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"data": [{"id": "recommended"}]}

        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "choices": [{"message": {"content": "test response"}}],
        }

        with patch("plugin_examples.llm_router.router.requests.get", return_value=mock_get_resp):
            with patch("plugin_examples.llm_router.router._resolve_api_key", return_value="fake"):
                router.run_preflight()

        # Preflight should NOT add any calls
        assert mc.api_calls_count == 0


class TestCollectorIsolation:
    def test_two_routers_independent_collectors(self):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import _call_openai_compatible

        mc1 = MetricsCollector()
        mc2 = MetricsCollector()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "x"}}],
            "usage": {"total_tokens": 10},
        }

        with patch("plugin_examples.llm_router.router.requests.post", return_value=mock_resp):
            _call_openai_compatible("http://f", "p", metrics_collector=mc1, metrics_provider="a")
            _call_openai_compatible("http://f", "p", metrics_collector=mc2, metrics_provider="b")
            _call_openai_compatible("http://f", "p", metrics_collector=mc2, metrics_provider="b")

        assert mc1.api_calls_count == 1
        assert mc2.api_calls_count == 2
