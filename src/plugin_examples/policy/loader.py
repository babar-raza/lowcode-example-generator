"""Load gate policies, goal specifications, and SLO definitions from YAML.

Falls back to hardcoded defaults when YAML files are missing, so existing
behavior is preserved in environments where the config files haven't been
deployed yet.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class GatePolicy:
    """Externalized gate policy rules."""

    hard_stop_stages: frozenset[str] = field(default_factory=frozenset)
    approval_gated_types: frozenset[str] = field(default_factory=frozenset)
    publishable_verdicts: frozenset[str] = field(default_factory=frozenset)
    deprioritization_threshold: int = 3
    deprioritization_cooldown: int = 2


@dataclass
class GoalSpec:
    """A single declarative goal for the planner loop."""

    id: str
    metric: str
    threshold: float
    weight: int
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "metric": self.metric,
            "threshold": self.threshold,
            "weight": self.weight,
            "description": self.description,
        }


@dataclass
class SLODefinition:
    """A single Service Level Objective."""

    id: str
    metric: str
    target: float
    window_runs: int
    severity: str = "warning"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "metric": self.metric,
            "target": self.target,
            "window_runs": self.window_runs,
            "severity": self.severity,
        }


# ---------------------------------------------------------------------------
# Hardcoded defaults (match current behavior before policy-as-code)
# ---------------------------------------------------------------------------

_DEFAULT_GATE_POLICY = GatePolicy(
    hard_stop_stages=frozenset({
        "load_config", "nuget_fetch", "dependency_resolution",
        "extraction", "reflection", "plugin_detection",
    }),
    approval_gated_types=frozenset({
        "MERGE_READY_PR", "PDF_PR_CONFLICT_RECOVERY", "LIVE_PUBLISH_READY_PACKAGE",
    }),
    publishable_verdicts=frozenset({
        "PR_READY", "FULL_E2E_PASSED",
        "CANONICAL_TEMPLATE_GENERATION_PASS", "CANONICAL_LLM_GENERATION_PASS",
    }),
    deprioritization_threshold=3,
    deprioritization_cooldown=2,
)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_gate_policy(repo_root: Path) -> GatePolicy:
    """Load gate policy from pipeline/policies/gates.yml with fallback."""
    path = repo_root / "pipeline" / "policies" / "gates.yml"
    if not path.exists():
        logger.debug("gates.yml not found at %s, using defaults", path)
        return _DEFAULT_GATE_POLICY

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        logger.warning("Failed to parse %s, using defaults", path)
        return _DEFAULT_GATE_POLICY

    deprio = data.get("deprioritization", {})
    return GatePolicy(
        hard_stop_stages=frozenset(data.get("hard_stop_stages", [])),
        approval_gated_types=frozenset(data.get("approval_gated_types", [])),
        publishable_verdicts=frozenset(data.get("publishable_verdicts", [])),
        deprioritization_threshold=deprio.get("consecutive_failure_threshold", 3),
        deprioritization_cooldown=deprio.get("cooldown_runs", 2),
    )


def load_goals(repo_root: Path) -> list[GoalSpec]:
    """Load goal specifications from pipeline/configs/goals.yml."""
    path = repo_root / "pipeline" / "configs" / "goals.yml"
    if not path.exists():
        logger.debug("goals.yml not found at %s, returning empty goals", path)
        return []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        logger.warning("Failed to parse %s, returning empty goals", path)
        return []

    goals: list[GoalSpec] = []
    for entry in data.get("goals", []):
        goals.append(GoalSpec(
            id=entry.get("id", ""),
            metric=entry.get("metric", ""),
            threshold=float(entry.get("threshold", 0)),
            weight=int(entry.get("weight", 1)),
            description=entry.get("description", ""),
        ))
    return goals


def load_slos(repo_root: Path) -> list[SLODefinition]:
    """Load SLO definitions from pipeline/configs/slo.yml."""
    path = repo_root / "pipeline" / "configs" / "slo.yml"
    if not path.exists():
        logger.debug("slo.yml not found at %s, returning empty SLOs", path)
        return []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        logger.warning("Failed to parse %s, returning empty SLOs", path)
        return []

    slos: list[SLODefinition] = []
    for entry in data.get("slos", []):
        slos.append(SLODefinition(
            id=entry.get("id", ""),
            metric=entry.get("metric", ""),
            target=float(entry.get("target", 0)),
            window_runs=int(entry.get("window_runs", 10)),
            severity=entry.get("severity", "warning"),
        ))
    return slos
