"""Metrics configuration loader — lazy, config-driven, no secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class MetricsConfig:
    """Parsed metrics configuration."""

    enabled: bool = False
    dry_run: bool = True
    strict_mode: bool = False

    agent_owner: str = ""
    agent_name: str = "Lowcode Example Generator"
    agent_name_test_prefix: str = "test-"

    website: str = "aspose.net"
    website_section: str = "Examples"
    platform: str = ".NET"

    family_to_product: dict[str, str] = field(default_factory=dict)
    command_to_job_type: dict[str, str] = field(default_factory=dict)
    command_to_item_name: dict[str, str] = field(default_factory=dict)
    verdict_to_status: dict[str, str] = field(default_factory=dict)

    allowed_statuses: list[str] = field(
        default_factory=lambda: ["success", "partial_success", "failure"]
    )
    allowed_job_types: list[str] = field(
        default_factory=lambda: ["Examples Generation", "Discovery", "Publishing", "Reporting", "Test"]
    )

    api_endpoint: str = ""
    post_ledger_path: str = "workspace/verification/agent-metrics-post-ledger.jsonl"
    ledger_max_entries: int = 500

    env_token_var: str = "AGENT_METRICS_TOKEN"

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = valid)."""
        errors: list[str] = []
        if not self.agent_owner:
            errors.append("agent_owner is required")
        if not self.agent_name:
            errors.append("agent_name is required")
        if not self.website:
            errors.append("website is required")
        if not self.api_endpoint:
            errors.append("api_endpoint is required")
        if not self.family_to_product:
            errors.append("family_to_product must have at least one entry")
        if not self.command_to_job_type:
            errors.append("command_to_job_type must have at least one entry")
        if not self.verdict_to_status:
            errors.append("verdict_to_status must have at least one entry")
        # Unknown verdicts mapping to success is never allowed
        for verdict, status in self.verdict_to_status.items():
            if status not in self.allowed_statuses:
                errors.append(
                    f"verdict_to_status[{verdict}] maps to invalid status '{status}'"
                )
        return errors

    def validate_family(self, family: str) -> str | None:
        """Return error message if family is not mapped, else None."""
        if family not in self.family_to_product:
            return f"Family '{family}' not in family_to_product mapping"
        return None

    def validate_command(self, command: str) -> str | None:
        """Return error message if command is not mapped, else None."""
        if command not in self.command_to_job_type:
            return f"Command '{command}' not in command_to_job_type mapping"
        return None

    def resolve_status(self, verdict: str) -> tuple[str, bool]:
        """Map verdict to (status, was_unknown).

        Unknown verdicts map to 'failure', never 'success'.
        """
        if verdict in self.verdict_to_status:
            return self.verdict_to_status[verdict], False
        return "failure", True


def load_metrics_config(
    config_path: Path | None = None,
    override: dict | None = None,
) -> MetricsConfig:
    """Load metrics config from YAML file.

    Args:
        config_path: Path to metrics.yml. If None, uses default location.
        override: Dict of field overrides (for testing).
    """
    if config_path is None:
        config_path = (
            Path(__file__).resolve().parents[3]
            / "pipeline"
            / "configs"
            / "metrics.yml"
        )

    raw: dict = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data and "metrics" in data:
            raw = data["metrics"]

    # Extract env block first so env var names are config-driven
    env_block = raw.pop("env", {})
    env_token_var = env_block.get("metrics_token", "AGENT_METRICS_TOKEN")
    env_endpoint_var = env_block.get("metrics_endpoint", "AGENT_METRICS_ENDPOINT")

    # Apply env var overrides
    if os.environ.get("AGENT_METRICS_ENABLED", "").lower() == "true":
        raw.setdefault("enabled", True)
    if os.environ.get("AGENT_METRICS_DRY_RUN", "").lower() == "false":
        raw["dry_run"] = False
    if os.environ.get("AGENT_METRICS_STRICT", "").lower() == "true":
        raw["strict_mode"] = True
    endpoint_override = os.environ.get(env_endpoint_var, "")
    if endpoint_override:
        raw["api_endpoint"] = endpoint_override

    # Apply overrides
    if override:
        raw.update(override)

    return MetricsConfig(
        enabled=raw.get("enabled", False),
        dry_run=raw.get("dry_run", True),
        strict_mode=raw.get("strict_mode", False),
        agent_owner=raw.get("agent_owner", ""),
        agent_name=raw.get("agent_name", "Lowcode Example Generator"),
        agent_name_test_prefix=raw.get("agent_name_test_prefix", "test-"),
        website=raw.get("website", "aspose.net"),
        website_section=raw.get("website_section", "Examples"),
        platform=raw.get("platform", ".NET"),
        family_to_product=raw.get("family_to_product", {}),
        command_to_job_type=raw.get("command_to_job_type", {}),
        command_to_item_name=raw.get("command_to_item_name", {}),
        verdict_to_status=raw.get("verdict_to_status", {}),
        allowed_statuses=raw.get("allowed_statuses", ["success", "partial_success", "failure"]),
        allowed_job_types=raw.get("allowed_job_types", ["Examples Generation", "Discovery", "Publishing", "Reporting", "Test"]),
        api_endpoint=raw.get("api_endpoint", ""),
        post_ledger_path=raw.get("post_ledger_path", "workspace/verification/agent-metrics-post-ledger.jsonl"),
        ledger_max_entries=raw.get("ledger_max_entries", 500),
        env_token_var=env_token_var,
    )


def is_agent_metrics_production_enabled() -> bool:
    """Return True only when AGENT_METRICS_PRODUCTION_ENABLED=true is explicitly set.

    Single production gate for Agent Metrics. Does not read AGENT_METRICS_TOKEN,
    AGENT_METRICS_DRY_RUN, or perform network I/O. Default: False.
    """
    return os.environ.get("AGENT_METRICS_PRODUCTION_ENABLED", "") == "true"
