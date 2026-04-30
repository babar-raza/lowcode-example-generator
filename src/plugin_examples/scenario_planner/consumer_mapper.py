"""Map consumer relationships between plugin types."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def build_consumer_map(catalog: dict, plugin_namespaces: list[str]) -> dict:
    """Build a consumer relationship map for all plugin types.

    For each type, find which other types' methods accept it as a parameter.

    Args:
        catalog: Full API catalog dict.
        plugin_namespaces: List of matched plugin namespace names.

    Returns:
        Dict mapping full_name -> list of consumer dicts.
    """
    # Collect all plugin type full names
    plugin_types = set()
    for ns in catalog.get("namespaces", []):
        if ns.get("namespace", "") not in plugin_namespaces:
            continue
        for t in ns.get("types", []):
            plugin_types.add(t["full_name"])

    # Build map: type -> list of consumers
    consumer_map: dict[str, list[dict]] = {t: [] for t in plugin_types}

    # Search ALL types (not just plugin) for methods that accept plugin types
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            type_name = t["full_name"]
            # Check methods
            for m in t.get("methods", []):
                for p in m.get("parameters", []):
                    param_type = p.get("type", "")
                    if param_type in consumer_map:
                        consumer_map[param_type].append({
                            "consumer_type": type_name,
                            "consumer_method": m["name"],
                            "parameter_name": p.get("name", ""),
                            "is_static": m.get("is_static", False),
                        })
            # Check constructors
            for ctor in t.get("constructors", []):
                for p in ctor.get("parameters", []):
                    param_type = p.get("type", "")
                    if param_type in consumer_map:
                        consumer_map[param_type].append({
                            "consumer_type": type_name,
                            "consumer_method": ".ctor",
                            "parameter_name": p.get("name", ""),
                            "is_static": False,
                        })

    return consumer_map


def write_consumer_relationships(
    consumer_map: dict,
    verification_dir: Path,
) -> Path:
    """Write consumer relationship evidence."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "api-consumer-relationships.json"

    with_consumers = {k: v for k, v in consumer_map.items() if v}
    without_consumers = {k: v for k, v in consumer_map.items() if not v}

    data = {
        "total_types": len(consumer_map),
        "types_with_consumers": len(with_consumers),
        "types_without_consumers": len(without_consumers),
        "relationships": {
            k: v for k, v in consumer_map.items()
        },
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Consumer relationships written: %s", path)
    return path
