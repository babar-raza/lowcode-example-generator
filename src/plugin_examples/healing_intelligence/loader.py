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
from datetime import UTC
from pathlib import Path
from typing import Any

from plugin_examples.observability import get_logger

logger = get_logger(__name__)

# Default location relative to the project root.
_DEFAULT_REGISTRY_DIR = Path("workspace/verification/latest/healing-intelligence")

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

    def load(self) -> HealingIntelligenceLoader:
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
                    "Healing intelligence registry not found: %s — " "run will proceed without this knowledge layer",
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
        return {key: (self._registry_dir / filename).exists() for key, filename in _REGISTRY_FILES.items()}

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
            p
            for p in self._failure_patterns
            if family in p.get("affected_families", []) and type_name in p.get("affected_types", [])
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
            r
            for r in self._validator_patterns
            if "IMPLEMENTED" in r.get("current_status", "") and "NOT_IMPLEMENTED" not in r.get("current_status", "")
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
            "families_with_steering": list(self._semantic_steering.get("families", {}).keys()),
            "registries_present": self.registries_present(),
        }

    def find_confirmed_repair(self, failure_reason: str) -> dict | None:
        """Return a CONFIRMED repair pattern matching the failure reason, or None.

        Only CONFIRMED repairs trigger the repair loop (not CANDIDATE).
        """
        sig = _normalize_reason(failure_reason)
        for p in self._repair_patterns:
            if p.get("status") != "CONFIRMED":
                continue
            pattern_sig = _normalize_reason(p.get("failure_reason", "") or p.get("name", ""))
            if pattern_sig and sig and pattern_sig in sig:
                return p
        return None


def _normalize_reason(reason: str) -> str:
    """Normalize a failure reason string to a stable signature for matching."""
    if not reason:
        return ""
    import re

    # Lower-case, collapse whitespace, strip punctuation
    normalized = reason.lower().strip()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def auto_learn_from_run(
    run_dir: Path,
    family: str,
    registry_path: Path,
) -> dict:
    """Additive-only: append new CANDIDATE failure patterns from a run; increment occurrences.

    Design constraints:
    - NEVER auto-promotes CANDIDATE to CONFIRMED.
    - NEVER modifies or deletes existing CONFIRMED entries.
    - Additive only — only appends new entries or increments counters.
    - Writes updated failure-pattern-registry.json and auto-learned-patterns.json.

    Args:
        run_dir:       Directory of the completed pipeline run.
        family:        Family name for context.
        registry_path: Path to failure-pattern-registry.json.

    Returns:
        dict with ``added``, ``incremented``, ``skipped`` counts.
    """
    from datetime import datetime, timezone

    def _utcnow() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    # Load existing registry
    if registry_path.exists():
        try:
            raw = json.loads(registry_path.read_text(encoding="utf-8"))
            patterns: list[dict] = raw.get("patterns", []) if isinstance(raw, dict) else raw
        except Exception:  # noqa: BLE001
            patterns = []
    else:
        patterns = []

    # Load failures from run directory
    failures = _load_run_failures(run_dir)
    if not failures:
        return {"added": 0, "incremented": 0, "skipped": 0}

    added = 0
    incremented = 0
    skipped = 0
    auto_learned: list[dict] = []

    for failure in failures:
        sig = _normalize_reason(failure.get("failure_reason", "") or failure.get("reason", ""))
        if not sig:
            skipped += 1
            continue

        existing = _find_by_sig(patterns, sig)
        if existing is None:
            # New pattern — add as CANDIDATE only
            new_entry: dict = {
                "reason_signature": sig,
                "family": family,
                "scenario_id": failure.get("scenario_id"),
                "first_seen": _utcnow(),
                "last_seen": _utcnow(),
                "occurrence_count": 1,
                "status": "CANDIDATE",
                "repair_hint": None,
            }
            patterns.append(new_entry)
            auto_learned.append({"action": "added", "sig": sig, "family": family})
            added += 1
        else:
            # Existing entry — increment occurrence_count only; NEVER change status
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            existing["last_seen"] = _utcnow()
            auto_learned.append({"action": "incremented", "sig": sig, "count": existing["occurrence_count"]})
            incremented += 1

    # Persist updated registry
    if added or incremented:
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            json.dumps({"patterns": patterns}, indent=2),
            encoding="utf-8",
        )
        # Write auto-learned-patterns.json evidence sidecar
        evidence_path = run_dir / "auto-learned-patterns.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "family": family,
                    "run_dir": str(run_dir),
                    "generated_at": _utcnow(),
                    "added": added,
                    "incremented": incremented,
                    "skipped": skipped,
                    "entries": auto_learned,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        logger.info(
            "Healing auto-learn: +%d new patterns, %d incremented for %s",
            added,
            incremented,
            family,
        )

    return {"added": added, "incremented": incremented, "skipped": skipped}


def _load_run_failures(run_dir: Path) -> list[dict]:
    """Load failure records from a run directory."""
    failures: list[dict] = []
    for candidate in ["reviewer-failures.json", "validation-results.json", "example-gate-results.json"]:
        path = run_dir / candidate
        if not path.exists():
            # Try evidence subdir
            path = run_dir / "evidence" / "latest" / candidate
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                failures.extend(f for f in data if isinstance(f, dict) and not f.get("passed", True))
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        failures.extend(f for f in v if isinstance(f, dict) and not f.get("passed", True))
        except (OSError, json.JSONDecodeError, KeyError):  # noqa: BLE001
            logger.debug("Failed to parse failure record from %s", path, exc_info=True)
    return failures


def _find_by_sig(patterns: list[dict], sig: str) -> dict | None:
    """Find an existing pattern entry by signature."""
    for p in patterns:
        if _normalize_reason(p.get("reason_signature", "")) == sig:
            return p
    return None
