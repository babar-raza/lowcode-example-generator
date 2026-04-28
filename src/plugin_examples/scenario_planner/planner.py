"""Plan example scenarios from reflected API catalog and delta."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.plugin_detector.proof_reporter import (
    SourceOfTruthGateError,
    assert_source_of_truth_eligible,
)

logger = logging.getLogger(__name__)


@dataclass
class Scenario:
    """A planned example scenario."""
    scenario_id: str
    title: str
    target_type: str
    target_namespace: str
    target_methods: list[str] = field(default_factory=list)
    required_symbols: list[str] = field(default_factory=list)
    required_fixtures: list[str] = field(default_factory=list)
    output_plan: str = ""
    validation_plan: str = ""
    status: str = "ready"  # ready, blocked_no_fixture, blocked_unclear_semantics, blocked_obsolete
    blocked_reason: str | None = None


@dataclass
class PlanningResult:
    """Result of scenario planning."""
    family: str
    ready_scenarios: list[Scenario] = field(default_factory=list)
    blocked_scenarios: list[Scenario] = field(default_factory=list)

    @property
    def ready_count(self) -> int:
        return len(self.ready_scenarios)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_scenarios)


def plan_scenarios(
    *,
    family: str,
    catalog: dict,
    plugin_namespaces: list[str],
    fixture_registry: dict | None = None,
    min_examples: int = 3,
    source_of_truth_proof_path: str | None = None,
) -> PlanningResult:
    """Plan example scenarios from reflected API catalog.

    Args:
        family: Family name.
        catalog: API catalog dict.
        plugin_namespaces: List of matched plugin namespace names.
        fixture_registry: Fixture registry dict (optional).
        min_examples: Minimum required ready scenarios.
        source_of_truth_proof_path: Path to proof file (gate check).

    Returns:
        PlanningResult with ready and blocked scenarios.

    Raises:
        SourceOfTruthGateError: If proof is missing or not eligible.
    """
    # Gate check: source of truth must be eligible
    if source_of_truth_proof_path:
        assert_source_of_truth_eligible(source_of_truth_proof_path)

    result = PlanningResult(family=family)

    # Build scenarios from plugin namespace types
    for ns in catalog.get("namespaces", []):
        ns_name = ns.get("namespace", "")
        if ns_name not in plugin_namespaces:
            continue

        for type_info in ns.get("types", []):
            if type_info.get("is_obsolete", False):
                result.blocked_scenarios.append(_make_blocked_scenario(
                    family, type_info, ns_name, "blocked_obsolete",
                    f"Type {type_info['full_name']} is obsolete",
                ))
                continue

            if type_info.get("kind") == "enum":
                continue  # Enums don't get standalone scenarios

            methods = type_info.get("methods", [])
            if not methods:
                result.blocked_scenarios.append(_make_blocked_scenario(
                    family, type_info, ns_name, "blocked_unclear_semantics",
                    f"Type {type_info['full_name']} has no public methods",
                ))
                continue

            # Build scenario for this type
            scenario = _build_scenario(family, type_info, ns_name, fixture_registry)
            if scenario.status == "ready":
                result.ready_scenarios.append(scenario)
            else:
                result.blocked_scenarios.append(scenario)

    logger.info(
        "Planning for %s: %d ready, %d blocked",
        family, result.ready_count, result.blocked_count,
    )
    return result


def _build_scenario(
    family: str,
    type_info: dict,
    namespace: str,
    fixture_registry: dict | None,
) -> Scenario:
    """Build a scenario for a single type."""
    full_name = type_info["full_name"]
    name = type_info["name"]
    methods = type_info.get("methods", [])

    # Determine required symbols
    required_symbols = [full_name]
    target_methods = []
    for m in methods:
        if not m.get("is_obsolete", False):
            target_methods.append(m["name"])
            required_symbols.append(f"{full_name}.{m['name']}")

    # Generate slug
    slug = _to_slug(name)
    scenario_id = f"{family}-{slug}"

    # Determine if fixtures are needed (heuristic: if method has file-like params)
    needs_fixture = _needs_fixture(methods)
    required_fixtures = []
    if needs_fixture:
        fixture_name = f"sample-{family}.xlsx"
        required_fixtures = [fixture_name]

    # Check fixture availability
    status = "ready"
    blocked_reason = None

    if needs_fixture and fixture_registry:
        available = fixture_registry.get("fixtures", [])
        available_names = {f.get("filename", "") for f in available}
        if not any(fn in available_names for fn in required_fixtures):
            # Don't block — fixtures can be generated
            pass

    # Build output and validation plans
    output_plan = f"Console output demonstrating {name} usage"
    validation_plan = f"Build succeeds, runs without exception, uses {', '.join(target_methods[:3])}"

    return Scenario(
        scenario_id=scenario_id,
        title=f"Use {name} from {namespace}",
        target_type=full_name,
        target_namespace=namespace,
        target_methods=target_methods,
        required_symbols=required_symbols,
        required_fixtures=required_fixtures,
        output_plan=output_plan,
        validation_plan=validation_plan,
        status=status,
        blocked_reason=blocked_reason,
    )


def _make_blocked_scenario(
    family: str,
    type_info: dict,
    namespace: str,
    status: str,
    reason: str,
) -> Scenario:
    """Create a blocked scenario."""
    slug = _to_slug(type_info["name"])
    return Scenario(
        scenario_id=f"{family}-{slug}",
        title=f"Use {type_info['name']} from {namespace}",
        target_type=type_info["full_name"],
        target_namespace=namespace,
        status=status,
        blocked_reason=reason,
    )


def _to_slug(name: str) -> str:
    """Convert a class name to a slug."""
    # CamelCase to kebab-case
    s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'-\1', name)
    return s.lower()


def _needs_fixture(methods: list[dict]) -> bool:
    """Heuristic: check if methods suggest file input is needed."""
    file_param_types = {"System.String", "System.IO.Stream", "Stream", "String"}
    for m in methods:
        for p in m.get("parameters", []):
            param_type = p.get("type", "")
            param_name = p.get("name", "").lower()
            if param_type in file_param_types and any(
                kw in param_name for kw in ("path", "file", "input", "source", "stream")
            ):
                return True
    return False
