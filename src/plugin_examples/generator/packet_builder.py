"""Build constrained prompt packets for LLM example generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class UnknownSymbolError(Exception):
    """Raised when a scenario references symbols not in the catalog."""


@dataclass
class PromptPacket:
    """Constrained prompt packet for LLM generation."""
    scenario_id: str
    target_type: str
    target_namespace: str
    target_methods: list[str] = field(default_factory=list)
    approved_symbols: list[str] = field(default_factory=list)
    fixture_files: list[str] = field(default_factory=list)
    output_plan: str = ""
    constraints: list[str] = field(default_factory=list)
    system_prompt: str = ""
    user_prompt: str = ""


def build_packet(
    scenario: dict,
    catalog: dict,
    *,
    prompt_template: str | None = None,
) -> PromptPacket:
    """Build a constrained prompt packet from a scenario.

    Validates that all required symbols exist in the catalog before
    allowing LLM generation.

    Args:
        scenario: Scenario dict from scenario catalog.
        catalog: API catalog dict.
        prompt_template: Optional custom prompt template.

    Returns:
        PromptPacket ready for LLM generation.

    Raises:
        UnknownSymbolError: If scenario references unknown symbols.
    """
    catalog_symbols = _build_catalog_symbols(catalog)
    required_symbols = scenario.get("required_symbols", [])

    # Validate all symbols exist
    unknown = [s for s in required_symbols if s not in catalog_symbols]
    if unknown:
        raise UnknownSymbolError(
            f"Scenario {scenario.get('scenario_id')} references unknown symbols: "
            f"{', '.join(unknown)}"
        )

    target_type = scenario.get("target_type", "")
    target_ns = scenario.get("target_namespace", "")
    methods = scenario.get("target_methods", [])

    # Build approved symbol context from catalog
    approved = _get_type_details(catalog, target_type)

    constraints = [
        "Use only symbols from the approved API catalog",
        "Do not use TODO placeholders",
        "Do not use NotImplementedException",
        "Do not hardcode absolute file paths",
        "Use PackageReference without inline version numbers",
        "Create a complete, runnable SDK-style console application",
    ]

    system_prompt = (
        "You are an expert C# developer. Generate a complete, runnable SDK-style "
        "console application example that demonstrates the specified API. "
        "Use only the symbols provided in the API catalog. "
        "The example must compile and run without errors."
    )

    user_prompt = _build_user_prompt(scenario, approved, prompt_template)

    return PromptPacket(
        scenario_id=scenario.get("scenario_id", ""),
        target_type=target_type,
        target_namespace=target_ns,
        target_methods=methods,
        approved_symbols=required_symbols,
        fixture_files=scenario.get("required_fixtures", []),
        output_plan=scenario.get("output_plan", ""),
        constraints=constraints,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def _build_catalog_symbols(catalog: dict) -> set[str]:
    """Build set of all known symbols."""
    symbols: set[str] = set()
    for ns in catalog.get("namespaces", []):
        symbols.add(ns["namespace"])
        for t in ns.get("types", []):
            symbols.add(t["full_name"])
            for m in t.get("methods", []):
                symbols.add(f"{t['full_name']}.{m['name']}")
    return symbols


def _get_type_details(catalog: dict, full_name: str) -> dict:
    """Get detailed type information from catalog."""
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            if t["full_name"] == full_name:
                return t
    return {}


def _build_user_prompt(scenario: dict, type_details: dict, template: str | None) -> str:
    """Build user prompt from scenario and type details."""
    if template:
        return template

    title = scenario.get("title", "")
    target = scenario.get("target_type", "")
    methods = scenario.get("target_methods", [])
    output_plan = scenario.get("output_plan", "")

    prompt_parts = [
        f"Generate a C# console application example: {title}",
        f"\nTarget type: {target}",
        f"Methods to demonstrate: {', '.join(methods)}",
    ]

    if output_plan:
        prompt_parts.append(f"Expected output: {output_plan}")

    if type_details:
        prompt_parts.append(f"\nType details: {type_details.get('name', '')}")
        for m in type_details.get("methods", []):
            params = ", ".join(f"{p['type']} {p['name']}" for p in m.get("parameters", []))
            prompt_parts.append(f"  - {m['name']}({params}) -> {m.get('return_type', 'void')}")

    return "\n".join(prompt_parts)
