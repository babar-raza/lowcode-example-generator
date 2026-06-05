"""Data models for the plugin-code registry."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PluginEntry:
    family: str
    plugin_slug: str
    registry_status: str
    canonical_url: Optional[str] = None
    plugin_url: Optional[str] = None
    page_source_status: Optional[str] = None
    implementation_model: Optional[str] = None
    transformation_readiness_reason: Optional[str] = None
    classes_used: list = field(default_factory=list)
    methods_used: list = field(default_factory=list)
    namespaces_used: list = field(default_factory=list)
    code_hashes: list = field(default_factory=list)
    github_links: list = field(default_factory=list)
    next_action: Optional[str] = None
    blocker_type: Optional[str] = None
    dryrun_package_path: Optional[str] = None
    dryrun_validation_status: Optional[str] = None
    publication_candidate_status: Optional[str] = None
    # Canonical identity fields (added Sprint lowcode-plugin-canonical-identity-wave7-20260605)
    canonical_plugin_slug: Optional[str] = None
    identity_status: Optional[str] = None
    # Canonical-primary fields (added Sprint lowcode-plugin-canonical-primary-wave8-20260605)
    legacy_aliases: list = field(default_factory=list)
    display_plugin_name: Optional[str] = None
    migration_status: Optional[str] = None
    migrated_from: Optional[str] = None

    @property
    def effective_canonical_slug(self) -> str:
        """The canonical plugin slug from products.aspose.net. Falls back to plugin_slug."""
        if self.canonical_plugin_slug:
            return self.canonical_plugin_slug
        if self.canonical_url:
            return self.canonical_url.rstrip("/").split("/")[-1]
        return self.plugin_slug

    @property
    def is_identity_verified(self) -> bool:
        """True only when canonical_plugin_slug is confirmed and matches canonical_url."""
        return self.identity_status == "CANONICAL_IDENTITY_VERIFIED"

    @property
    def is_canonical_primary(self) -> bool:
        """True when this entry uses canonical slug as primary key (not a legacy alias)."""
        return self.migration_status == "CANONICAL_PRIMARY_MIGRATED" or (
            self.is_identity_verified and not self.migrated_from
        )

    @property
    def canonical_key(self) -> str:
        """The canonical family/slug key for this plugin."""
        return f"{self.family}/{self.effective_canonical_slug}"

    def is_alias_for(self, slug: str) -> bool:
        """True if slug is in this entry's legacy aliases."""
        return slug in self.legacy_aliases

    @property
    def is_ready(self) -> bool:
        return self.registry_status == "READY_FOR_TRANSFORMATION"

    @property
    def has_canonical_page(self) -> bool:
        return bool(self.canonical_url)

    @property
    def has_code_evidence(self) -> bool:
        return bool(self.code_hashes) or bool(self.github_links)

    @property
    def is_fixture_free(self) -> bool:
        """Heuristic: families/models that can run without external file fixtures."""
        fixture_free_models = {"STATIC_CONVERTER_CLASS"}
        fixture_free_families = {"barcode", "tex", "svg", "html"}
        return (
            self.implementation_model in fixture_free_models
            or self.family in fixture_free_families
        )

    def readiness_score(self) -> int:
        """Score for prioritizing transformation candidates."""
        score = 0
        if self.registry_status == "READY_FOR_TRANSFORMATION":
            score += 10
        if self.has_canonical_page:
            score += 5
        if self.has_code_evidence:
            score += 3
        if self.is_fixture_free:
            score += 2
        if self.implementation_model:
            score += 1
        return score


@dataclass
class FamilyRegistry:
    family: str
    package_id: str
    github_repo: Optional[str]
    implementation_model: Optional[str]
    plugins: list = field(default_factory=list)

    @property
    def ready_plugins(self) -> list:
        return [p for p in self.plugins if p.registry_status == "READY_FOR_TRANSFORMATION"]
