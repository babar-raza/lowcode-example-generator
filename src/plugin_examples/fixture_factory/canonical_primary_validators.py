"""
Canonical-Primary Invariant Validators (12 rules: CPV-01..CPV-12)

Sprint: lowcode-plugin-canonical-primary-wave8-20260605

These validators enforce that the canonical-primary registry model is
applied consistently: only products.aspose.net slug-based identities
are treated as publication candidates. Legacy alias entries must never
be counted as separate canonical coverage.

Relationship to PIV validators:
- PIV-01..PIV-14 validate individual dryrun packages
- CPV-01..CPV-12 validate system-level invariants across all packages
  and the registry as a whole
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

GENERIC_BARCODE_SLUGS = {
    "generate-barcode",
    "recognize-barcode",
    "generate-qr-code",
    "scan-barcode",
    "read-barcode",
    "create-barcode",
}

CANONICAL_BARCODE_SLUGS = {
    "1d-barcode-writer",
    "1d-barcode-reader",
    "2d-barcode-writer",
    "2d-barcode-reader",
}


@dataclass
class CpvViolation:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    context: str = ""


@dataclass
class CpvResult:
    violations: list[CpvViolation] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARNING")

    def to_dict(self) -> dict:
        return {
            "passes": self.passes,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "violations": [
                {"rule": v.rule, "severity": v.severity, "message": v.message, "context": v.context}
                for v in self.violations
            ],
        }


def _read_json(path: Path) -> dict | None:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def run_canonical_primary_validators(
    packages: dict[str, dict],
    registry_entries: list[dict] | None = None,
    publication_matrix: dict | None = None,
    family_plugin_lists: dict | None = None,
) -> CpvResult:
    """
    Run all 12 canonical-primary invariant rules.

    Args:
        packages: dict of package_key -> package info dict.
            Each package info may have: verdict, canonical_plugin_slug,
            legacy_slug, classification, path, sprint.
        registry_entries: list of registry entry dicts (from YAML loader).
            Each entry may have: family, plugin_slug, canonical_plugin_slug,
            identity_status, migration_status, legacy_aliases, display_plugin_name.
        publication_matrix: optional dict with keys like "canonical_candidates",
            "legacy_aliases", "identity_review_required".
        family_plugin_lists: optional dict of family -> list of canonical slugs.
            Used for CPV-11.

    Returns:
        CpvResult with all violations.
    """
    result = CpvResult()
    registry_entries = registry_entries or []
    publication_matrix = publication_matrix or {}
    family_plugin_lists = family_plugin_lists or {}

    # -------------------------------------------------------------------
    # CPV-01: Publication candidate must not use legacy slug as primary
    # A package classified as PUBLICATION_CANDIDATE_LOCAL_CLEAN must have
    # package_key == canonical_plugin_slug (not a generic alias).
    # -------------------------------------------------------------------
    canonical_candidates = publication_matrix.get("canonical_candidates", [])
    for key in canonical_candidates:
        family, slug = key.split("/", 1) if "/" in key else ("", key)
        if family == "barcode" and slug in GENERIC_BARCODE_SLUGS:
            result.violations.append(
                CpvViolation(
                    "CPV-01",
                    "ERROR",
                    f"Publication candidate '{key}' uses a legacy generic slug — must use canonical slug",
                    key,
                )
            )
        # Check against package info
        pkg = packages.get(key, {})
        legacy = pkg.get("legacy_slug")
        canon = pkg.get("canonical_plugin_slug")
        if legacy and not canon:
            result.violations.append(
                CpvViolation(
                    "CPV-01",
                    "ERROR",
                    f"Publication candidate '{key}' has legacy_slug '{legacy}' but no canonical_plugin_slug",
                    key,
                )
            )

    # -------------------------------------------------------------------
    # CPV-02: Canonical registry entry must have canonical_plugin_slug
    # -------------------------------------------------------------------
    for entry in registry_entries:
        if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED" and not entry.get("canonical_plugin_slug"):
            fslug = f"{entry.get('family', '?')}/{entry.get('plugin_slug', '?')}"
            result.violations.append(
                CpvViolation(
                    "CPV-02",
                    "ERROR",
                    f"Registry entry '{fslug}' has identity_status=CANONICAL_IDENTITY_VERIFIED but no canonical_plugin_slug",
                    fslug,
                )
            )

    # -------------------------------------------------------------------
    # CPV-03: Canonical registry entry must have display_plugin_name
    # -------------------------------------------------------------------
    for entry in registry_entries:
        if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED" and not entry.get("display_plugin_name"):
                fslug = f"{entry.get('family', '?')}/{entry.get('plugin_slug', '?')}"
                result.violations.append(
                    CpvViolation(
                        "CPV-03",
                        "WARNING",
                        f"Registry entry '{fslug}' has CANONICAL_IDENTITY_VERIFIED but missing display_plugin_name",
                        fslug,
                    )
                )

    # -------------------------------------------------------------------
    # CPV-04: Legacy alias must not be counted as a separate canonical example
    # If a package_key is in legacy_aliases list AND also in canonical_candidates,
    # it is double-counted.
    # -------------------------------------------------------------------
    legacy_alias_keys = set(publication_matrix.get("legacy_aliases", []))
    canonical_candidate_keys = set(canonical_candidates)
    double_counted = legacy_alias_keys & canonical_candidate_keys
    for key in double_counted:
        result.violations.append(
            CpvViolation(
                "CPV-04",
                "ERROR",
                f"'{key}' appears in both legacy_aliases and canonical_candidates — double-counted",
                key,
            )
        )

    # -------------------------------------------------------------------
    # CPV-05: Dryrun path must use canonical slug, not generic slug
    # Check packages where path contains a generic barcode slug directory
    # -------------------------------------------------------------------
    for key, pkg in packages.items():
        path_str = pkg.get("path", "")
        family, slug = key.split("/", 1) if "/" in key else ("", key)
        if family == "barcode" and slug in GENERIC_BARCODE_SLUGS:
            # Only an error if no legacy_slug / migrated_from in source-provenance
            sp_canon = pkg.get("canonical_plugin_slug")
            if not sp_canon:
                result.violations.append(
                    CpvViolation(
                        "CPV-05",
                        "ERROR",
                        f"Dryrun package '{key}' at path '{path_str}' uses generic slug with no alias record in source-provenance",
                        key,
                    )
                )

    # -------------------------------------------------------------------
    # CPV-06: source-provenance canonical_url must match registry canonical_url
    # For packages that have canonical_plugin_slug, check against registry
    # -------------------------------------------------------------------
    registry_url_map: dict[str, str] = {}
    for entry in registry_entries:
        slug = f"{entry.get('family', '')}/{entry.get('canonical_plugin_slug', '') or entry.get('plugin_slug', '')}"
        url = entry.get("canonical_url", "")
        if slug and url:
            registry_url_map[slug] = url

    for key, pkg in packages.items():
        canon_slug = pkg.get("canonical_plugin_slug")
        if not canon_slug:
            continue
        family = key.split("/")[0] if "/" in key else ""
        reg_key = f"{family}/{canon_slug}"
        reg_url = registry_url_map.get(reg_key)
        # source-provenance data would be in path/source-provenance.json
        path = pkg.get("path")
        if path and reg_url:
            sp_path = Path(path) / "source-provenance.json"
            sp_data = _read_json(sp_path) or {}
            sp_url = sp_data.get("canonical_url", "")
            if sp_url and reg_url and sp_url.rstrip("/") != reg_url.rstrip("/"):
                result.violations.append(
                    CpvViolation(
                        "CPV-06",
                        "WARNING",
                        f"'{key}' source-provenance canonical_url '{sp_url}' differs from registry '{reg_url}'",
                        key,
                    )
                )

    # -------------------------------------------------------------------
    # CPV-07: README title must not use generic operation name
    # For each package, check its README.md first line
    # -------------------------------------------------------------------
    for key, pkg in packages.items():
        path = pkg.get("path")
        if not path:
            continue
        readme = Path(path) / "README.md"
        if readme.exists():
            try:
                first_line = readme.read_text(encoding="utf-8", errors="replace").split("\n")[0].strip().lower()
                for generic in GENERIC_BARCODE_SLUGS:
                    readable = generic.replace("-", " ")
                    family = key.split("/")[0] if "/" in key else ""
                    if family == "barcode" and readable in first_line:
                        result.violations.append(
                            CpvViolation(
                                "CPV-07",
                                "WARNING",
                                f"'{key}' README title contains generic operation name '{generic}' — use display_plugin_name",
                                str(readme),
                            )
                        )
                        break
            except (OSError, json.JSONDecodeError, KeyError):
                logger.debug("Failed to parse README for generic-name check on %s", key, exc_info=True)

    # -------------------------------------------------------------------
    # CPV-08: BarCode generic names must not appear in publication candidate list
    # -------------------------------------------------------------------
    for key in canonical_candidate_keys:
        family, slug = key.split("/", 1) if "/" in key else ("", key)
        if family == "barcode" and slug in GENERIC_BARCODE_SLUGS:
            result.violations.append(
                CpvViolation(
                    "CPV-08",
                    "ERROR",
                    f"Publication candidate list contains BarCode generic name '{key}' — must not be PUBLICATION_CANDIDATE_LOCAL_CLEAN",
                    key,
                )
            )

    # -------------------------------------------------------------------
    # CPV-09: Publication matrix must not include IDENTITY_REVIEW_REQUIRED as clean
    # -------------------------------------------------------------------
    review_required = set(publication_matrix.get("identity_review_required", []))
    contamination = review_required & canonical_candidate_keys
    for key in contamination:
        result.violations.append(
            CpvViolation(
                "CPV-09",
                "ERROR",
                f"'{key}' is in both identity_review_required and canonical_candidates — matrix contaminated",
                key,
            )
        )

    # -------------------------------------------------------------------
    # CPV-10: Family-level probe must not be counted as plugin-level coverage
    # A "family-level" package would have slug == family name (e.g., "barcode/barcode")
    # or a generic verb phrase without plugin identity.
    # -------------------------------------------------------------------
    for key in canonical_candidate_keys:
        parts = key.split("/", 1)
        if len(parts) == 2:
            family, slug = parts
            if slug == family:
                result.violations.append(
                    CpvViolation(
                        "CPV-10",
                        "WARNING",
                        f"'{key}' appears to be a family-level probe (slug == family), not plugin-level coverage",
                        key,
                    )
                )

    # -------------------------------------------------------------------
    # CPV-11: Canonical identity map must include family plugin list
    # Each family with CANONICAL_IDENTITY_VERIFIED entries needs a plugin list.
    # -------------------------------------------------------------------
    verified_families: set = set()
    for entry in registry_entries:
        if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
            fam = entry.get("family", "")
            if fam:
                verified_families.add(fam)

    for fam in sorted(verified_families):
        if fam not in family_plugin_lists:
            result.violations.append(
                CpvViolation(
                    "CPV-11",
                    "WARNING",
                    f"Family '{fam}' has CANONICAL_IDENTITY_VERIFIED entries but no entry in family_plugin_lists",
                    fam,
                )
            )

    # -------------------------------------------------------------------
    # CPV-12: Final summary must not count canonical entries and legacy aliases together
    # Validate that total = canonical_candidates + legacy_aliases + identity_review_required
    # (plus any other bucket), NOT that canonical + legacy sums are combined.
    # -------------------------------------------------------------------
    total_declared = publication_matrix.get("total")
    if total_declared is not None:
        bucket_sum = len(canonical_candidate_keys) + len(legacy_alias_keys) + len(review_required)
        other_buckets = publication_matrix.get("other_buckets", [])
        for bucket in other_buckets:
            bucket_sum += len(bucket)
        if bucket_sum != total_declared:
            result.violations.append(
                CpvViolation(
                    "CPV-12",
                    "WARNING",
                    f"Publication matrix total={total_declared} but sum of buckets={bucket_sum} — "
                    "canonical and legacy aliases may be conflated",
                    f"total={total_declared}, bucket_sum={bucket_sum}",
                )
            )

    return result
