"""Command-agnostic metrics session — any CLI command can use this."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Commands that have source-backed count formulas allowing external POST.
# All other commands can only write local evidence.
EXTERNAL_POST_COMMANDS: frozenset[str] = frozenset({"run"})

# Commands that are info-only and excluded from metrics entirely.
EXCLUDED_COMMANDS: frozenset[str] = frozenset({"status", "check"})


@dataclass
class MetricsSession:
    """Manages metrics lifecycle for a single CLI command invocation.

    Provides:
    - A MetricsCollector instance for LLM call tracking
    - Config loading and caching
    - Evidence directory management
    - Payload finalization with command-specific count policies
    - Safe no-op when metrics are disabled
    """

    command: str
    family: str = ""
    config: Any = None
    collector: Any = None
    dry_run: bool = True
    post: bool = False
    job_type_override: str | None = None
    force_repost: bool = False
    strict: bool = False
    evidence_dir: Path | None = None
    repo_root: Path | None = None
    run_id: str = ""
    _start_time: float = 0.0
    _active: bool = False

    def start(self) -> None:
        """Begin the metrics session."""
        if self.command in EXCLUDED_COMMANDS:
            return
        self._start_time = time.time()
        self._active = True

    @property
    def active(self) -> bool:
        return self._active

    @property
    def external_post_allowed(self) -> bool:
        """Whether this command has verified count formulas for external POST."""
        return self.command in EXTERNAL_POST_COMMANDS

    @property
    def count_source_policy(self) -> str:
        if self.command in EXCLUDED_COMMANDS:
            return "EXCLUDED_INFO_ONLY"
        if self.command in EXTERNAL_POST_COMMANDS:
            return "SUPPORTED_EXTERNAL_METRICS"
        return "LOCAL_ONLY_LLM_METRICS"

    def finalize(
        self,
        *,
        report: dict | None = None,
        items_discovered: int = 0,
        items_succeeded: int = 0,
        items_failed: int = 0,
        verdict: str = "",
        ctx: Any = None,
    ) -> dict:
        """Finalize the metrics session — write evidence, optionally POST.

        For non-run commands with unverified count formulas, writes local
        evidence but blocks external POST with a clear reason.
        """
        if not self._active:
            return {"metrics_enabled": False}

        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload
        from plugin_examples.metrics.evidence import (
            write_llm_calls_jsonl,
            write_run_summary,
            write_payload,
            write_validation_result,
            write_post_result,
        )
        from plugin_examples.metrics.poster import post_metrics

        result: dict[str, Any] = {"metrics_enabled": True}
        duration_ms = int((time.time() - self._start_time) * 1000)

        try:
            token_usage = self.collector.token_usage if self.collector else 0
            api_calls_count = self.collector.api_calls_count if self.collector else 0

            # Write LLM call evidence
            ev_path = self.evidence_dir
            if ev_path and self.collector and self.collector.calls:
                write_llm_calls_jsonl(ev_path, self.collector.calls)

            # Write run summary
            if ev_path:
                summary = {
                    "run_id": self.run_id,
                    "family": self.family,
                    "command": self.command,
                    "token_usage": token_usage,
                    "api_calls_count": api_calls_count,
                    "items_discovered": items_discovered,
                    "items_succeeded": items_succeeded,
                    "items_failed": items_failed,
                    "verdict": verdict,
                    "run_duration_ms": duration_ms,
                    "count_source_policy": self.count_source_policy,
                    "external_post_allowed": self.external_post_allowed,
                }
                write_run_summary(ev_path, summary)

            # Build payload
            test_mode = self.job_type_override == "Test"
            payload = build_payload(
                self.config,
                command=self.command,
                family=self.family,
                run_id=self.run_id,
                verdict=verdict,
                items_discovered=items_discovered,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                run_duration_ms=duration_ms,
                token_usage=token_usage,
                api_calls_count=api_calls_count,
                job_type_override=self.job_type_override,
                test_mode=test_mode,
            )
            result["payload"] = payload

            if ev_path:
                write_payload(ev_path, payload)

            # Validate
            validation = validate_payload(payload, self.config)
            result["validation"] = validation

            if ev_path:
                write_validation_result(ev_path, validation)

            if not validation["valid"]:
                logger.warning("Metrics payload validation failed: %s", validation["errors"])
                if self.strict:
                    raise ValueError(f"Metrics validation failed: {validation['errors']}")

            # Determine if external POST is allowed
            effective_post = self.post
            post_blocked_reason = None

            if not self.external_post_allowed and not test_mode:
                effective_post = False
                post_blocked_reason = f"count_source_unverified_for_{self.command}"

            if effective_post:
                post_result = post_metrics(
                    payload,
                    self.config,
                    dry_run=False,
                    force_repost=self.force_repost,
                    repo_root=self.repo_root,
                    test_only_sprint=True,
                )
            elif post_blocked_reason:
                post_result = {
                    "posted": False,
                    "reason": post_blocked_reason,
                    "dry_run": self.dry_run,
                    "count_source_policy": self.count_source_policy,
                }
            else:
                post_result = post_metrics(
                    payload,
                    self.config,
                    dry_run=True,
                    repo_root=self.repo_root,
                    test_only_sprint=True,
                )

            result["post_result"] = post_result

            if ev_path:
                write_post_result(ev_path, post_result)

        except Exception as exc:
            logger.error("Metrics session finalization error: %s", exc)
            result["error"] = str(exc)
            if self.strict:
                raise

        return result
