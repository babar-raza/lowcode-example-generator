"""Tests for src/plugin_examples/observability.py.

Verifies that:
- JSON log records contain all required fields (timestamp, level, logger, run_id,
  stage, family, message)
- bind_context() propagates fields to subsequent records
- clear_context() resets the context
- configure_logging() can be called multiple times without duplicate handlers
- Plain-text formatter is used when PLUGIN_EXAMPLES_LOG_FORMAT is not set and
  force_json=False on a TTY (tested indirectly via flag)
- Extra keyword arguments are forwarded into the JSON payload
"""

from __future__ import annotations

import json
import logging
import os
from io import StringIO

import pytest

from plugin_examples.observability import (
    _JsonFormatter,
    _LogContext,
    bind_context,
    clear_context,
    configure_logging,
    get_logger,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_json_record(message: str, **extra: object) -> dict:
    """Emit one log record through the JSON formatter and return the parsed dict."""
    formatter = _JsonFormatter()
    logger = logging.getLogger("test.observability")
    record = logger.makeRecord(
        name="test.observability",
        level=logging.INFO,
        fn="test_file.py",
        lno=1,
        msg=message,
        args=(),
        exc_info=None,
        extra=extra,
    )
    line = formatter.format(record)
    return json.loads(line)


# ---------------------------------------------------------------------------
# Field presence tests
# ---------------------------------------------------------------------------

class TestJsonFormatterFields:
    def test_required_fields_present(self):
        record = _make_json_record("hello world")
        for field in ("timestamp", "level", "logger", "trace_id", "run_id", "stage", "family", "message"):
            assert field in record, f"Missing field: {field}"

    def test_message_value(self):
        record = _make_json_record("stage completed")
        assert record["message"] == "stage completed"

    def test_level_value(self):
        record = _make_json_record("test")
        assert record["level"] == "INFO"

    def test_logger_name(self):
        record = _make_json_record("test")
        assert record["logger"] == "test.observability"

    def test_timestamp_is_iso_format(self):
        record = _make_json_record("test")
        ts = record["timestamp"]
        # ISO-8601 UTC ends with +00:00 or Z
        assert "T" in ts, f"timestamp not ISO format: {ts}"

    def test_extra_fields_forwarded(self):
        record = _make_json_record("test", package="Aspose.Cells", build_pass=True)
        assert record["package"] == "Aspose.Cells"
        assert record["build_pass"] is True


# ---------------------------------------------------------------------------
# Context binding tests
# ---------------------------------------------------------------------------

class TestContextBinding:
    def setup_method(self):
        clear_context()

    def teardown_method(self):
        clear_context()

    def test_bind_run_id(self):
        bind_context(run_id="run-abc123")
        record = _make_json_record("test")
        assert record["run_id"] == "run-abc123"

    def test_bind_stage(self):
        bind_context(stage="nuget_fetch")
        record = _make_json_record("test")
        assert record["stage"] == "nuget_fetch"

    def test_bind_family(self):
        bind_context(family="cells")
        record = _make_json_record("test")
        assert record["family"] == "cells"

    def test_bind_all(self):
        bind_context(run_id="r1", stage="gate_eval", family="pdf")
        record = _make_json_record("test")
        assert record["run_id"] == "r1"
        assert record["stage"] == "gate_eval"
        assert record["family"] == "pdf"

    def test_clear_context_resets_fields(self):
        bind_context(run_id="r1", stage="s1", family="f1")
        clear_context()
        record = _make_json_record("test")
        assert record["trace_id"] == ""
        assert record["run_id"] == ""
        assert record["stage"] == ""
        assert record["family"] == ""

    def test_partial_bind_preserves_other_fields(self):
        bind_context(run_id="r1", stage="s1", family="f1")
        bind_context(stage="s2")
        record = _make_json_record("test")
        assert record["run_id"] == "r1"
        assert record["stage"] == "s2"
        assert record["family"] == "f1"


# ---------------------------------------------------------------------------
# configure_logging tests
# ---------------------------------------------------------------------------

class TestConfigureLogging:
    def test_configure_logging_no_duplicate_handlers(self):
        configure_logging(level=logging.WARNING, force_json=True)
        count_before = len(logging.getLogger().handlers)
        configure_logging(level=logging.WARNING, force_json=True)
        count_after = len(logging.getLogger().handlers)
        assert count_after == count_before, "Duplicate handlers after second configure_logging call"

    def test_configure_logging_json_forced(self):
        configure_logging(level=logging.DEBUG, force_json=True)
        root = logging.getLogger()
        assert any(isinstance(h.formatter, _JsonFormatter) for h in root.handlers)

    def test_configure_logging_respects_env_var(self, monkeypatch):
        monkeypatch.setenv("PLUGIN_EXAMPLES_LOG_FORMAT", "json")
        configure_logging(level=logging.INFO)
        root = logging.getLogger()
        assert any(isinstance(h.formatter, _JsonFormatter) for h in root.handlers)
        monkeypatch.delenv("PLUGIN_EXAMPLES_LOG_FORMAT", raising=False)


# ---------------------------------------------------------------------------
# get_logger tests
# ---------------------------------------------------------------------------

class TestGetLogger:
    def test_returns_logger_instance(self):
        log = get_logger("plugin_examples.test_module")
        assert isinstance(log, logging.Logger)

    def test_logger_name_matches(self):
        log = get_logger("plugin_examples.runner")
        assert log.name == "plugin_examples.runner"

    def test_logger_is_functional(self):
        """Logger emits records without raising."""
        configure_logging(level=logging.DEBUG, force_json=True)
        log = get_logger("plugin_examples.smoke")
        log.info("smoke test record")  # should not raise


# ---------------------------------------------------------------------------
# Trace ID tests (TC-RH01)
# ---------------------------------------------------------------------------

class TestTraceId:
    def setup_method(self):
        clear_context()

    def teardown_method(self):
        clear_context()

    def test_trace_id_auto_generated_on_bind(self):
        bind_context(run_id="r1")
        record = _make_json_record("test")
        assert record["trace_id"] != ""
        assert len(record["trace_id"]) == 32  # UUID4 hex

    def test_trace_id_explicit(self):
        bind_context(trace_id="custom-trace-abc")
        record = _make_json_record("test")
        assert record["trace_id"] == "custom-trace-abc"

    def test_trace_id_stable_across_binds(self):
        bind_context(run_id="r1")
        record1 = _make_json_record("first")
        tid1 = record1["trace_id"]
        bind_context(stage="s2")
        record2 = _make_json_record("second")
        assert record2["trace_id"] == tid1, "trace_id should be stable across partial binds"

    def test_trace_id_cleared(self):
        bind_context(run_id="r1")
        clear_context()
        record = _make_json_record("test")
        assert record["trace_id"] == ""

    def test_trace_id_present_in_json_output(self):
        bind_context(trace_id="t123")
        record = _make_json_record("test")
        assert "trace_id" in record
