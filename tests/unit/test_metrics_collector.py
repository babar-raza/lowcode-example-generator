"""Unit tests for the MetricsCollector and MetricsSession."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin_examples.metrics.models import LLMCallRecord, MetricsCollector
from plugin_examples.metrics.session import (
    EXCLUDED_COMMANDS,
    EXTERNAL_POST_COMMANDS,
    MetricsSession,
)


class TestLLMCallRecord:
    def test_record_fields(self):
        r = LLMCallRecord(
            call_index=1,
            timestamp="2026-05-19T08:00:00Z",
            stage="generation",
            provider="llm_professionalize",
            model="gpt-4o",
            success=True,
            http_status=200,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            token_usage_available=True,
            duration_ms=1200.0,
        )
        assert r.call_index == 1
        assert r.provider == "llm_professionalize"
        assert r.total_tokens == 150
        assert r.error_category is None

    def test_error_category_default(self):
        r = LLMCallRecord(
            call_index=1, timestamp="", stage="", provider="", model="",
            success=False, http_status=500, prompt_tokens=0, completion_tokens=0,
            total_tokens=0, token_usage_available=False, duration_ms=0.0,
            error_category="timeout",
        )
        assert r.error_category == "timeout"


class TestMetricsCollector:
    def test_empty_collector(self):
        c = MetricsCollector()
        assert c.api_calls_count == 0
        assert c.token_usage == 0

    def test_record_call(self):
        c = MetricsCollector()
        c.record_call(
            stage="generation",
            provider="llm_professionalize",
            model="gpt-4o",
            success=True,
            http_status=200,
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            token_usage_available=True,
            duration_ms=1200.0,
        )
        assert c.api_calls_count == 1
        assert c.token_usage == 150

    def test_multiple_calls_accumulate(self):
        c = MetricsCollector()
        for i in range(3):
            c.record_call(total_tokens=100, stage=f"stage_{i}")
        assert c.api_calls_count == 3
        assert c.token_usage == 300

    def test_call_index_increments(self):
        c = MetricsCollector()
        c.record_call(stage="a")
        c.record_call(stage="b")
        assert c.calls[0].call_index == 1
        assert c.calls[1].call_index == 2

    def test_disabled_collector_ignores_calls(self):
        c = MetricsCollector(enabled=False)
        c.record_call(stage="test", total_tokens=100)
        assert c.api_calls_count == 0
        assert c.token_usage == 0

    def test_timestamp_is_set(self):
        c = MetricsCollector()
        c.record_call(stage="test")
        assert c.calls[0].timestamp  # non-empty


class TestMetricsSession:
    def test_session_starts(self):
        s = MetricsSession(command="run", family="cells")
        s.start()
        assert s.active is True

    def test_excluded_command_does_not_activate(self):
        for cmd in EXCLUDED_COMMANDS:
            s = MetricsSession(command=cmd)
            s.start()
            assert s.active is False

    def test_external_post_allowed_for_run(self):
        s = MetricsSession(command="run")
        assert s.external_post_allowed is True

    def test_external_post_denied_for_other_commands(self):
        s = MetricsSession(command="publish-pr")
        assert s.external_post_allowed is False

    def test_count_source_policy_for_run(self):
        s = MetricsSession(command="run")
        assert s.count_source_policy == "SUPPORTED_EXTERNAL_METRICS"

    def test_count_source_policy_for_excluded(self):
        s = MetricsSession(command="status")
        assert s.count_source_policy == "EXCLUDED_INFO_ONLY"

    def test_count_source_policy_local_only(self):
        s = MetricsSession(command="publish-pr")
        assert s.count_source_policy == "LOCAL_ONLY_LLM_METRICS"

    def test_default_not_active(self):
        s = MetricsSession(command="run")
        assert s.active is False

    def test_dry_run_default_true(self):
        s = MetricsSession(command="run")
        assert s.dry_run is True
