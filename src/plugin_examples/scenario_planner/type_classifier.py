"""Classify reflected plugin types into roles for scenario planning."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Canonical type roles
WORKFLOW_ROOT = "workflow_root"
OPERATION_FACADE = "operation_facade"
OPTIONS = "options"
PROVIDER_CALLBACK = "provider_callback"
EVENT_CALLBACK = "event_callback"
RESULT_MODEL = "result_model"
SETTINGS_MODEL = "settings_model"
ENUM = "enum"
UTILITY = "utility"
ABSTRACT_BASE = "abstract_base"
INTERFACE_CONTRACT = "interface_contract"
UNKNOWN = "unknown"

# Roles that may be generated as standalone examples
STANDALONE_ROLES = frozenset({WORKFLOW_ROOT, OPERATION_FACADE})

# Roles that may NOT be standalone example roots
NON_STANDALONE_ROLES = frozenset({
    OPTIONS, PROVIDER_CALLBACK, EVENT_CALLBACK, RESULT_MODEL,
    SETTINGS_MODEL, ENUM, UTILITY, ABSTRACT_BASE, INTERFACE_CONTRACT, UNKNOWN,
})

# Workflow verb patterns (types with these in their name are candidate roots)
_WORKFLOW_VERBS = re.compile(
    r"(Converter|Merger|Splitter|Locker|Unlocker|Processor|Replacer|"
    r"Assembler|Protector|Saver|Compressor|Signer|Extractor|Generator|"
    r"Renderer|Exporter|Importer)$",
    re.IGNORECASE,
)

# Callback/provider patterns — match at end OR followed by "Of" (compound names)
_CALLBACK_PATTERNS = re.compile(
    r"(Provider|Callback|Handler|EventArgs|OptionsProvider|Listener|Observer)($|Of[A-Z])",
    re.IGNORECASE,
)


@dataclass
class TypeRole:
    """Classification of a single reflected type."""
    full_name: str
    name: str
    role: str
    confidence: float  # 0.0–1.0
    reason: str
    has_static_methods: bool = False
    has_instance_methods: bool = False
    has_constructors: bool = False
    method_count: int = 0


def classify_type(type_info: dict) -> TypeRole:
    """Classify a single type into a role.

    Args:
        type_info: Type dict from the reflected API catalog.

    Returns:
        TypeRole with classification.
    """
    name = type_info.get("name", "")
    full_name = type_info.get("full_name", "")
    kind = type_info.get("kind", "class")
    methods = type_info.get("methods", [])
    constructors = type_info.get("constructors", [])
    properties = type_info.get("properties", [])

    has_static = any(m.get("is_static") for m in methods)
    has_instance = any(not m.get("is_static") for m in methods)
    has_ctors = len(constructors) > 0
    method_count = len(methods)

    base = dict(
        full_name=full_name, name=name,
        has_static_methods=has_static, has_instance_methods=has_instance,
        has_constructors=has_ctors, method_count=method_count,
    )

    # Enum
    if kind == "enum":
        return TypeRole(**base, role=ENUM, confidence=1.0, reason="Enum type")

    # Interface
    if kind == "interface":
        return TypeRole(**base, role=INTERFACE_CONTRACT, confidence=1.0,
                        reason="Interface type")

    # Abstract class
    if kind == "abstract_class" or name.startswith("Abstract"):
        return TypeRole(**base, role=ABSTRACT_BASE, confidence=1.0,
                        reason="Abstract class")

    # Provider/callback patterns
    if _CALLBACK_PATTERNS.search(name):
        return TypeRole(**base, role=PROVIDER_CALLBACK, confidence=0.95,
                        reason=f"Name matches callback/provider pattern: {name}")

    # Options types
    if name.endswith("Options") or name.endswith("Option"):
        return TypeRole(**base, role=OPTIONS, confidence=0.9,
                        reason=f"Name ends with Options: {name}")

    # Result/Info models
    if name.endswith("Result") or name.endswith("Info"):
        return TypeRole(**base, role=RESULT_MODEL, confidence=0.9,
                        reason=f"Name ends with Result/Info: {name}")

    # Settings models
    if name.endswith("Settings") or name.endswith("Config"):
        return TypeRole(**base, role=SETTINGS_MODEL, confidence=0.85,
                        reason=f"Name ends with Settings/Config: {name}")

    # SaveOptions types (specific to Aspose — have SaveOptions in name, but not Providers)
    if "SaveOptions" in name and not _WORKFLOW_VERBS.search(name) and "Provider" not in name:
        return TypeRole(**base, role=OPTIONS, confidence=0.9,
                        reason=f"SaveOptions type: {name}")

    # LoadOptions types
    if "LoadOptions" in name:
        return TypeRole(**base, role=OPTIONS, confidence=0.9,
                        reason=f"LoadOptions type: {name}")

    # Workflow root: static methods + workflow verb
    if _WORKFLOW_VERBS.search(name) and has_static and method_count > 0:
        return TypeRole(**base, role=WORKFLOW_ROOT, confidence=0.95,
                        reason=f"Workflow verb + static methods: {name}")

    # Operation facade: workflow verb + instance methods
    if _WORKFLOW_VERBS.search(name) and has_instance and method_count > 0:
        return TypeRole(**base, role=OPERATION_FACADE, confidence=0.85,
                        reason=f"Workflow verb + instance methods: {name}")

    # Workflow root: any type with static public methods that isn't options/callback
    if has_static and method_count > 0:
        return TypeRole(**base, role=WORKFLOW_ROOT, confidence=0.7,
                        reason=f"Has static methods, no special suffix: {name}")

    # No methods at all
    if method_count == 0:
        if len(properties) > 0:
            return TypeRole(**base, role=SETTINGS_MODEL, confidence=0.6,
                            reason=f"No methods, has properties: {name}")
        return TypeRole(**base, role=UNKNOWN, confidence=0.3,
                        reason=f"No methods, no properties: {name}")

    # Instance-only with constructors but no workflow verb
    if has_instance and has_ctors and not has_static:
        return TypeRole(**base, role=UTILITY, confidence=0.5,
                        reason=f"Instance methods with constructors, no workflow verb: {name}")

    return TypeRole(**base, role=UNKNOWN, confidence=0.3,
                    reason=f"Could not classify: {name}")


def classify_catalog(catalog: dict, plugin_namespaces: list[str]) -> list[TypeRole]:
    """Classify all plugin types in the catalog.

    Args:
        catalog: Full API catalog dict.
        plugin_namespaces: List of matched plugin namespace names.

    Returns:
        List of TypeRole classifications.
    """
    roles = []
    for ns in catalog.get("namespaces", []):
        if ns.get("namespace", "") not in plugin_namespaces:
            continue
        for type_info in ns.get("types", []):
            roles.append(classify_type(type_info))
    return roles


def write_type_role_classification(
    roles: list[TypeRole],
    verification_dir: Path,
) -> Path:
    """Write type role classification evidence."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "plugin-type-role-classification.json"

    summary = {}
    for r in roles:
        summary.setdefault(r.role, []).append(r.name)

    data = {
        "total_types": len(roles),
        "role_summary": {role: len(names) for role, names in summary.items()},
        "types": [
            {
                "full_name": r.full_name,
                "name": r.name,
                "role": r.role,
                "confidence": r.confidence,
                "reason": r.reason,
                "has_static_methods": r.has_static_methods,
                "has_instance_methods": r.has_instance_methods,
                "has_constructors": r.has_constructors,
                "method_count": r.method_count,
            }
            for r in roles
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Type role classification written: %s", path)
    return path
