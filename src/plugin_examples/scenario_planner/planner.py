"""Plan example scenarios from reflected API catalog and delta."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path

from plugin_examples.fixture_registry.fixture_factory import SUPPORTED_FORMATS
from plugin_examples.plugin_detector.proof_reporter import (
    SourceOfTruthGateError,
    assert_source_of_truth_eligible,
)
from plugin_examples.scenario_planner.consumer_mapper import build_consumer_map
from plugin_examples.scenario_planner.entrypoint_scorer import (
    EntrypointScore,
    score_entrypoint,
)
from plugin_examples.scenario_planner.type_classifier import (
    STANDALONE_ROLES,
    TypeRole,
    classify_type,
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
    input_strategy: str = (
        "none"  # existing_fixture, generated_fixture_file, programmatic_input, hybrid, no_valid_input_strategy, none
    )
    input_files: list[str] = field(default_factory=list)
    required_input_format: str = ""
    required_output_contract: str = ""  # canonical output from FormatContract
    format_contract_id: str = ""  # e.g. "cells/SpreadsheetConverter"
    format_contract_hash: str = ""  # for traceability
    fixture_strategy: str = ""  # "real_github", "synthetic_fallback", "cache_hit", etc.
    fixture_sources: list[dict] = field(default_factory=list)  # provenance refs


@dataclass
class PlanningResult:
    """Result of scenario planning."""

    family: str
    ready_scenarios: list[Scenario] = field(default_factory=list)
    blocked_scenarios: list[Scenario] = field(default_factory=list)
    sufficiency_status: str = "UNKNOWN"  # SUFFICIENT, BELOW_MINIMUM, REGISTRY_INCOMPLETE, UNKNOWN
    min_examples_required: int = 0
    total_registry_entries: int = 0

    @property
    def ready_count(self) -> int:
        return len(self.ready_scenarios)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_scenarios)


_REGISTRY_GENERATION_READY = frozenset({"PROBE_CONFIRMED", "VERIFIED_PUBLISHABLE"})


def plan_scenarios_from_registry(
    *,
    family: str,
    registry_entries: list[dict],
    source_of_truth_proof_path: str | None = None,
    min_examples: int = 3,
) -> PlanningResult:
    """Plan example scenarios from capability registry entries.

    Non-LowCode families use registry entries (PROBE_CONFIRMED, VERIFIED_PUBLISHABLE)
    instead of DllReflector catalogs. Each generation-ready entry becomes a ready
    scenario; non-ready entries become blocked scenarios.

    Args:
        family: Family name.
        registry_entries: List of registry entry dicts from YAML.
        source_of_truth_proof_path: Path to non-LowCode SOT proof (gate check).
        min_examples: Minimum required ready scenarios for SUFFICIENT status.

    Returns:
        PlanningResult with ready and blocked scenarios.

    Raises:
        SourceOfTruthGateError: If proof is missing or not eligible.
    """
    from plugin_examples.plugin_detector.proof_reporter import (
        assert_nonlowcode_source_of_truth_eligible,
    )

    if source_of_truth_proof_path:
        assert_nonlowcode_source_of_truth_eligible(source_of_truth_proof_path)

    result = PlanningResult(family=family)

    for entry in registry_entries:
        if not isinstance(entry, dict):
            continue

        plugin_slug = entry.get("plugin_slug") or entry.get("slug", "unknown")
        status = entry.get("status", "UNKNOWN")
        type_name = entry.get("type_name", "")
        namespace = entry.get("namespace", "")
        method_name = entry.get("method_name", "")
        operation_kind = entry.get("operation_kind", "")

        scenario_id = f"{family}-{plugin_slug}"
        target_type = f"{namespace}.{type_name}" if namespace and type_name else type_name
        title = f"Use {type_name} from {namespace}" if namespace else f"Use {plugin_slug}"

        # Collect methods
        target_methods = []
        if method_name:
            target_methods.append(method_name)
        for cm in entry.get("candidate_methods", []):
            if cm and cm not in target_methods:
                target_methods.append(cm)

        # Derive input/output from selected_api_mapping
        api_mapping = entry.get("selected_api_mapping") or {}
        constructor = api_mapping.get("constructor", "")
        output_format = (
            api_mapping.get("output_format")
            or api_mapping.get("output_format_enum")
            or ""
        )

        # Determine input strategy from constructor hint
        input_strategy = "programmatic_input"
        if "string" in constructor.lower() or "stream" in constructor.lower():
            input_strategy = "programmatic_input"

        # Determine output plan
        output_plan = f"{operation_kind}: {type_name}.{method_name}" if method_name else operation_kind

        if status in _REGISTRY_GENERATION_READY:
            scenario = Scenario(
                scenario_id=scenario_id,
                title=title,
                target_type=target_type,
                target_namespace=namespace,
                target_methods=target_methods,
                required_symbols=[target_type],
                output_plan=output_plan,
                validation_plan=f"Build succeeds, runs without exception, produces output",
                status="ready",
                input_strategy=input_strategy,
            )
            result.ready_scenarios.append(scenario)
        else:
            scenario = Scenario(
                scenario_id=scenario_id,
                title=title,
                target_type=target_type,
                target_namespace=namespace,
                target_methods=target_methods,
                status="blocked_probe_pending",
                blocked_reason=(
                    f"Registry status '{status}' is not generation-ready "
                    f"(need PROBE_CONFIRMED or VERIFIED_PUBLISHABLE)"
                ),
            )
            result.blocked_scenarios.append(scenario)

    # Sufficiency assessment (TC-PSAL-02)
    result.total_registry_entries = len(registry_entries)
    result.min_examples_required = min_examples
    if result.ready_count >= min_examples:
        result.sufficiency_status = "SUFFICIENT"
    elif result.total_registry_entries > result.ready_count:
        result.sufficiency_status = "REGISTRY_INCOMPLETE"
        logger.warning(
            "Registry sufficiency for %s: REGISTRY_INCOMPLETE — "
            "%d ready of %d entries, min required %d. "
            "%d entries need probing before generation.",
            family,
            result.ready_count,
            result.total_registry_entries,
            min_examples,
            result.blocked_count,
        )
    else:
        result.sufficiency_status = "BELOW_MINIMUM"
        logger.warning(
            "Registry sufficiency for %s: BELOW_MINIMUM — "
            "%d ready, min required %d. "
            "Registry has only %d total entries.",
            family,
            result.ready_count,
            min_examples,
            result.total_registry_entries,
        )

    logger.info(
        "Registry planning for %s: %d ready, %d blocked, sufficiency=%s",
        family,
        result.ready_count,
        result.blocked_count,
        result.sufficiency_status,
    )
    return result


def plan_scenarios(
    *,
    family: str,
    catalog: dict,
    plugin_namespaces: list[str],
    fixture_registry: dict | None = None,
    min_examples: int = 3,
    source_of_truth_proof_path: str | None = None,
    default_fixture_extension: str = ".xlsx",
    allowed_types: list[str] | None = None,
    preferred_methods_per_type: dict[str, str] | None = None,
    repo_root: Path | None = None,
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
        allowed_types: Optional allowlist of type short-names (e.g. ["Converter", "Splitter"]).
            When non-empty, types not in this list are blocked as pilot_not_in_scope.
        preferred_methods_per_type: Optional map of type short-name to preferred primary method
            (e.g. {"Watermarker": "SetText"}). The specified method is placed first in
            target_methods so the LLM demonstrates it as the primary operation.

    Returns:
        PlanningResult with ready and blocked scenarios.

    Raises:
        SourceOfTruthGateError: If proof is missing or not eligible.
    """
    # Gate check: source of truth must be eligible
    if source_of_truth_proof_path:
        assert_source_of_truth_eligible(source_of_truth_proof_path)

    # Catalog hash validation (B-013): strict enforcement (F-1 closure)
    if repo_root is not None:
        validate_catalog_hash(family, catalog, repo_root, strict=True)

    result = PlanningResult(family=family)
    _allowed = set(allowed_types) if allowed_types else set()
    _preferred = preferred_methods_per_type or {}

    # Build consumer map for entrypoint scoring
    consumer_map = build_consumer_map(catalog, plugin_namespaces)

    # Build scenarios from plugin namespace types
    for ns in catalog.get("namespaces", []):
        ns_name = ns.get("namespace", "")
        if ns_name not in plugin_namespaces:
            continue

        for type_info in ns.get("types", []):
            full_name = type_info.get("full_name", "")
            type_short_name = type_info.get("name", "")

            if type_info.get("is_obsolete", False):
                result.blocked_scenarios.append(
                    _make_blocked_scenario(
                        family,
                        type_info,
                        ns_name,
                        "blocked_obsolete",
                        f"Type {full_name} is obsolete",
                    )
                )
                continue

            # Classify the type role
            role = classify_type(type_info)

            # Enum — not a runnable LowCode API; record in blocked_scenarios for tracking
            if role.role == "enum":
                result.blocked_scenarios.append(
                    _make_blocked_scenario(
                        family,
                        type_info,
                        ns_name,
                        "blocked_enum_not_runnable",
                        f"Type '{type_info['name']}' is an ENUM — not a runnable LowCode API.",
                    )
                )
                continue

            # Allowlist enforcement: if allowed_types is set, block types not in it.
            # ENUMs are classified before this gate so they remain visible as
            # blocked_enum_not_runnable instead of pilot scope exclusions.
            if _allowed and type_short_name not in _allowed:
                result.blocked_scenarios.append(
                    _make_blocked_scenario(
                        family,
                        type_info,
                        ns_name,
                        "blocked_pilot_not_in_scope",
                        f"Type '{type_short_name}' is not in the controlled pilot allowlist. "
                        f"Allowed: {sorted(_allowed)}",
                    )
                )
                continue

            # Score the entrypoint
            fixture_available = _check_fixture_available(type_info, fixture_registry, default_fixture_extension)
            ep_score = score_entrypoint(
                type_info,
                role,
                consumer_map,
                fixture_available=fixture_available,
            )

            # Non-standalone roles are blocked with explicit reason
            if role.role not in STANDALONE_ROLES:
                result.blocked_scenarios.append(
                    _make_blocked_scenario(
                        family,
                        type_info,
                        ns_name,
                        f"blocked_{role.role}",
                        ep_score.rejection_reason or f"Type role '{role.role}' is not a standalone entrypoint",
                    )
                )
                continue

            # Standalone role but scored as not runnable
            if not ep_score.runnable:
                result.blocked_scenarios.append(
                    _make_blocked_scenario(
                        family,
                        type_info,
                        ns_name,
                        "blocked_low_score",
                        ep_score.rejection_reason or f"Entrypoint score too low ({ep_score.score:.1f})",
                    )
                )
                continue

            # Build scenario for this type
            preferred_method = _preferred.get(type_short_name)
            scenario = _build_scenario(
                family,
                type_info,
                ns_name,
                fixture_registry,
                default_fixture_extension,
                preferred_method=preferred_method,
            )
            if scenario.status == "ready":
                result.ready_scenarios.append(scenario)
            else:
                result.blocked_scenarios.append(scenario)

    logger.info(
        "Planning for %s: %d ready, %d blocked",
        family,
        result.ready_count,
        result.blocked_count,
    )
    return result


# ---------------------------------------------------------------------------
# Catalog hash enforcement (B-013)
# ---------------------------------------------------------------------------


class CatalogHashMismatchError(Exception):
    """Raised in strict mode when catalog hash doesn't match denominator."""


@dataclass
class CatalogHashResult:
    """Result of catalog hash validation against denominator."""

    family: str
    match: bool | None  # None = indeterminate (no denominator)
    current_hash: str
    denominator_hash: str | None
    denominator_path: str | None

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "match": self.match,
            "current_hash": self.current_hash,
            "denominator_hash": self.denominator_hash,
            "denominator_path": self.denominator_path,
        }


def compute_catalog_hash(catalog: dict) -> str:
    """Compute deterministic SHA-256 hash of an API catalog dict."""
    canonical = json.dumps(catalog, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_catalog_hash(
    family: str,
    catalog: dict,
    repo_root: Path,
    *,
    strict: bool = False,
) -> CatalogHashResult:
    """Validate the current catalog hash against the denominator file.

    Args:
        family: Family name (e.g. "cells").
        catalog: The API catalog dict from DllReflector.
        repo_root: Repository root path.
        strict: If True, raise CatalogHashMismatchError on mismatch.

    Returns:
        CatalogHashResult with match status and hashes.
    """
    current_hash = compute_catalog_hash(catalog)
    denom_path = repo_root / "pipeline" / "configs" / "denominators" / f"{family}.json"

    if not denom_path.exists():
        logger.info(
            "No denominator file for %s — catalog hash check skipped",
            family,
        )
        return CatalogHashResult(
            family=family,
            match=None,
            current_hash=current_hash,
            denominator_hash=None,
            denominator_path=None,
        )

    denom = json.loads(denom_path.read_text(encoding="utf-8"))
    denom_hash = denom.get("api_catalog_sha256")

    if not denom_hash:
        logger.info(
            "Denominator for %s has no api_catalog_sha256 — check skipped",
            family,
        )
        return CatalogHashResult(
            family=family,
            match=None,
            current_hash=current_hash,
            denominator_hash=None,
            denominator_path=str(denom_path),
        )

    is_match = current_hash == denom_hash

    if is_match:
        logger.info("Catalog hash for %s matches denominator", family)
    else:
        msg = (
            f"Catalog hash MISMATCH for {family}: "
            f"current={current_hash[:16]}... "
            f"denominator={denom_hash[:16]}... "
            f"The API catalog has changed since the denominator was created."
        )
        if strict:
            raise CatalogHashMismatchError(msg)
        logger.warning(msg)

    return CatalogHashResult(
        family=family,
        match=is_match,
        current_hash=current_hash,
        denominator_hash=denom_hash,
        denominator_path=str(denom_path),
    )


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
    preferred_method: str | None = None,
) -> Scenario:
    """Build a scenario for a single type.

    Args:
        preferred_method: When set, this method is placed FIRST in target_methods
            so the LLM demonstrates it as the primary operation.
    """
    full_name = type_info["full_name"]
    name = type_info["name"]
    methods = type_info.get("methods", [])

    # Determine required symbols — deduplicate method names (multiple overloads
    # map to a single representative entry; the LLM will pick the simplest overload).
    # Factory methods (Create/CreateXxx) are moved to the END so the LLM picks
    # the primary OPERATION method first.
    required_symbols = [full_name]
    operation_methods: list[str] = []
    factory_methods: list[str] = []
    seen_methods: set[str] = set()
    for m in methods:
        if not m.get("is_obsolete", False):
            method_name = m["name"]
            required_symbols.append(f"{full_name}.{method_name}")
            if method_name not in seen_methods:
                seen_methods.add(method_name)
                if method_name == "Create" or method_name.startswith("Create"):
                    factory_methods.append(method_name)
                else:
                    operation_methods.append(method_name)

    # Operation methods first, factory/Create methods last
    target_methods = operation_methods + factory_methods

    # If a preferred method is specified, move it to position 0
    if preferred_method and preferred_method in target_methods:
        target_methods = [preferred_method] + [m for m in target_methods if m != preferred_method]

    # Generate slug
    slug = _to_slug(name)
    scenario_id = f"{family}-{slug}"

    # Determine if fixtures are needed (heuristic: if method has file-like params)
    needs_fixture = _needs_fixture(methods)
    required_fixtures = []
    if needs_fixture:
        fixture_name = f"sample-{family}{default_fixture_extension}"
        required_fixtures = [fixture_name]

    # Infer the correct input format for this specific scenario.
    # allow_legacy_format_inference=False: if contract not found, use family_default (not stale map)
    inferred_input_format = _infer_input_format(
        name, default_fixture_extension, family=family, allow_legacy_format_inference=False
    )

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
        # PDF types use instance-method IPlugin pattern — Process(XxxOptions) takes an
        # options object, not a raw file path. _needs_fixture() returns False because
        # the method signature has no string/Stream file-path parameter. However, the
        # options object requires an input PDF to be created programmatically first.
        input_strategy = "programmatic_input" if family == "pdf" else "none"

    # Build output and validation plans.
    # allow_legacy_format_inference=False: if contract not found, use family_default (not stale map)
    inferred_output_format = _infer_output_format(
        name, family_default=default_fixture_extension, family=family, allow_legacy_format_inference=False
    )
    output_plan = f"Convert input{inferred_input_format} to output{inferred_output_format} using {name}"
    validation_plan = f"Build succeeds, runs without exception, produces output{inferred_output_format}"

    # Attach FormatContract metadata if available
    contract_output = ""
    contract_id = ""
    contract_hash = ""
    try:
        from plugin_examples.format_authority.store import get_contract

        contract = get_contract(family, name)
        contract_output = contract.canonical_output_format
        contract_id = contract.contract_id
        contract_hash = contract.contract_hash
    except ImportError:
        pass
    # NOTE: MissingFormatContractError (subclass of KeyError) is intentionally NOT caught here.
    # A missing contract must propagate so the caller can handle it explicitly.

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
        required_output_contract=contract_output,
        format_contract_id=contract_id,
        format_contract_hash=contract_hash,
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
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", name)
    return s.lower()


# ---------------------------------------------------------------------------
# Input format inference — scenario-specific mapping
# ---------------------------------------------------------------------------

# Map workflow-root type name patterns to their correct input format.
# Key = lowercased type name (without namespace), Value = input extension.
# Converters that IMPORT a format use that format as input.
# Converters that EXPORT to a format use the family default as input.
_INPUT_FORMAT_MAP: dict[str, str] = {
    # Cells types
    "textconverter": ".csv",  # TextConverter processes text-based formats only
    "jsonconverter": ".xlsx",  # JsonConverter exports spreadsheet to JSON
    "htmlconverter": ".xlsx",  # HtmlConverter exports spreadsheet to HTML
    "cells:pdfconverter": ".xlsx",  # Cells PdfConverter exports spreadsheet to PDF
    "imageconverter": ".xlsx",  # ImageConverter renders spreadsheet to image
    "spreadsheetconverter": ".xlsx",  # Converts between spreadsheet formats
    "spreadsheetmerger": ".xlsx",  # Merges multiple spreadsheets
    "spreadsheetsplitter": ".xlsx",  # Splits spreadsheet into sheets
    "spreadsheetlocker": ".xlsx",  # Locks/protects a spreadsheet
    # Words types — use family-scoped keys for names shared with other families
    "words:converter": ".docx",
    "watermarker": ".docx",
    "replacer": ".docx",
    "comparer": ".docx",
    "mailmerger": ".docx",
    "reportbuilder": ".docx",
    "processor": ".docx",
    "signer": ".docx",
    # Diagram types — both take Visio input (.vsdx)
    "diagramconverter": ".vsdx",
    "diagram:pdfconverter": ".vsdx",
    # Slides types — use family-scoped keys for shared names
    "slides:convert": ".pptx",
    "slides:merger": ".pptx",
    "slides:compress": ".pptx",
    "slides:foreach": ".pptx",
    "slides:collect": ".pptx",
    # PDF types — Html takes HTML input, not PDF
    "pdf:html": ".html",
    # Email types
    "email:converter": ".eml",
}


def _infer_input_format(
    type_name: str,
    family_default: str,
    family: str = "",
    *,
    allow_legacy_format_inference: bool = True,
) -> str:
    """Infer the correct input format for a scenario based on type name.

    Priority:
    1. FormatContract (API-backed authority) — if available
    2. Legacy _INPUT_FORMAT_MAP (deprecated; only if allow_legacy_format_inference=True)
    3. family_default fallback
    """
    # Priority 1: FormatContract authority
    if family:
        try:
            from plugin_examples.format_authority.store import get_contract

            contract = get_contract(family, type_name)
            return contract.input_format
        except ImportError:
            pass
        # NOTE: MissingFormatContractError (KeyError subclass) is NOT caught here — fail closed.

    if not allow_legacy_format_inference:
        return family_default

    # Priority 2: Legacy map (deprecated — compatibility only)
    key = type_name.lower()
    if family:
        scoped = f"{family}:{key}"
        if scoped in _INPUT_FORMAT_MAP:
            logger.debug("DEPRECATED: _INPUT_FORMAT_MAP used for %s/%s input", family, type_name)
            return _INPUT_FORMAT_MAP[scoped]
    result = _INPUT_FORMAT_MAP.get(key)
    if result is not None:
        logger.debug("DEPRECATED: _INPUT_FORMAT_MAP used for %s input", type_name)
        return result
    return family_default


def _infer_output_format(
    type_name: str,
    family_default: str = ".out",
    family: str = "",
    *,
    allow_legacy_format_inference: bool = True,
) -> str:
    """Infer the output format from the type name.

    Priority:
    1. FormatContract (API-backed authority) — if available
    2. Legacy _map (deprecated; only if allow_legacy_format_inference=True)
    3. family_default fallback
    """
    # Priority 1: FormatContract authority
    if family:
        try:
            from plugin_examples.format_authority.store import get_contract

            contract = get_contract(family, type_name)
            return contract.canonical_output_format
        except ImportError:
            pass
        # NOTE: MissingFormatContractError (KeyError subclass) is NOT caught here — fail closed.

    if not allow_legacy_format_inference:
        return family_default

    # Priority 2: Legacy map (deprecated — compatibility only)
    name_lower = type_name.lower()
    _map = {
        # Cells types
        "textconverter": ".txt",
        "jsonconverter": ".json",
        "htmlconverter": ".html",
        "imageconverter": ".png",
        "spreadsheetconverter": ".xlsx",
        "spreadsheetmerger": ".xlsx",
        "spreadsheetsplitter": ".xlsx",
        "spreadsheetlocker": ".xlsx",
        "spreadsheetcompressor": ".xlsx",
        # Words types — Converter outputs PDF as canonical cross-format demo.
        "converter": ".pdf",
        "watermarker": ".docx",
        "replacer": ".docx",
        "comparer": ".docx",
        "mailmerger": ".docx",
        "reportbuilder": ".docx",
        "processor": ".docx",
        "signer": ".docx",
        "words:merger": ".docx",
        "words:splitter": ".docx",
        # PDF types — complete coverage for all 19 types
        "textextractor": "",
        "docconverter": ".docx",
        "xlsconverter": ".xlsx",
        "pdf:html": ".pdf",
        "jpeg": ".jpg",
        "png": ".png",
        "tiff": ".tiff",
        "pdf:merger": ".pdf",
        "pdf:splitter": ".pdf",
        "optimizer": ".pdf",
        "pdfaconverter": ".pdf",
        "tocgenerator": ".pdf",
        "tablegenerator": ".pdf",
        "imageextractor": ".png",
        "security": ".pdf",
        "formflattener": ".pdf",
        "formeditor": ".pdf",
        "formexporter": ".xml",
        "signature": ".pdf",
        # Diagram types
        "diagramconverter": ".vdx",
        "pdfconverter": ".pdf",  # Both Cells and Diagram PdfConverter output PDF
        "diagram:pdfconverter": ".pdf",
        "diagram:merger": ".vsdx",
        # Slides types — use scoped keys for shared names
        "slides:convert": ".pdf",
        "slides:merger": ".pptx",
        "slides:compress": ".pptx",
        # Email types — Converter uses FolderOutputHandler
        "email:converter": ".eml",
    }
    if family:
        scoped = f"{family}:{name_lower}"
        if scoped in _map:
            return _map[scoped]
    return _map.get(name_lower, family_default)


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


def build_fixture_resolution_evidence(
    planning_result: PlanningResult,
    family_config: dict | None = None,
) -> dict:
    """Build fixture resolution evidence for all planned scenarios.

    This produces a summary of how each scenario's fixture needs would be resolved
    (real fetch, synthetic fallback, generated, programmatic, etc.). It does NOT
    perform actual downloads — that is the runner's responsibility.

    Args:
        planning_result: Result from ``plan_scenarios()``.
        family_config: Optional family YAML config dict (for repo info).

    Returns:
        Dict suitable for writing as ``scenario-fixture-resolution.json``.
    """
    from datetime import datetime, timezone

    repo_configured = False
    repo_info = None
    if family_config:
        github = family_config.get("github", {})
        repo_info = github.get("official_examples_repo")
        repo_configured = bool(repo_info and repo_info.get("owner") and repo_info.get("repo"))

    scenarios = []
    for s in planning_result.ready_scenarios + planning_result.blocked_scenarios:
        entry: dict = {
            "scenario_id": s.scenario_id,
            "status": s.status,
            "input_strategy": s.input_strategy,
            "required_fixtures": s.required_fixtures,
            "fixture_strategy": s.fixture_strategy or s.input_strategy,
        }
        if s.input_strategy == "existing_fixture":
            entry["resolution"] = "registry_match"
        elif s.input_strategy == "generated_fixture_file":
            entry["resolution"] = "pipeline_generated"
        elif s.input_strategy == "programmatic_input":
            entry["resolution"] = "code_generated"
        elif s.input_strategy == "no_valid_input_strategy":
            entry["resolution"] = "blocked"
            entry["blocker_class"] = "FIXTURE_BLOCKED"
        else:
            entry["resolution"] = "none_required"
        scenarios.append(entry)

    return {
        "family": planning_result.family,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "repo_configured": repo_configured,
        "repo_info": {
            "owner": repo_info.get("owner", "") if repo_info else "",
            "repo": repo_info.get("repo", "") if repo_info else "",
        }
        if repo_info
        else None,
        "total_scenarios": len(scenarios),
        "fixture_blocked_count": sum(1 for s in scenarios if s.get("blocker_class") == "FIXTURE_BLOCKED"),
        "scenarios": scenarios,
    }
