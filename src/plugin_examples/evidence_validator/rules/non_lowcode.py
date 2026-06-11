"""Evidence validation rules — NonLowCodeValidatorRules (NL-V01 through NL-V15).

MANDATORY SKIP behavior (every rule):
  Returns passed=True (SKIP) when:
  - pipeline/plugin-capability-registry/ does not exist
  - No registry YAML file for the family
  - family.config.plugin_detection.fallback_strategy is None

Status values are from the 12-value authoritative enum only.

NL-V05: fires when status=PROBE_CONFIRMED but probe_evidence is absent.
NL-V06: fires when status=VERIFIED_PUBLISHABLE but probe_evidence is absent.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plugin_examples.evidence_validator.models import RuleResult

logger = logging.getLogger(__name__)

_AUTHORITATIVE_STATUSES = frozenset(
    {
        "WEBSITE_DISCOVERED",
        "REFLECTION_CANDIDATE",
        "AI_DRAFT",
        "PROBE_CANDIDATE",
        "PROBE_CONFIRMED",
        "PROBE_FAILED",
        "VERIFIED_PUBLISHABLE",
        "STATIC_MAPPING_REQUIRED",
        "BLOCKED_PACKAGE_UNAVAILABLE",
        "BLOCKED_REFLECTION_FAILED",
        "BLOCKED_LICENSE_RESTRICTED",
        "REJECTED_BY_VALIDATOR",
    }
)

_VALID_FAILURE_TAXONOMIES = frozenset(
    {
        "PROBE_FAILED_LICENSE",
        "PROBE_FAILED_API",
        "PROBE_FAILED_BUILD",
        "PROBE_FAILED_RESTORE",
        "PROBE_FAILED_TIMEOUT",
    }
)

_VALID_REJECTION_REASONS = frozenset(
    {
        "TYPE_NOT_IN_REFLECTION",
        "METHOD_NOT_IN_REFLECTION",
    }
)


# Import here to avoid circular at module top
def _RuleResult(**kwargs):
    from plugin_examples.evidence_validator.models import RuleResult

    return RuleResult(**kwargs)


class NonLowCodeValidatorRules:
    """Rule mixin for non-LowCode plugin capability validation.

    Follows Sprint89Rules mixin pattern exactly.
    All 14 rules skip when registry is absent or fallback_strategy is None.

    Expects self.bundle_dir (Path) to be set by the hosting validator.
    Expects self.family (str) for registry lookups.
    Expects self.config (optional) for fallback_strategy check.
    """

    # ------------------------------------------------------------------
    # SKIP helper
    # ------------------------------------------------------------------

    def _nl_skip_check(self, rule_id: str, description: str):
        """Return a SKIP RuleResult if preconditions for NL-V rules are not met.

        Returns None if the rule should proceed.
        """
        registry_dir = self._nl_registry_dir()
        if not registry_dir.exists():
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="SKIP: plugin-capability-registry/ does not exist",
            )

        family = getattr(self, "family", None)
        if family:
            registry_file = registry_dir / f"{family}.yaml"
            if not registry_file.exists():
                return _RuleResult(
                    rule_id=rule_id,
                    description=description,
                    severity="FAILURE",
                    passed=True,
                    evidence=f"SKIP: no registry file for family '{family}'",
                )

        config = getattr(self, "config", None)
        if config is not None:
            pd = getattr(config, "plugin_detection", None)
            if pd is not None and getattr(pd, "fallback_strategy", None) is None:
                return _RuleResult(
                    rule_id=rule_id,
                    description=description,
                    severity="FAILURE",
                    passed=True,
                    evidence="SKIP: fallback_strategy is None",
                )

        return None

    def _nl_registry_dir(self) -> Path:
        bundle_dir = getattr(self, "bundle_dir", Path("."))
        # Walk up to find repo root (contains pipeline/)
        candidate = bundle_dir
        for _ in range(10):
            if (candidate / "pipeline").exists():
                return candidate / "pipeline" / "plugin-capability-registry"
            if candidate.parent == candidate:
                break
            candidate = candidate.parent
        return bundle_dir / "pipeline" / "plugin-capability-registry"

    def _nl_load_registry_entries(self) -> list[dict]:
        """Load registry entries for self.family from the YAML file."""
        registry_dir = self._nl_registry_dir()
        family = getattr(self, "family", "")
        registry_file = registry_dir / f"{family}.yaml"
        if not registry_file.exists():
            return []
        try:
            import yaml

            data = yaml.safe_load(registry_file.read_text(encoding="utf-8"))
            return data.get("entries", []) if isinstance(data, dict) else []
        except Exception:  # noqa: BLE001
            return []

    # ------------------------------------------------------------------
    # Rules NL-V01 through NL-V15
    # ------------------------------------------------------------------

    def rule_nl_v01(self) -> "RuleResult":
        """NL-V01: Registry file must exist for families with fallback_strategy set.

        Uses narrower skip: only skips when registry dir absent OR fallback_strategy is None.
        Does NOT skip when the family YAML is absent — that is what this rule checks.
        """
        rule_id, description = "NL-V01", "Registry YAML must exist for non-LowCode families"
        registry_dir = self._nl_registry_dir()
        if not registry_dir.exists():
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="SKIP: plugin-capability-registry/ does not exist",
            )
        config = getattr(self, "config", None)
        if config is not None:
            pd = getattr(config, "plugin_detection", None)
            if pd is not None and getattr(pd, "fallback_strategy", None) is None:
                return _RuleResult(
                    rule_id=rule_id,
                    description=description,
                    severity="FAILURE",
                    passed=True,
                    evidence="SKIP: fallback_strategy is None",
                )
        family = getattr(self, "family", "")
        registry_file = registry_dir / f"{family}.yaml"
        if registry_file.exists():
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence=f"Registry file exists: {registry_file.name}",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V01: Registry file missing for family '{family}'",
        )

    def rule_nl_v02(self) -> "RuleResult":
        """NL-V02: Every registry entry must have a status from the 12-value enum."""
        rule_id, description = "NL-V02", "All registry entries must use authoritative 12-value status"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        invalid = [e.get("status") for e in entries if e.get("status") not in _AUTHORITATIVE_STATUSES]
        if not invalid:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence=f"All {len(entries)} entries use authoritative status values",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V02: Invalid status values found: {invalid}",
        )

    def rule_nl_v03(self) -> "RuleResult":
        """NL-V03: confidence_score must be in [0.0, 1.05] for all entries."""
        rule_id, description = "NL-V03", "confidence_score must be in [0.0, 1.05]"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            f"{e.get('type_name')}:{e.get('confidence_score')}"
            for e in entries
            if not isinstance(e.get("confidence_score"), (int, float))
            or not (0.0 <= float(e.get("confidence_score", -1)) <= 1.05)
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence=f"All {len(entries)} entries have valid confidence_score",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V03: confidence_score out of range: {violations}",
        )

    def rule_nl_v04(self) -> "RuleResult":
        """NL-V04: package_id must not be inferred from slug (must use alias table)."""
        rule_id, description = "NL-V04", "package_id must be explicit (never slug-inferred)"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        family = getattr(self, "family", "")
        violations = []
        for e in entries:
            pkg = e.get("package_id", "")
            # A slug-inferred ID would be e.g. f"Aspose.{family.title()}" — detect obvious cases
            slug_inferred = f"Aspose.{family.title()}"
            if not pkg or pkg == slug_inferred:
                # Check against alias file
                registry_dir = self._nl_registry_dir()
                alias_file = registry_dir / "package-aliases.json"
                if alias_file.exists():
                    try:
                        aliases = json.loads(alias_file.read_text(encoding="utf-8"))
                        expected = aliases.get("families", {}).get(family)
                        if expected and pkg != expected:
                            violations.append(f"Expected '{expected}' got '{pkg}'")
                    except Exception:  # noqa: BLE001
                        pass
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="package_id values are explicit",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V04: Mismatched package_id: {violations}",
        )

    def rule_nl_v05(self) -> "RuleResult":
        """NL-V05: PROBE_CONFIRMED entries must have probe_evidence field."""
        rule_id, description = "NL-V05", "PROBE_CONFIRMED requires probe_evidence"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            e.get("type_name") for e in entries if e.get("status") == "PROBE_CONFIRMED" and not e.get("probe_evidence")
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All PROBE_CONFIRMED entries have probe_evidence",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V05: PROBE_CONFIRMED missing probe_evidence: {violations}",
        )

    def rule_nl_v06(self) -> "RuleResult":
        """NL-V06: VERIFIED_PUBLISHABLE entries must have probe_evidence field."""
        rule_id, description = "NL-V06", "VERIFIED_PUBLISHABLE requires probe_evidence"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            e.get("type_name")
            for e in entries
            if e.get("status") == "VERIFIED_PUBLISHABLE" and not e.get("probe_evidence")
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All VERIFIED_PUBLISHABLE entries have probe_evidence",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V06: VERIFIED_PUBLISHABLE missing probe_evidence: {violations}",
        )

    def rule_nl_v07(self) -> "RuleResult":
        """NL-V07: PROBE_FAILED entries must have failure_taxonomy from 5-code enum."""
        rule_id, description = "NL-V07", "PROBE_FAILED requires valid failure_taxonomy"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            f"{e.get('type_name')}:{e.get('failure_taxonomy')}"
            for e in entries
            if e.get("status") == "PROBE_FAILED" and e.get("failure_taxonomy") not in _VALID_FAILURE_TAXONOMIES
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All PROBE_FAILED entries have valid failure_taxonomy",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V07: Invalid failure_taxonomy: {violations}",
        )

    def rule_nl_v08(self) -> "RuleResult":
        """NL-V08: REJECTED_BY_VALIDATOR entries must have rejection_reason."""
        rule_id, description = "NL-V08", "REJECTED_BY_VALIDATOR requires rejection_reason"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            e.get("type_name")
            for e in entries
            if e.get("status") == "REJECTED_BY_VALIDATOR" and e.get("rejection_reason") not in _VALID_REJECTION_REASONS
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All REJECTED_BY_VALIDATOR entries have rejection_reason",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V08: REJECTED_BY_VALIDATOR missing rejection_reason: {violations}",
        )

    def rule_nl_v09(self) -> "RuleResult":
        """NL-V09: assembly_fingerprint must be a 64-char hex string if present."""
        rule_id, description = "NL-V09", "assembly_fingerprint must be valid SHA-256 if set"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = []
        for e in entries:
            fp = e.get("assembly_fingerprint")
            if fp and (len(fp) != 64 or not all(c in "0123456789abcdef" for c in fp.lower())):
                violations.append(f"{e.get('type_name')}:'{fp}'")
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All assembly_fingerprint values are valid",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V09: Invalid fingerprints: {violations}",
        )

    def rule_nl_v10(self) -> "RuleResult":
        """NL-V10: PROBE_CONFIRMED entries must have a last_validated timestamp."""
        rule_id, description = "NL-V10", "PROBE_CONFIRMED requires last_validated timestamp"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            e.get("type_name") for e in entries if e.get("status") == "PROBE_CONFIRMED" and not e.get("last_validated")
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="All PROBE_CONFIRMED entries have last_validated",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V10: PROBE_CONFIRMED missing last_validated: {violations}",
        )

    def rule_nl_v11(self) -> "RuleResult":
        """NL-V11: entries must not have status=PROBE_UNKNOWN (forbidden unclassified status)."""
        rule_id, description = "NL-V11", "PROBE_UNKNOWN status is forbidden (always classify)"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [e.get("type_name") for e in entries if e.get("status") == "PROBE_UNKNOWN"]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="No PROBE_UNKNOWN entries found",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V11: Forbidden PROBE_UNKNOWN status: {violations}",
        )

    def rule_nl_v12(self) -> "RuleResult":
        """NL-V12: AI-sourced entries (ai_source_flag=True) must not be VERIFIED_PUBLISHABLE."""
        rule_id, description = "NL-V12", "AI-sourced entries cannot be VERIFIED_PUBLISHABLE"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [
            e.get("type_name")
            for e in entries
            if e.get("ai_source_flag") is True and e.get("status") == "VERIFIED_PUBLISHABLE"
        ]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="No AI-sourced VERIFIED_PUBLISHABLE entries",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V12: AI entries must not be VERIFIED_PUBLISHABLE: {violations}",
        )

    def rule_nl_v13(self) -> "RuleResult":
        """NL-V13: registry entries must not reference format-authority paths."""
        rule_id, description = "NL-V13", "Registry entries must not reference format-authority/"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = []
        for e in entries:
            pe = e.get("probe_evidence") or ""
            if "format-authority" in pe:
                violations.append(f"{e.get('type_name')}:{pe}")
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="No format-authority references in registry entries",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V13: format-authority referenced: {violations}",
        )

    def rule_nl_v14(self) -> "RuleResult":
        """NL-V14: type_name and method_name must be non-empty in all entries."""
        rule_id, description = "NL-V14", "type_name and method_name must be non-empty"
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip
        entries = self._nl_load_registry_entries()
        violations = [str(i) for i, e in enumerate(entries) if not e.get("type_name") or not e.get("method_name")]
        if not violations:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence=f"All {len(entries)} entries have type_name and method_name",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=f"NL-V14: Missing type_name or method_name at indices: {violations}",
        )

    def rule_nl_v15(self) -> "RuleResult":
        """NL-V15: When fallback_strategy is capability_registry and namespace_patterns is empty,
        at least one entry must have status=PROBE_CONFIRMED.

        Families with fallback_strategy=capability_registry and no namespace_patterns rely
        entirely on the capability registry for discovery.  If no PROBE_CONFIRMED entry
        exists, the non-LowCode pipeline produces zero generation-ready candidates and
        the family is effectively dead — this must be surfaced as a failure, not silently
        skipped.
        """
        rule_id = "NL-V15"
        description = (
            "capability_registry families with empty namespace_patterns must have at least one PROBE_CONFIRMED entry"
        )
        skip = self._nl_skip_check(rule_id, description)
        if skip:
            return skip

        # Determine fallback_strategy and namespace_patterns from config
        config = getattr(self, "config", None)
        fallback_strategy = None
        namespace_patterns: list = []
        if config is not None:
            pd = getattr(config, "plugin_detection", None)
            if pd is not None:
                fallback_strategy = getattr(pd, "fallback_strategy", None)
                namespace_patterns = getattr(pd, "namespace_patterns", []) or []

        # Only applies when fallback_strategy is capability_registry and namespace_patterns is empty
        if fallback_strategy != "capability_registry" or namespace_patterns:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence="SKIP: rule only applies when fallback_strategy=capability_registry and namespace_patterns=[]",
            )

        entries = self._nl_load_registry_entries()
        confirmed = [e for e in entries if e.get("status") == "PROBE_CONFIRMED"]
        if confirmed:
            return _RuleResult(
                rule_id=rule_id,
                description=description,
                severity="FAILURE",
                passed=True,
                evidence=f"{len(confirmed)} PROBE_CONFIRMED entries found — generation-ready candidates exist",
            )
        return _RuleResult(
            rule_id=rule_id,
            description=description,
            severity="FAILURE",
            passed=False,
            failure_detail=(
                "NL-V15: fallback_strategy=capability_registry with empty namespace_patterns "
                "but no PROBE_CONFIRMED entries — non-LowCode pipeline produces zero generation-ready candidates. "
                "Run probe validation to promote at least one entry to PROBE_CONFIRMED."
            ),
        )
