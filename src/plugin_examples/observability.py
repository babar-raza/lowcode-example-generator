"""
Structured logging and observability for the plugin examples pipeline.

Provides a JSON-structured logging wrapper so that log records emitted
during pipeline execution carry consistent machine-readable fields.
Downstream tools (log aggregators, dashboards, CI parsers) can reliably
ingest and filter on these fields.

Fields emitted on every log record:
  timestamp   — ISO-8601 UTC
  level       — DEBUG | INFO | WARNING | ERROR | CRITICAL
  logger      — dotted module name
  run_id      — pipeline run identifier (set per-run via bind())
  stage       — current pipeline stage name (set via bind())
  family      — family being processed (set via bind())
  message     — human-readable log message
  extra       — any additional keyword arguments passed to log calls

Usage:
    from plugin_examples.observability import get_logger, configure_logging

    configure_logging()          # call once at process startup
    log = get_logger(__name__)
    log.info("stage_start", stage="nuget_fetch", family="cells")
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Context holder — per-run metadata attached to every log record
# ---------------------------------------------------------------------------

class _LogContext:
    """Thread-local-style log context bound to the current pipeline run."""

    def __init__(self) -> None:
        self._run_id: str = ""
        self._stage: str = ""
        self._family: str = ""

    def bind(self, *, run_id: str = "", stage: str = "", family: str = "") -> None:
        """Update the current pipeline context fields."""
        if run_id:
            self._run_id = run_id
        if stage:
            self._stage = stage
        if family:
            self._family = family

    def clear(self) -> None:
        self._run_id = ""
        self._stage = ""
        self._family = ""

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def stage(self) -> str:
        return self._stage

    @property
    def family(self) -> str:
        return self._family


_context = _LogContext()


def bind_context(*, run_id: str = "", stage: str = "", family: str = "") -> None:
    """Bind pipeline context fields to all subsequent log records."""
    _context.bind(run_id=run_id, stage=stage, family=family)


def clear_context() -> None:
    """Clear all pipeline context fields (e.g., between runs)."""
    _context.clear()


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------

class _JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "run_id": _context.run_id,
            "stage": _context.stage,
            "family": _context.family,
            "message": record.getMessage(),
        }

        # Attach any extra fields passed via the `extra` dict
        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_ATTRS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# Standard LogRecord attributes that we do NOT re-emit as extras
_STANDARD_LOG_RECORD_ATTRS = frozenset({
    "args", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "message", "module", "msecs",
    "msg", "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "taskName", "thread", "threadName",
})


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_configured = False


def configure_logging(
    level: int | str | None = None,
    *,
    force_json: bool = False,
) -> None:
    """Configure the root logger for the pipeline.

    Call this once at process startup (e.g., in ``__main__`` or the CLI
    entry point) before any loggers are used.

    Args:
        level: Log level (default: INFO, or DEBUG if LOG_LEVEL env var set).
        force_json: If True, always use JSON format even in a TTY.
    """
    global _configured

    if level is None:
        env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    use_json = (
        force_json
        or os.environ.get("PLUGIN_EXAMPLES_LOG_FORMAT", "").lower() == "json"
        or not sys.stderr.isatty()
    )

    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicate output when called multiple times
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stderr)
    if use_json:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
            datefmt="%H:%M:%S",
        ))

    root.addHandler(handler)
    _configured = True


# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """Return a standard Logger for the given module name.

    The returned logger emits JSON-structured records when the pipeline is
    running in non-interactive mode or when ``PLUGIN_EXAMPLES_LOG_FORMAT=json``.

    Usage:
        log = get_logger(__name__)
        log.info("nuget_fetch_start", extra={"package": "Aspose.Cells"})
    """
    return logging.getLogger(name)
