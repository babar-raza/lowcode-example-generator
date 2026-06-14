"""Integration tests for structured logging observability."""

import io
import json
import logging

from plugin_examples.observability import bind_context, clear_context, configure_logging, get_logger


def test_json_logging_produces_valid_json(capfd):
    """When force_json=True, log output must be valid JSON with required fields."""
    # Reset logging state
    root = logging.getLogger()
    root.handlers.clear()

    configure_logging(level=logging.DEBUG, force_json=True)
    log = get_logger("test.integration.observability")
    bind_context(run_id="test-run-123", stage="verification", family="pdf")

    log.info("test_message_for_integration")

    # Read stderr output
    captured = capfd.readouterr()
    lines = [l for l in captured.err.strip().splitlines() if l.strip()]
    assert len(lines) >= 1, "Expected at least one log line in stderr"

    record = json.loads(lines[-1])
    assert record["level"] == "INFO"
    assert record["message"] == "test_message_for_integration"
    assert record["run_id"] == "test-run-123"
    assert record["stage"] == "verification"
    assert record["family"] == "pdf"
    assert "timestamp" in record

    clear_context()


def test_bind_context_updates_subsequent_records(capfd):
    """bind_context changes should appear in subsequent log records."""
    root = logging.getLogger()
    root.handlers.clear()

    configure_logging(level=logging.DEBUG, force_json=True)
    log = get_logger("test.integration.context")

    bind_context(stage="stage_a")
    log.info("msg_a")

    bind_context(stage="stage_b")
    log.info("msg_b")

    captured = capfd.readouterr()
    lines = [l for l in captured.err.strip().splitlines() if l.strip()]
    assert len(lines) >= 2

    rec_a = json.loads(lines[-2])
    rec_b = json.loads(lines[-1])
    assert rec_a["stage"] == "stage_a"
    assert rec_b["stage"] == "stage_b"

    clear_context()
