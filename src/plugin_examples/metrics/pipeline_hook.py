"""Pipeline hook — called at pipeline end to finalize metrics."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def finalize_metrics(
    *,
    ctx: Any,
    config: Any,
    report: dict,
    command: str,
    dry_run: bool = True,
    post: bool = False,
    job_type_override: str | None = None,
    force_repost: bool = False,
    strict: bool = False,
    test_only_sprint: bool = True,
) -> dict:
    """Collect, validate, and optionally POST metrics at pipeline end.

    Returns a summary dict with keys: payload, validation, post_result.
    Never raises unless strict=True and an error occurs.
    """
    from plugin_examples.metrics.config import MetricsConfig
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
    evidence_dir = getattr(ctx, "evidence_dir", None)

    try:
        # Extract counts from report
        comp = report.get("comparison", {})
        meta = report.get("meta", {})
        verdict = report.get("verdict", "")
        plan = getattr(ctx, "planning", None)

        items_discovered = 0
        items_succeeded = 0
        items_failed = 0

        if command == "run":
            ready = getattr(plan, "ready_scenarios", []) if plan else []
            blocked = getattr(plan, "blocked_count", 0) if plan else 0
            items_discovered = len(ready) + blocked
            items_succeeded = sum(
                1 for v in (ctx.validation_results or []) if v.passed
            )
            items_failed = len(ctx.generated_projects) - items_succeeded
        else:
            # Simple 1/0 for non-run commands
            items_discovered = 1
            items_succeeded = 1 if not report.get("gate_summary", {}).get("hard_stopped") else 0
            items_failed = 1 - items_succeeded

        # Collector stats
        collector = getattr(ctx, "metrics_collector", None)
        token_usage = collector.token_usage if collector else 0
        api_calls_count = collector.api_calls_count if collector else 0
        run_duration_ms = meta.get("total_duration_ms", 0)

        # Write LLM call evidence
        ev_path = Path(evidence_dir) if evidence_dir else None
        if ev_path and collector and collector.calls:
            write_llm_calls_jsonl(ev_path, collector.calls)

        # Write run summary
        if ev_path:
            summary = {
                "run_id": getattr(ctx, "run_id", ""),
                "family": getattr(ctx, "family", ""),
                "command": command,
                "token_usage": token_usage,
                "api_calls_count": api_calls_count,
                "items_discovered": items_discovered,
                "items_succeeded": items_succeeded,
                "items_failed": items_failed,
                "verdict": verdict,
                "run_duration_ms": run_duration_ms,
            }
            write_run_summary(ev_path, summary)

        # Build payload
        test_mode = job_type_override == "Test"
        payload = build_payload(
            config,
            command=command,
            family=getattr(ctx, "family", ""),
            run_id=getattr(ctx, "run_id", ""),
            verdict=verdict,
            items_discovered=items_discovered,
            items_succeeded=items_succeeded,
            items_failed=items_failed,
            run_duration_ms=run_duration_ms,
            token_usage=token_usage,
            api_calls_count=api_calls_count,
            job_type_override=job_type_override,
            test_mode=test_mode,
        )
        result["payload"] = payload

        if ev_path:
            write_payload(ev_path, payload)

        # Validate
        validation = validate_payload(payload, config)
        result["validation"] = validation

        if ev_path:
            write_validation_result(ev_path, validation)

        if not validation["valid"]:
            logger.warning("Metrics payload validation failed: %s", validation["errors"])
            if strict:
                raise ValueError(f"Metrics validation failed: {validation['errors']}")

        # POST (or dry-run)
        repo_root = getattr(ctx, "repo_root", None)
        post_result = post_metrics(
            payload,
            config,
            dry_run=dry_run if not post else False,
            force_repost=force_repost,
            repo_root=repo_root,
            test_only_sprint=test_only_sprint,
        )
        result["post_result"] = post_result

        if ev_path:
            write_post_result(ev_path, post_result)

        if post_result.get("posted"):
            logger.info("Metrics posted successfully (run_id=%s)", payload.get("run_id"))
        else:
            logger.info("Metrics not posted: %s", post_result.get("reason", "unknown"))

    except Exception as exc:
        logger.error("Metrics finalization error: %s", exc)
        result["error"] = str(exc)
        if strict:
            raise

    return result
