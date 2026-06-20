"""Tests for GitHub API rate-limit handling in github_pr_publisher (TC-SRHP-09)."""

from __future__ import annotations

import time
from email.message import Message
from unittest.mock import patch

import pytest

from plugin_examples.publisher.github_pr_publisher import _check_rate_limit

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _headers(**kwargs) -> Message:
    """Build an email.message.Message from kwargs (mimics http response headers)."""
    msg = Message()
    for k, v in kwargs.items():
        msg[k] = str(v)
    return msg


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_rate_limit_no_headers_is_noop() -> None:
    """None headers does not raise or sleep."""
    with patch("time.sleep") as mock_sleep:
        _check_rate_limit(None, "https://api.github.com/test")
    mock_sleep.assert_not_called()


def test_rate_limit_missing_header_is_noop() -> None:
    """Headers without X-RateLimit-Remaining does not sleep."""
    headers = _headers(**{"Content-Type": "application/json"})
    with patch("time.sleep") as mock_sleep:
        _check_rate_limit(headers, "https://api.github.com/test")
    mock_sleep.assert_not_called()


def test_rate_limit_high_remaining_no_warning(caplog) -> None:
    """Remaining well above threshold does not warn."""
    import logging

    headers = _headers(**{"X-RateLimit-Remaining": "4500", "X-RateLimit-Reset": "9999999999"})
    with patch("time.sleep"), caplog.at_level(logging.WARNING, logger="plugin_examples.publisher.github_pr_publisher"):
        _check_rate_limit(headers, "https://api.github.com/test")
    assert "rate_limit" not in caplog.text


def test_rate_limit_low_remaining_logs_warning(caplog) -> None:
    """Remaining below threshold logs a warning."""
    import logging

    headers = _headers(**{"X-RateLimit-Remaining": "50", "X-RateLimit-Reset": "9999999999"})
    with patch("time.sleep"), caplog.at_level(logging.WARNING, logger="plugin_examples.publisher.github_pr_publisher"):
        _check_rate_limit(headers, "https://api.github.com/test")
    assert "rate_limit" in caplog.text


def test_rate_limit_zero_remaining_sleeps() -> None:
    """Remaining == 0 causes a sleep until reset time."""
    future_reset = str(int(time.time()) + 30)
    headers = _headers(**{"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": future_reset})
    with patch("time.sleep") as mock_sleep:
        _check_rate_limit(headers, "https://api.github.com/test")
    mock_sleep.assert_called_once()
    # Sleep duration should be approximately 31s (30 + 1 buffer)
    sleep_arg = mock_sleep.call_args[0][0]
    assert sleep_arg >= 1, f"Expected sleep >= 1s, got {sleep_arg}"


def test_rate_limit_zero_remaining_no_reset_sleeps_60() -> None:
    """Remaining == 0 with unparseable reset defaults to 60s sleep."""
    headers = _headers(**{"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "not-a-number"})
    with patch("time.sleep") as mock_sleep:
        _check_rate_limit(headers, "https://api.github.com/test")
    mock_sleep.assert_called_once_with(60)


def test_rate_limit_invalid_remaining_is_noop() -> None:
    """Non-integer X-RateLimit-Remaining does not raise."""
    headers = _headers(**{"X-RateLimit-Remaining": "not-a-number"})
    with patch("time.sleep") as mock_sleep:
        _check_rate_limit(headers, "https://api.github.com/test")
    mock_sleep.assert_not_called()
