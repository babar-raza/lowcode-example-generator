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
from plugin_examples.scenario_planner.type_classifier import (
    STANDALONE_ROLES,
    classify_type,
    TypeRole,
)
from plugin_examples.scenario_planner.consumer_mapper import build_consumer_map
from plugin_examples.scenario_planner.entrypoint_scorer import (
    score_entrypoint,
    EntrypointScore,
)
from plugin_examples.fixture_registry.fixture_factory import SUPPORTED_FORMATS

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
    input_strategy: str = "none"  # existing_fixture, generated_fixture_file, programmatic_input, hybrid, no_valid_input_strategy, none
    input_files: list[str] = field(default_factory=list)
    required_input_format: str = ""


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
    default_fixture_extension: str = ".xlsx",
) -> PlanningResult:
    """Plan example scenarios from reflected API catalog.

    Uses type role classification and entrypoint scoring to ensure only
    workflow-root and operation-facade types become standalone scenarios.
    Provider/callback types are blocked with explicit reasons.

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

    # Build consumer map for entrypoint scoring
    consumer_map = build_consumer_map(catalog, plugin_namespaces)

    # Build scenarios from plugin namespace types
    for ns in catalog.get("namespaces", []):
        ns_name = ns.get("namespace", "")
        if ns_name not in plugin_namespaces:
            continue

        for type_info in ns.get("types", []):
            full_name = type_info.get("full_name", "")

            if type_info.get("is_obsolete", False):
                result.blocked_scenarios.append(_make_blocked_scenario(
                    family, type_info, ns_name, "blocked_obsolete",
                    f"Type {full_name} is obsolete",
                ))
                continue

            # Classify the type role
            role = classify_type(type_info)

            # Enum — skip entirely
            if role.role == "enum":
                continue

            # Score the entrypoint
            fixture_available = _check_fixture_available(
                type_info, fixture_registry, default_fixture_extension)
            ep_score = score_entrypoint(
                type_info, role, consumer_map,
                fixture_available=fixture_available,
            )

            # Non-standalone roles are blocked with explicit reason
            if role.role not in STANDALONE_ROLES:
                result.blocked_scenarios.append(_make_blocked_scenario(
                    family, type_info, ns_name,
                    f"blocked_{role.role}",
                    ep_score.rejection_reason or f"Type role '{role.role}' is not a standalone entrypoint",
                ))
                continue

            # Standalone role but scored as not runnable
            if not ep_score.runnable:
                result.blocked_scenarios.append(_make_blocked_scenario(
                    family, type_info, ns_name,
                    "blocked_low_score",
                    ep_score.rejection_reason or f"Entrypoint score too low ({ep_score.score:.1f})",
                ))
                continue

            # Build scenario for this type
            scenario = _build_scenario(family, type_info, ns_name, fixture_registry, default_fixture_extension)
            if scenario.status == "ready":
                result.ready_scenarios.append(scenario)
            else:
                result.blocked_scenarios.append(scenario)

    logger.info(
        "Planning for %s: %d ready, %d blocked",
        family, result.ready_count, result.blocked_count,
    )
    return result


def _check_fixture_available(
    type_info: dict,
    fixture_registry: dict | None,
    default_fixture_extension: str,
) -> bool:
    """Check if fixtures are available for a type."""
    if not fixture_registry:
        return False
    available = fixture_registry.get("fixtures", [])
    available_names = {f.get("filename", "") for f in available if f.get("available", True)}
    return len(available_names) > 0


def _build_scenario(
    family: str,
    type_info: dict,
    namespace: str,
    fixture_registry: dict | None,
    default_fixture_extension: str = ".xlsx",
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
        fixture_name = f"sample-{family}{default_fixture_extension}"
        required_fixtures = [fixture_name]

    # Infer the correct input format for this specific scenario
    inferred_input_format = _infer_input_format(name, default_fixture_extension)

    # Determine input strategy with proven input resolution
    status = "ready"
    blocked_reason = None
    input_strategy = "none"
    input_files: list[str] = []
    required_input_format = inferred_input_format

    if needs_fixture:
        # Priority 1: existing fixture from registry
        fixture_found = False
        if fixture_registry:
            available = fixture_registry.get("fixtures", [])
            available_names = {f.get("filename", "") for f in available if f.get("available", True)}
            fixture_found = any(fn in available_names for fn in required_fixtures)

        if fixture_found:
            input_strategy = "existing_fixture"
            input_files = list(required_fixtures)
        elif inferred_input_format in SUPPORTED_FORMATS:
            # Priority 2: pipeline generates a minimal valid fixture file
            input_strategy = "generated_fixture_file"
            input_filename = f"input{inferred_input_format}"
            input_files = [input_filename]
            required_fixtures = [input_filename]
        elif _has_static_methods(methods):
            # Priority 3: programmatic input via Aspose API in Program.cs
            input_strategy = "programmatic_input"
            input_files = []
            required_fixtures = []
        else:
            # No valid input strategy — block the scenario
            input_strategy = "no_valid_input_strategy"
            status = "blocked_no_fixture"
            blocked_reason = (
                f"Required fixture format '{inferred_input_format}' not in "
                f"supported generator formats and no existing fixture found"
            )
    else:
        input_strategy = "none"

    # Build output and validation plans
    inferred_output_format = _infer_output_format(name)
    output_plan = f"Convert input{inferred_input_format} to output{inferred_output_format} using {name}"
    validation_plan = f"Build succeeds, runs without exception, produces output{inferred_output_format}"

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
        input_strategy=input_strategy,
        input_files=input_files,
        required_input_format=required_input_format,
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


# ---------------------------------------------------------------------------
# Input format inference — scenario-specific mapping
# ---------------------------------------------------------------------------

# Map workflow-root type name patterns to their correct input format.
# Key = lowercased type name (without namespace), Value = input extension.
# Converters that IMPORT a format use that format as input.
# Converters that EXPORT to a format use the family default as input.
_INPUT_FORMAT_MAP: dict[str, str] = {
    "textconverter": ".csv",        # TextConverter processes text-based formats only
    "jsonconverter": ".xlsx",       # JsonConverter exports spreadsheet to JSON
    "htmlconverter": ".xlsx",       # HtmlConverter exports spreadsheet to HTML
    "pdfconverter": ".xlsx",        # PdfConverter exports spreadsheet to PDF
    "imageconverter": ".xlsx",      # ImageConverter renders spreadsheet to image
    "spreadsheetconverter": ".xlsx",  # Converts between spreadsheet formats
    "spreadsheetmerger": ".xlsx",   # Merges multiple spreadsheets
    "spreadsheetsplitter": ".xlsx", # Splits spreadsheet into sheets
    "spreadsheetlocker": ".xlsx",   # Locks/protects a spreadsheet
}


def _infer_input_format(type_name: str, family_default: str) -> str:
    """Infer the correct input format for a scenario based on type name.

    Args:
        type_name: Simple type name (e.g., "TextConverter").
        family_default: Default input extension for the family (e.g., ".xlsx").

    Returns:
        The inferred input extension.
    """
    key = type_name.lower()
    return _INPUT_FORMAT_MAP.get(key, family_default)


def _infer_output_format(type_name: str) -> str:
    """Infer the output format from the type name."""
    name_lower = type_name.lower()
    _map = {
        "textconverter": ".txt",
        "jsonconverter": ".json",
        "htmlconverter": ".html",
        "pdfconverter": ".pdf",
        "imageconverter": ".png",
        "spreadsheetconverter": ".xlsx",
        "spreadsheetmerger": ".xlsx",
        "spreadsheetsplitter": ".xlsx",
        "spreadsheetlocker": ".xlsx",
    }
    return _map.get(name_lower, ".out")


def _has_static_methods(methods: list[dict]) -> bool:
    """Check if any methods are static."""
    return any(m.get("is_static", False) for m in methods)


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
