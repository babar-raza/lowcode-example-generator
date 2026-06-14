"""Config-driven payload validation — no hardcoded allowlists."""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = [
    "timestamp",
    "agent_name",
    "agent_owner",
    "job_type",
    "run_id",
    "status",
    "product",
    "platform",
    "website",
    "website_section",
    "item_name",
    "items_discovered",
    "items_failed",
    "items_succeeded",
    "run_duration_ms",
    "token_usage",
    "api_calls_count",
]


def validate_payload(payload: dict, config: Any) -> dict:
    """Validate a metrics payload against config-driven rules.

    Returns dict with:
        valid: bool
        errors: list[str]
        warnings: list[str]
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required fields
    for f in REQUIRED_FIELDS:
        if f not in payload:
            errors.append(f"missing required field: {f}")
        elif payload[f] is None:
            errors.append(f"field '{f}' is None")

    # String fields must be non-empty
    for f in [
        "timestamp",
        "agent_name",
        "agent_owner",
        "run_id",
        "product",
        "platform",
        "website",
        "website_section",
        "item_name",
    ]:
        val = payload.get(f, "")
        if isinstance(val, str) and not val:
            errors.append(f"field '{f}' is empty")

    # Status must be in config-allowed values (config-driven, not hardcoded)
    status = payload.get("status", "")
    if status and status not in config.allowed_statuses:
        errors.append(f"status '{status}' not in allowed_statuses: {config.allowed_statuses}")

    # job_type must be in config-allowed values (config-driven)
    job_type = payload.get("job_type", "")
    if job_type and job_type not in config.allowed_job_types:
        errors.append(f"job_type '{job_type}' not in allowed_job_types: {config.allowed_job_types}")

    # Website from config (config-driven validation)
    website = payload.get("website", "")
    if website and website != config.website:
        warnings.append(f"website '{website}' differs from config website '{config.website}'")

    # Numeric fields must be non-negative integers
    for f in [
        "items_discovered",
        "items_succeeded",
        "items_failed",
        "run_duration_ms",
        "token_usage",
        "api_calls_count",
    ]:
        val = payload.get(f)
        if val is not None and (not isinstance(val, int) or val < 0):
            errors.append(f"field '{f}' must be a non-negative integer, got {val!r}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
