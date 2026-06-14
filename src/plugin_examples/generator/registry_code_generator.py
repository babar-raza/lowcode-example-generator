"""Generate C# example code from capability registry selected_api_mapping.

Non-LowCode families use PROBE_CONFIRMED registry entries instead of
DllReflector catalogs. This module renders minimal-but-valid C# code
from the registry's ``selected_api_mapping`` fields.
"""

from __future__ import annotations

import logging

from plugin_examples.generator.code_generator import GeneratedExample
from plugin_examples.scenario_planner.planner import Scenario

logger = logging.getLogger(__name__)


def generate_code_from_registry(
    scenario: Scenario,
    registry_entry: dict,
    package_id: str,
) -> GeneratedExample:
    """Generate a C# example from a registry entry's selected_api_mapping.

    Uses the probe-confirmed API mapping to render a minimal console app
    that exercises the documented API surface.

    Args:
        scenario: Planned scenario from ``plan_scenarios_from_registry``.
        registry_entry: Registry entry dict with ``selected_api_mapping``.
        package_id: NuGet package ID (e.g. ``Aspose.BarCode``).

    Returns:
        GeneratedExample compatible with ``generate_project()``.
    """
    api_mapping = registry_entry.get("selected_api_mapping") or {}
    namespace = api_mapping.get("namespace") or registry_entry.get("namespace", "")
    type_name = api_mapping.get("type_name") or registry_entry.get("type_name", "")
    method_name = api_mapping.get("method_name") or registry_entry.get("method_name", "")
    constructor = api_mapping.get("constructor", "")
    output_format = (
        api_mapping.get("output_format")
        or api_mapping.get("output_format_enum")
        or ""
    )
    operation_kind = registry_entry.get("operation_kind", "")

    # Build constructor call
    ctor_call = _render_constructor(type_name, constructor, operation_kind)

    # Build method call
    method_call = _render_method_call(method_name, output_format)

    code = _CS_TEMPLATE.format(
        namespace=namespace,
        type_name=type_name,
        ctor_call=ctor_call,
        method_call=method_call,
        scenario_id=scenario.scenario_id,
    )

    logger.info(
        "Registry code generated for %s (type=%s.%s, method=%s)",
        scenario.scenario_id,
        namespace,
        type_name,
        method_name,
    )

    return GeneratedExample(
        scenario_id=scenario.scenario_id,
        code=code,
        claimed_symbols=[f"{namespace}.{type_name}", f"{namespace}.{type_name}.{method_name}"],
        status="generated",
        generation_strategy="registry_template",
    )


def _render_constructor(type_name: str, constructor: str, operation_kind: str) -> str:
    """Render the constructor call from registry hints."""
    if not constructor:
        return f"new {type_name}()"

    # Parse constructor hint like "BarcodeGenerator(EncodeTypes, string)"
    # or "BarCodeReader(string filePath, DecodeType)"
    paren_idx = constructor.find("(")
    if paren_idx == -1:
        return f"new {type_name}()"

    params_str = constructor[paren_idx + 1 : -1].strip() if constructor.endswith(")") else ""
    if not params_str:
        return f"new {type_name}()"

    params = [p.strip() for p in params_str.split(",")]
    args = []
    for param in params:
        parts = param.split()
        param_type = parts[0] if parts else param
        args.append(_default_value_for_type(param_type, operation_kind))

    return f"new {type_name}({', '.join(args)})"


def _default_value_for_type(param_type: str, operation_kind: str) -> str:
    """Generate a sensible default value for a constructor parameter type."""
    pt = param_type.lower().rstrip(",")
    if pt in ("string", "system.string"):
        if "generation" in operation_kind.lower() or "write" in operation_kind.lower():
            return '"Sample text content"'
        return '"input.bin"'
    if pt in ("stream", "system.io.stream"):
        return "Stream.Null"
    if "encodetypes" in pt or "encodetype" in pt:
        return "EncodeTypes.Code128"
    if "decodetype" in pt or "decodetypes" in pt:
        return "DecodeType.AllSupportedTypes"
    if pt in ("int", "int32", "system.int32"):
        return "0"
    if pt in ("bool", "boolean", "system.boolean"):
        return "false"
    return f"default /* {param_type} */"


def _render_method_call(method_name: str, output_format: str) -> str:
    """Render the primary method call."""
    if not method_name:
        return "// No method specified in registry"

    if output_format and "format" in output_format.lower():
        return f'obj.{method_name}("output.bin", {output_format}.Png)'
    if method_name.lower() == "save":
        return f'obj.{method_name}("output.bin")'
    if method_name.lower() in ("readbarcodes", "read"):
        return f"var results = obj.{method_name}();"
    return f'obj.{method_name}("output.bin")'


_CS_TEMPLATE = """\
// Auto-generated from capability registry — TEMPLATE_REGISTRY mode
// Scenario: {scenario_id}
using System;
using {namespace};

var outputPath = args.Length > 0 ? args[0] : "output.bin";
var obj = {ctor_call};
{method_call}
Console.WriteLine("Example: {scenario_id}");
"""
