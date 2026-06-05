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
