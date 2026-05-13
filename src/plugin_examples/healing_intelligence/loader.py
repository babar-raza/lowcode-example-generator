"""Healing intelligence loader — loads persistent registries from disk.

The healing intelligence registries are committed JSON files under
workspace/verification/latest/healing-intelligence/. This loader makes them
available during:
  - generation (semantic steering constraints)
  - repair (failure patterns to detect known regressions)
  - semantic validation (validator rules)
  - rerun planning (rerun governance)

The registries are loaded lazily and cached in memory for the session lifetime.
All loads are read-only — this module never writes to the registries.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default location relative to the project root.
_DEFAULT_REGISTRY_DIR = Path(
    "workspace/verification/latest/healing-intelligence"
)

_REGISTRY_FILES = {
    "bootstrap": "healing-intelligence-bootstrap.json",
    "failure_patterns": "failure-pattern-registry.json",
    "repair_patterns": "repair-pattern-registry.json",
    "semantic_steering": "semantic-steering-registry.json",
    "validator_patterns": "validator-pattern-registry.json",
}


class HealingIntelligenceLoader:
    """Loads and exposes the persistent healing intelligence registries.

    Usage::

        loader = HealingIntelligenceLoader()
        loader.load()

        # Check if a failure pattern is already known
        known = loader.is_known_failure("missing_namespace_using_directive_textfragment")

        # Get steering constraints for a family/type
        constraints = loader.get_steering_constraints("pdf", "Merger")

        # Get validator rules for a type
        rules = loader.get_validator_rules("pdf", "Merger")
    """

    def __init__(self, registry_dir: Path | str | None = None) -> None:
        self._registry_dir = Path(registry_dir) if registry_dir else _DEFAULT_REGISTRY_DIR
        self._loaded = False
        self._bootstrap: dict[str, Any] = {}
        self._failure_patterns: list[dict] = []
        self._repair_patterns: list[dict] = []
        self._semantic_steering: dict[str, Any] = {}
        self._validator_patterns: list[dict] = []

    # ------------------------------------------------------------------
    # Public loading API
    # ------------------------------------------------------------------

    def load(self) -> "HealingIntelligenceLoader":
        """Load all healing intelligence registries from disk.

        Returns self for chaining. Idempotent — safe to call multiple times.
        Missing files are warned about but do not raise; the loader degrades
        gracefully so that a missing registry does not block a pipeline run.
        """
        if self._loaded:
            return self
        for key, filename in _REGISTRY_FILES.items():
            path = self._registry_dir / filename
            if not path.exists():
                logger.warning(
                    "Healing intelligence registry not found: %s — "
                    "run will proceed without this knowledge layer",
                    path,
                )
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                setattr(self, f"_{key}", data if isinstance(data, (dict, list)) else {})
                logger.debug("Loaded healing intelligence: %s", filename)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to load %s: %s", path, exc)

        # Unpack nested lists from dict registries
        if isinstance(self._failure_patterns, dict):
            self._failure_patterns = self._failure_patterns.get("patterns", [])
        if isinstance(self._repair_patterns, dict):
            self._repair_patterns = self._repair_patterns.get("patterns", [])
        if isinstance(self._validator_patterns, dict):
            self._validator_patterns = self._validator_patterns.get("rules", [])

        self._loaded = True
        return self

    # ------------------------------------------------------------------
    # Registry presence / validity checks
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        """Return True if registries have been loaded."""
        return self._loaded

    def registries_present(self) -> dict[str, bool]:
        """Return a dict indicating which registry files exist on disk."""
        return {
            key: (self._registry_dir / filename).exists()
            for key, filename in _REGISTRY_FILES.items()
        }

    def all_core_registries_present(self) -> bool:
        """Return True if the 4 core registries (not bootstrap) are all on disk."""
        core = {"failure_patterns", "repair_patterns", "semantic_steering", "validator_patterns"}
        presence = self.registries_present()
        return all(presence.get(k, False) for k in core)

    # ------------------------------------------------------------------
    # Failure pattern queries
    # ------------------------------------------------------------------

    def get_failure_patterns(self) -> list[dict]:
        """Return all known failure patterns."""
        return list(self._failure_patterns)

    def get_failure_pattern(self, pattern_id: str) -> dict | None:
        """Return a failure pattern by ID (e.g. 'FP-001')."""
        for p in self._failure_patterns:
            if p.get("id") == pattern_id:
                return p
        return None

    def is_known_failure(self, name: str) -> bool:
        """Return True if a failure with the given name is in the registry."""
        return any(p.get("name") == name for p in self._failure_patterns)

    def get_failures_for_type(self, family: str, type_name: str) -> list[dict]:
        """Return all known failure patterns affecting a specific type."""
        return [
            p for p in self._failure_patterns
            if family in p.get("affected_families", [])
            and type_name in p.get("affected_types", [])
        ]

    # ------------------------------------------------------------------
    # Repair pattern queries
    # ------------------------------------------------------------------

    def get_repair_pattern(self, pattern_id: str) -> dict | None:
        """Return a repair pattern by ID (e.g. 'RP-001')."""
        for p in self._repair_patterns:
            if p.get("id") == pattern_id:
                return p
        return None

    def get_repair_for_failure(self, failure_id: str) -> dict | None:
        """Return the repair strategy that resolves a given failure ID."""
        for p in self._repair_patterns:
            if p.get("resolves_failure") == failure_id:
                return p
        return None

    # ------------------------------------------------------------------
    # Semantic steering queries
    # ------------------------------------------------------------------

    def get_steering_constraints(self, family: str, type_name: str) -> dict:
        """Return REQUIRED and FORBIDDEN constraints for a family/type pair.

        Returns a dict with keys 'required' and 'forbidden' (both lists).
        Returns empty lists if no constraints are defined.
        """
        families = self._semantic_steering.get("families", {})
        family_data = families.get(family, {})
        per_type = family_data.get("per_type", {})
        type_constraints = per_type.get(type_name, {})
        return {
            "required": list(type_constraints.get("required", [])),
            "forbidden": list(type_constraints.get("forbidden", [])),
            "global_required": list(family_data.get("global_required", [])),
            "global_forbidden": list(family_data.get("global_forbidden", [])),
        }

    def get_global_steering(self, family: str) -> dict:
        """Return global REQUIRED and FORBIDDEN constraints for a family."""
        families = self._semantic_steering.get("families", {})
        family_data = families.get(family, {})
        return {
            "global_required": list(family_data.get("global_required", [])),
            "global_forbidden": list(family_data.get("global_forbidden", [])),
        }

    # ------------------------------------------------------------------
    # Validator rule queries
    # ------------------------------------------------------------------

    def get_validator_rules(self, family: str, type_name: str) -> list[dict]:
        """Return all validator rules that apply to a family/type pair."""
        results = []
        for rule in self._validator_patterns:
            applies_to = rule.get("applies_to", {})
            rule_families = applies_to.get("families", [])
            rule_types = applies_to.get("types", [])
            family_match = rule_families == "all" or family in rule_families
            type_match = rule_types == "all" or type_name in rule_types
            if family_match and type_match:
                results.append(rule)
        return results

    def get_implemented_validator_rules(self) -> list[dict]:
        """Return only validator rules with current_status containing 'IMPLEMENTED'."""
        return [
            r for r in self._validator_patterns
            if "IMPLEMENTED" in r.get("current_status", "")
            and "NOT_IMPLEMENTED" not in r.get("current_status", "")
        ]

    # ------------------------------------------------------------------
    # Summary / diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary of loaded registry counts."""
        return {
            "loaded": self._loaded,
            "registry_dir": str(self._registry_dir),
            "failure_patterns_count": len(self._failure_patterns),
            "repair_patterns_count": len(self._repair_patterns),
            "validator_rules_count": len(self._validator_patterns),
            "families_with_steering": list(
                self._semantic_steering.get("families", {}).keys()
            ),
            "registries_present": self.registries_present(),
        }
