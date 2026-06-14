"""Load plugin-code registry from YAML files."""

import os
from pathlib import Path

import yaml

from .models import FamilyRegistry, PluginEntry

PROTECTED_FAMILIES = {"cells", "words", "pdf", "slides", "email", "diagram"}

REGISTRY_DIR = Path(__file__).parents[3] / "pipeline" / "plugin-code-registry" / "family"


class PluginCodeRegistryLoader:
    """Loads and validates the plugin-code registry from YAML files."""

    def __init__(self, registry_dir: Path | None = None):
        self.registry_dir = registry_dir or REGISTRY_DIR
        self._families: dict[str, FamilyRegistry] = {}
        self._loaded = False

    def load(self) -> "PluginCodeRegistryLoader":
        """Load all family YAML files."""
        self._families = {}
        for path in sorted(self.registry_dir.glob("*.yaml")):
            family = path.stem
            try:
                with open(path) as f:
                    data = yaml.safe_load(f)
                if data:
                    self._families[family] = self._parse_family(family, data)
            except Exception as e:
                print(f"WARNING: failed to load {path}: {e}")
        self._loaded = True
        return self

    def _parse_family(self, family: str, data: dict) -> FamilyRegistry:
        plugins = []
        for raw in data.get("plugins", []):
            entry = PluginEntry(
                family=family,
                plugin_slug=raw.get("plugin_slug", "unknown"),
                registry_status=raw.get("registry_status", "UNKNOWN"),
                canonical_url=raw.get("canonical_url"),
                plugin_url=raw.get("plugin_url"),
                page_source_status=raw.get("page_source_status"),
                implementation_model=raw.get("implementation_model"),
                transformation_readiness_reason=raw.get("transformation_readiness_reason"),
                classes_used=raw.get("classes_used") or [],
                methods_used=raw.get("methods_used") or [],
                namespaces_used=raw.get("namespaces_used") or [],
                code_hashes=raw.get("code_hashes") or [],
                github_links=raw.get("github_links") or [],
                next_action=raw.get("next_action"),
                blocker_type=raw.get("blocker_type"),
                dryrun_package_path=raw.get("dryrun_package_path"),
                dryrun_validation_status=raw.get("dryrun_validation_status"),
                publication_candidate_status=raw.get("publication_candidate_status"),
                canonical_plugin_slug=raw.get("canonical_plugin_slug"),
                identity_status=raw.get("identity_status"),
                legacy_aliases=raw.get("legacy_aliases") or [],
                display_plugin_name=raw.get("display_plugin_name"),
                migration_status=raw.get("migration_status"),
                migrated_from=raw.get("migrated_from"),
            )
            plugins.append(entry)
        return FamilyRegistry(
            family=family,
            package_id=data.get("package_id", ""),
            github_repo=data.get("github_repo"),
            implementation_model=data.get("implementation_model"),
            plugins=plugins,
        )

    def all_families(self) -> dict[str, FamilyRegistry]:
        if not self._loaded:
            self.load()
        return self._families

    def non_protected_families(self) -> dict[str, FamilyRegistry]:
        return {k: v for k, v in self.all_families().items() if k not in PROTECTED_FAMILIES}

    def ready_entries(self) -> list[PluginEntry]:
        """Return all READY_FOR_TRANSFORMATION entries from non-protected families."""
        entries = []
        for fam in self.non_protected_families().values():
            entries.extend(fam.ready_plugins)
        return sorted(entries, key=lambda e: -e.readiness_score())

    def active_entries(self) -> list[PluginEntry]:
        """Return READY_FOR_TRANSFORMATION + TRANSFORMED_TO_EXAMPLE_DRYRUN entries."""
        active_statuses = {"READY_FOR_TRANSFORMATION", "TRANSFORMED_TO_EXAMPLE_DRYRUN", "PUBLICATION_CANDIDATE_LOCAL"}
        entries = []
        for fam in self.non_protected_families().values():
            entries.extend([p for p in fam.plugins if p.registry_status in active_statuses])
        return sorted(entries, key=lambda e: -e.readiness_score())

    def lookup_by_alias(self, family: str, alias_slug: str) -> "PluginEntry | None":
        """Find a canonical entry that has alias_slug in its legacy_aliases."""
        fam = self.all_families().get(family)
        if not fam:
            return None
        for entry in fam.plugins:
            if entry.is_alias_for(alias_slug):
                return entry
        return None

    def canonical_primary_entries(self) -> list["PluginEntry"]:
        """Return entries that are canonical-primary (migration_status=CANONICAL_PRIMARY_MIGRATED)."""
        entries = []
        for fam in self.non_protected_families().values():
            entries.extend([p for p in fam.plugins if p.is_canonical_primary])
        return entries

    def select_wave(self, exclude_slugs: set | None = None, limit: int = 15) -> list["PluginEntry"]:
        """Select top candidates for the next transformation wave."""
        exclude = exclude_slugs or set()
        candidates = [e for e in self.ready_entries() if f"{e.family}/{e.plugin_slug}" not in exclude]
        return candidates[:limit]

    def validate_entry(self, entry: PluginEntry) -> list[str]:
        """Run registry readiness checks. Returns list of violation strings."""
        violations = []
        if entry.registry_status == "READY_FOR_TRANSFORMATION":
            if not entry.canonical_url:
                violations.append(f"R01: {entry.family}/{entry.plugin_slug} missing canonical_url")
            if not entry.page_source_status:
                violations.append(f"R02: {entry.family}/{entry.plugin_slug} missing page_source_status")
            if not entry.implementation_model:
                violations.append(f"R03: {entry.family}/{entry.plugin_slug} missing implementation_model")
            if not entry.classes_used and not entry.methods_used:
                violations.append(f"R04: {entry.family}/{entry.plugin_slug} missing classes_used/methods_used")
            if not entry.transformation_readiness_reason:
                violations.append(f"R07: {entry.family}/{entry.plugin_slug} missing transformation_readiness_reason")
        return violations

    def build_readiness_matrix(self) -> dict:
        """Build full status matrix for reporting."""
        matrix = {"families": {}, "status_counts": {}, "violations": []}
        for family, reg in self.non_protected_families().items():
            family_row = {"ready": 0, "code_harvested": 0, "needs_mapping": 0, "blocked": 0, "other": 0}
            for p in reg.plugins:
                s = p.registry_status
                if s == "READY_FOR_TRANSFORMATION":
                    family_row["ready"] += 1
                elif s == "CODE_HARVESTED":
                    family_row["code_harvested"] += 1
                elif s == "NEEDS_MANUAL_MAPPING":
                    family_row["needs_mapping"] += 1
                elif "BLOCKED" in s:
                    family_row["blocked"] += 1
                else:
                    family_row["other"] += 1
                violations = self.validate_entry(p)
                matrix["violations"].extend(violations)
            matrix["families"][family] = family_row
        return matrix
