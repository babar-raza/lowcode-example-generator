"""Score candidate scenarios for runnability."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.scenario_planner.type_classifier import (
    STANDALONE_ROLES,
    TypeRole,
)

logger = logging.getLogger(__name__)


@dataclass
class EntrypointScore:
    """Score and explanation for a candidate scenario entrypoint."""
    full_name: str
    name: str
    role: str
    score: float = 0.0
    max_score: float = 0.0
    signals: list[dict] = field(default_factory=list)
    runnable: bool = False
    rejection_reason: str | None = None


def score_entrypoint(
    type_info: dict,
    role: TypeRole,
    consumer_map: dict,
    fixture_available: bool = False,
) -> EntrypointScore:
    """Score a type as a candidate standalone scenario entrypoint.

    Args:
        type_info: Type dict from catalog.
        role: TypeRole classification.
        consumer_map: Consumer relationship map.
        fixture_available: Whether fixtures are available.

    Returns:
        EntrypointScore with detailed signals.
    """
    name = type_info.get("name", "")
    full_name = type_info.get("full_name", "")
    methods = type_info.get("methods", [])
    properties = type_info.get("properties", [])

    result = EntrypointScore(
        full_name=full_name, name=name, role=role.role,
    )

    signals = []

    # --- Positive signals ---

    # Static public method
    static_methods = [m for m in methods if m.get("is_static")]
    if static_methods:
        signals.append({"signal": "has_static_methods", "weight": 3.0,
                        "detail": f"{len(static_methods)} static methods"})

    # Belongs to standalone role
    if role.role in STANDALONE_ROLES:
        signals.append({"signal": "standalone_role", "weight": 3.0,
                        "detail": f"Role: {role.role}"})

    # Has simple string/file parameters
    simple_param_methods = 0
    for m in methods:
        params = m.get("parameters", [])
        if all(_is_simple_param(p) for p in params):
            simple_param_methods += 1
    if simple_param_methods > 0:
        signals.append({"signal": "simple_parameters", "weight": 2.0,
                        "detail": f"{simple_param_methods} methods with simple params"})

    # Has file I/O semantics
    has_file_io = any(
        any(kw in p.get("name", "").lower()
            for kw in ("path", "file", "input", "output", "source", "result"))
        for m in methods for p in m.get("parameters", [])
    )
    if has_file_io:
        signals.append({"signal": "file_io_semantics", "weight": 1.5,
                        "detail": "Methods reference file paths"})

    # XML summary describes action
    has_summary = bool(type_info.get("xml_summary", "").strip())
    if has_summary:
        signals.append({"signal": "has_xml_summary", "weight": 0.5,
                        "detail": "Type has XML documentation"})

    # Fixture available
    if fixture_available:
        signals.append({"signal": "fixture_available", "weight": 1.0,
                        "detail": "Fixture files accessible"})

    # --- Negative signals ---

    # Provider/callback role
    if role.role == "provider_callback":
        signals.append({"signal": "provider_callback_role", "weight": -5.0,
                        "detail": "Provider/callback type — not standalone"})

    if role.role == "event_callback":
        signals.append({"signal": "event_callback_role", "weight": -5.0,
                        "detail": "Event callback type — not standalone"})

    # Interface or abstract
    if role.role in ("interface_contract", "abstract_base"):
        signals.append({"signal": "abstract_or_interface", "weight": -5.0,
                        "detail": "Cannot be instantiated"})

    # Method requires callback context (takes provider/callback params)
    callback_params = 0
    for m in methods:
        for p in m.get("parameters", []):
            ptype = p.get("type", "")
            if any(kw in ptype for kw in ("Provider", "Callback", "Handler", "EventArgs")):
                callback_params += 1
    if callback_params > 0:
        signals.append({"signal": "requires_callback_params", "weight": -2.0,
                        "detail": f"{callback_params} parameters are callback types"})

    # Complex object parameters without construction path
    complex_params = 0
    for m in methods:
        for p in m.get("parameters", []):
            if not _is_simple_param(p) and not _is_callback_param(p):
                complex_params += 1
    if complex_params > 0:
        signals.append({"signal": "complex_parameters", "weight": -1.0,
                        "detail": f"{complex_params} complex object parameters"})

    # No methods
    if not methods:
        signals.append({"signal": "no_methods", "weight": -3.0,
                        "detail": "No public methods"})

    # Compute score
    total_positive = sum(s["weight"] for s in signals if s["weight"] > 0)
    total_negative = sum(abs(s["weight"]) for s in signals if s["weight"] < 0)
    net_score = sum(s["weight"] for s in signals)

    result.signals = signals
    result.score = net_score
    result.max_score = total_positive

    # Determine runnability
    if role.role not in STANDALONE_ROLES:
        result.runnable = False
        result.rejection_reason = f"Role '{role.role}' is not a standalone entrypoint"
    elif net_score < 0:
        result.runnable = False
        result.rejection_reason = f"Net score {net_score:.1f} is negative"
    elif not methods:
        result.runnable = False
        result.rejection_reason = "No public methods to demonstrate"
    else:
        result.runnable = True

    return result


def write_entrypoint_scores(
    scores: list[EntrypointScore],
    verification_dir: Path,
) -> Path:
    """Write runnable entrypoint scores evidence."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "runnable-entrypoint-scores.json"

    runnable = [s for s in scores if s.runnable]
    rejected = [s for s in scores if not s.runnable]

    data = {
        "total_scored": len(scores),
        "runnable_count": len(runnable),
        "rejected_count": len(rejected),
        "scores": [
            {
                "full_name": s.full_name,
                "name": s.name,
                "role": s.role,
                "score": s.score,
                "max_score": s.max_score,
                "runnable": s.runnable,
                "rejection_reason": s.rejection_reason,
                "signals": s.signals,
            }
            for s in scores
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Entrypoint scores written: %s", path)
    return path


def _is_simple_param(param: dict) -> bool:
    """Check if a parameter is simple (string, int, bool, enum, stream)."""
    ptype = param.get("type", "")
    simple_types = {
        "System.String", "String", "System.Int32", "System.Int64",
        "System.Boolean", "System.IO.Stream", "Stream",
        "System.String[]", "String[]",
    }
    return ptype in simple_types


def _is_callback_param(param: dict) -> bool:
    """Check if a parameter is a callback/provider type."""
    ptype = param.get("type", "")
    return any(kw in ptype for kw in ("Provider", "Callback", "Handler", "EventArgs"))
