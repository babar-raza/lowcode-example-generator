"""Build and validate metrics payloads from config and run context."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_payload(
    config: Any,
    *,
    command: str = "run",
    family: str = "",
    run_id: str = "",
    verdict: str = "",
    items_discovered: int = 0,
    items_succeeded: int = 0,
    items_failed: int = 0,
    run_duration_ms: int = 0,
    token_usage: int = 0,
    api_calls_count: int = 0,
    job_type_override: str = "",
    test_mode: bool = False,
) -> dict:
    """Build a metrics payload dict from config and runtime values.

    All values come from config or explicit parameters — nothing hardcoded.
    """
    # Derive job_type
    if job_type_override:
        job_type = job_type_override
    else:
        job_type = config.command_to_job_type.get(command, "")

    # Derive agent_name — stable identity, not command-specific
    agent_name = config.agent_name
    if test_mode:
        agent_name = f"{config.agent_name_test_prefix}{agent_name}"

    # Derive product
    product = config.family_to_product.get(family, "")

    # Derive status from verdict
    if verdict:
        status, _ = config.resolve_status(verdict)
    else:
        status = "success"

    # Derive item_name
    item_name = config.command_to_item_name.get(command, "")
    if test_mode and item_name:
        item_name = f"test-{item_name}"

    # Build run_id for test mode
    effective_run_id = run_id
    if test_mode and run_id and not run_id.startswith("test-"):
        effective_run_id = f"test-{run_id}"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_name": agent_name,
        "agent_owner": config.agent_owner,
        "job_type": job_type,
        "run_id": effective_run_id,
        "status": status,
        "product": product,
        "platform": config.platform,
        "website": config.website,
        "website_section": config.website_section,
        "item_name": item_name,
        "items_discovered": items_discovered,
        "items_succeeded": items_succeeded,
        "items_failed": items_failed,
        "run_duration_ms": int(run_duration_ms),
        "token_usage": token_usage,
        "api_calls_count": api_calls_count,
    }
