"""Write scenario catalogs and blocked scenario reports."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.scenario_planner.planner import PlanningResult, Scenario

logger = logging.getLogger(__name__)


def write_scenario_catalog(
    result: PlanningResult,
    manifests_dir: Path,
) -> Path:
    """Write scenario catalog to manifests directory."""
    manifests_dir.mkdir(parents=True, exist_ok=True)
    path = manifests_dir / "scenario-catalog.json"

    data = {
        "family": result.family,
        "ready_count": result.ready_count,
        "blocked_count": result.blocked_count,
        "scenarios": [_scenario_to_dict(s) for s in result.ready_scenarios],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Scenario catalog written: %s (%d ready)", path, result.ready_count)
    return path


def write_blocked_scenarios(
    result: PlanningResult,
    verification_dir: Path,
) -> Path:
    """Write blocked scenarios report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "blocked-scenarios.json"

    data = {
        "family": result.family,
        "blocked_count": result.blocked_count,
        "blocked_scenarios": [_scenario_to_dict(s) for s in result.blocked_scenarios],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Blocked scenarios written: %s (%d blocked)", path, result.blocked_count)
    return path


def _scenario_to_dict(s: Scenario) -> dict:
    return {
        "scenario_id": s.scenario_id,
        "title": s.title,
        "target_type": s.target_type,
        "target_namespace": s.target_namespace,
        "target_methods": s.target_methods,
        "required_symbols": s.required_symbols,
        "required_fixtures": s.required_fixtures,
        "output_plan": s.output_plan,
        "validation_plan": s.validation_plan,
        "status": s.status,
        "blocked_reason": s.blocked_reason,
    }
