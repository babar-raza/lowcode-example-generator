"""LLM decision audit log — records every LLM routing decision as a structured artifact.

Each call to the LLM router is logged as a JSON Lines record in a per-run audit file.
This provides an auditable trail of model selection, token usage, latency, and outcomes
that satisfies the R5 (Auditable) dimension of enterprise readiness.

Audit records are written to .local/decision-audit-<run_id>.jsonl (one record per line).
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Global audit log instance — set by the pipeline runner at startup.
_global_audit_log: DecisionAuditLog | None = None
_lock = threading.Lock()


@dataclass
class DecisionAuditRecord:
    """Single LLM routing decision record."""

    timestamp: str
    run_id: str
    provider: str
    model: str
    prompt_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    outcome: str  # "success" | "error" | "circuit_breaker_tripped"
    error_message: str | None = None
    stage: str = ""
    extra: dict = field(default_factory=dict)


class DecisionAuditLog:
    """Thread-safe append-only audit log for LLM routing decisions.

    Records are written as JSON Lines (one record per line) to the given path.
    The file is created on first write. Each record is flushed immediately so
    partial runs produce recoverable audit logs.
    """

    def __init__(self, path: Path, run_id: str = "") -> None:
        self._path = Path(path)
        self._run_id = run_id
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def record(
        self,
        *,
        provider: str,
        model: str,
        prompt_name: str = "",
        stage: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        latency_ms: float = 0.0,
        outcome: str = "success",
        error_message: str | None = None,
        extra: dict | None = None,
    ) -> DecisionAuditRecord:
        """Append one audit record to the log file and return it."""
        rec = DecisionAuditRecord(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            run_id=self._run_id,
            provider=provider,
            model=model,
            prompt_name=prompt_name,
            stage=stage,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            outcome=outcome,
            error_message=error_message,
            extra=extra or {},
        )
        with self._lock:
            try:
                with open(self._path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(asdict(rec)) + "\n")
                    fh.flush()
            except OSError as exc:
                logger.warning("Could not write decision audit record: %s", exc)
        return rec

    def read_all(self) -> list[DecisionAuditRecord]:
        """Read all records from the audit log file."""
        if not self._path.exists():
            return []
        records = []
        with self._lock:
            try:
                for line in self._path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        records.append(DecisionAuditRecord(**data))
                    except (json.JSONDecodeError, TypeError, ValueError) as exc:
                        logger.debug("Skipping malformed audit record: %s", exc)
            except OSError as exc:
                logger.warning("Could not read decision audit log %s: %s", self._path, exc)
        return records

    def summary(self) -> dict:
        """Return a summary dict suitable for evidence reporting."""
        records = self.read_all()
        total = len(records)
        successes = sum(1 for r in records if r.outcome == "success")
        errors = sum(1 for r in records if r.outcome == "error")
        total_tokens = sum(r.total_tokens for r in records)
        avg_latency = (sum(r.latency_ms for r in records) / total) if total else 0.0
        providers = sorted({r.provider for r in records})
        models = sorted({r.model for r in records})
        return {
            "total_calls": total,
            "successful_calls": successes,
            "error_calls": errors,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 1),
            "providers_used": providers,
            "models_used": models,
            "audit_log_path": str(self._path),
        }


def init_global_audit_log(path: Path, run_id: str = "") -> DecisionAuditLog:
    """Initialize the module-level global audit log (call once at pipeline startup)."""
    global _global_audit_log
    with _lock:
        _global_audit_log = DecisionAuditLog(path=path, run_id=run_id)
        logger.info("Decision audit log initialized: %s", path)
    return _global_audit_log


def get_global_audit_log() -> DecisionAuditLog | None:
    """Return the global audit log, or None if not initialized."""
    return _global_audit_log


def record_decision(
    *,
    provider: str,
    model: str,
    prompt_name: str = "",
    stage: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    latency_ms: float = 0.0,
    outcome: str = "success",
    error_message: str | None = None,
    extra: dict | None = None,
) -> None:
    """Record a decision to the global audit log if initialized; silently skip otherwise."""
    log = _global_audit_log
    if log is None:
        return
    log.record(
        provider=provider,
        model=model,
        prompt_name=prompt_name,
        stage=stage,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        outcome=outcome,
        error_message=error_message,
        extra=extra or {},
    )
