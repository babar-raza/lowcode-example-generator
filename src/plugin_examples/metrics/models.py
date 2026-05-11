"""Metrics data models for accumulating LLM call records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LLMCallRecord:
    """Single LLM inference call record."""

    call_index: int
    timestamp: str
    stage: str
    provider: str
    model: str
    success: bool
    http_status: int | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    token_usage_available: bool
    duration_ms: float
    error_category: str | None = None


@dataclass
class MetricsCollector:
    """Accumulates per-call LLM metrics during a pipeline run.

    Instance-scoped — no global mutable state.
    """

    calls: list[LLMCallRecord] = field(default_factory=list)
    enabled: bool = True

    @property
    def token_usage(self) -> int:
        return sum(c.total_tokens for c in self.calls)

    @property
    def api_calls_count(self) -> int:
        return len(self.calls)

    def record_call(
        self,
        *,
        stage: str = "",
        provider: str = "",
        model: str = "",
        success: bool = True,
        http_status: int | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        token_usage_available: bool = False,
        duration_ms: float = 0.0,
        error_category: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        self.calls.append(
            LLMCallRecord(
                call_index=len(self.calls) + 1,
                timestamp=datetime.now(timezone.utc).isoformat(),
                stage=stage,
                provider=provider,
                model=model,
                success=success,
                http_status=http_status,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                token_usage_available=token_usage_available,
                duration_ms=duration_ms,
                error_category=error_category,
            )
        )
