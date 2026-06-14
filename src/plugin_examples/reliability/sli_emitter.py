"""Service Level Indicator (SLI) emission via structured logging.

Emits machine-readable SLI events that downstream tools (log aggregators,
SLO monitors, dashboards) can filter on. Each SLI event is a JSON log
record with ``sli_`` prefixed fields.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SLIEvent:
    """A single SLI measurement."""

    metric_name: str
    value: float
    timestamp: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


def emit_sli(metric_name: str, value: float, **labels: str) -> SLIEvent:
    """Emit an SLI event via structured logging and return it."""
    event = SLIEvent(metric_name=metric_name, value=value, labels=labels)
    logger.info(
        "sli_event",
        extra={
            "sli_metric": metric_name,
            "sli_value": value,
            "sli_labels": labels,
        },
    )
    return event


def emit_handler_sli(
    handler_id: str, duration_ms: int, success: bool
) -> SLIEvent:
    """Emit per-handler execution SLI (duration + success)."""
    event = SLIEvent(
        metric_name="handler_execution",
        value=duration_ms,
        labels={
            "handler_id": handler_id,
            "success": str(success).lower(),
        },
    )
    logger.info(
        "handler_sli",
        extra={
            "sli_metric": "handler_execution",
            "sli_handler_id": handler_id,
            "sli_duration_ms": duration_ms,
            "sli_success": success,
        },
    )
    return event


def compute_slis_from_loop_metrics(metrics: Any) -> list[SLIEvent]:
    """Derive SLI values from a completed loop's LoopMetrics.

    Args:
        metrics: A LoopMetrics instance (or any object with matching attrs).

    Returns:
        List of SLI events for the completed loop.
    """
    events: list[SLIEvent] = []
    total_executed = getattr(metrics, "actions_executed", 0)
    total_errors = getattr(metrics, "handler_errors", 0)
    total_duration = getattr(metrics, "total_duration_ms", 0)
    total_cycles = getattr(metrics, "total_cycles", 0)

    # Handler error rate
    total_attempts = total_executed + total_errors
    error_rate = total_errors / total_attempts if total_attempts > 0 else 0.0
    events.append(emit_sli("handler_error_rate", error_rate))

    # Average cycle duration
    avg_duration = total_duration / total_cycles if total_cycles > 0 else 0.0
    events.append(emit_sli("avg_cycle_duration_ms", avg_duration))

    # Actions per cycle
    actions_per_cycle = total_executed / total_cycles if total_cycles > 0 else 0.0
    events.append(emit_sli("actions_per_cycle", actions_per_cycle))

    return events


class HandlerTimer:
    """Context manager that times handler execution and emits SLI."""

    def __init__(self, handler_id: str) -> None:
        self.handler_id = handler_id
        self._start: float = 0
        self.duration_ms: int = 0
        self.success: bool = True
        self.sli_event: SLIEvent | None = None

    def __enter__(self) -> HandlerTimer:
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        self.duration_ms = int((time.monotonic() - self._start) * 1000)
        if exc_type is not None:
            self.success = False
        self.sli_event = emit_handler_sli(self.handler_id, self.duration_ms, self.success)
