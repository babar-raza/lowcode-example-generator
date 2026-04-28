"""Compute API delta between two catalog versions."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TypeDelta:
    """Change record for a single type."""
    full_name: str
    namespace: str
    change_type: str  # added, removed, modified
    added_methods: list[str] = field(default_factory=list)
    removed_methods: list[str] = field(default_factory=list)
    added_properties: list[str] = field(default_factory=list)
    removed_properties: list[str] = field(default_factory=list)


@dataclass
class DeltaResult:
    """Result of API delta computation."""
    initial_run: bool
    old_version: str | None
    new_version: str
    added_types: list[TypeDelta] = field(default_factory=list)
    removed_types: list[TypeDelta] = field(default_factory=list)
    modified_types: list[TypeDelta] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added_types or self.removed_types or self.modified_types)

    @property
    def total_changes(self) -> int:
        return len(self.added_types) + len(self.removed_types) + len(self.modified_types)


def compute_delta(
    new_catalog: dict,
    old_catalog: dict | None = None,
) -> DeltaResult:
    """Compute delta between two API catalogs.

    Args:
        new_catalog: Current API catalog.
        old_catalog: Previous API catalog (None for initial run).

    Returns:
        DeltaResult with added/removed/modified types.
    """
    new_version = new_catalog.get("assembly_version", "unknown")

    if old_catalog is None:
        # Initial run — everything is new
        result = DeltaResult(
            initial_run=True,
            old_version=None,
            new_version=new_version,
        )
        for ns in new_catalog.get("namespaces", []):
            for t in ns.get("types", []):
                result.added_types.append(TypeDelta(
                    full_name=t["full_name"],
                    namespace=ns["namespace"],
                    change_type="added",
                    added_methods=[m["name"] for m in t.get("methods", [])],
                    added_properties=[p["name"] for p in t.get("properties", [])],
                ))
        logger.info("Initial run delta: %d new types", len(result.added_types))
        return result

    old_version = old_catalog.get("assembly_version", "unknown")
    result = DeltaResult(
        initial_run=False,
        old_version=old_version,
        new_version=new_version,
    )

    old_types = _index_types(old_catalog)
    new_types = _index_types(new_catalog)

    old_names = set(old_types.keys())
    new_names = set(new_types.keys())

    # Added types
    for name in sorted(new_names - old_names):
        t, ns = new_types[name]
        result.added_types.append(TypeDelta(
            full_name=name,
            namespace=ns,
            change_type="added",
            added_methods=[m["name"] for m in t.get("methods", [])],
            added_properties=[p["name"] for p in t.get("properties", [])],
        ))

    # Removed types
    for name in sorted(old_names - new_names):
        t, ns = old_types[name]
        result.removed_types.append(TypeDelta(
            full_name=name,
            namespace=ns,
            change_type="removed",
            removed_methods=[m["name"] for m in t.get("methods", [])],
            removed_properties=[p["name"] for p in t.get("properties", [])],
        ))

    # Modified types
    for name in sorted(old_names & new_names):
        old_t, old_ns = old_types[name]
        new_t, new_ns = new_types[name]
        delta = _diff_type(name, old_ns, old_t, new_t)
        if delta:
            result.modified_types.append(delta)

    logger.info(
        "Delta: %d added, %d removed, %d modified (v%s -> v%s)",
        len(result.added_types), len(result.removed_types),
        len(result.modified_types), old_version, new_version,
    )
    return result


def write_delta_report(
    delta: DeltaResult,
    verification_dir: Path,
) -> Path:
    """Write API delta report to verification directory."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "api-delta-report.json"

    report = {
        "initial_run": delta.initial_run,
        "old_version": delta.old_version,
        "new_version": delta.new_version,
        "summary": {
            "added_types": len(delta.added_types),
            "removed_types": len(delta.removed_types),
            "modified_types": len(delta.modified_types),
            "total_changes": delta.total_changes,
        },
        "added_types": [_type_delta_to_dict(t) for t in delta.added_types],
        "removed_types": [_type_delta_to_dict(t) for t in delta.removed_types],
        "modified_types": [_type_delta_to_dict(t) for t in delta.modified_types],
    }

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Delta report written: %s", path)
    return path


def _index_types(catalog: dict) -> dict[str, tuple[dict, str]]:
    """Index types by full_name -> (type_dict, namespace)."""
    index: dict[str, tuple[dict, str]] = {}
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            index[t["full_name"]] = (t, ns["namespace"])
    return index


def _diff_type(name: str, namespace: str, old_t: dict, new_t: dict) -> TypeDelta | None:
    """Compute diff between old and new versions of a type."""
    old_methods = {m["name"] for m in old_t.get("methods", [])}
    new_methods = {m["name"] for m in new_t.get("methods", [])}
    old_props = {p["name"] for p in old_t.get("properties", [])}
    new_props = {p["name"] for p in new_t.get("properties", [])}

    added_m = sorted(new_methods - old_methods)
    removed_m = sorted(old_methods - new_methods)
    added_p = sorted(new_props - old_props)
    removed_p = sorted(old_props - new_props)

    if not any([added_m, removed_m, added_p, removed_p]):
        return None

    return TypeDelta(
        full_name=name,
        namespace=namespace,
        change_type="modified",
        added_methods=added_m,
        removed_methods=removed_m,
        added_properties=added_p,
        removed_properties=removed_p,
    )


def _type_delta_to_dict(td: TypeDelta) -> dict:
    return {
        "full_name": td.full_name,
        "namespace": td.namespace,
        "change_type": td.change_type,
        "added_methods": td.added_methods,
        "removed_methods": td.removed_methods,
        "added_properties": td.added_properties,
        "removed_properties": td.removed_properties,
    }
