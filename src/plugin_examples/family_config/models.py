"""Typed data model for family configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RepoRef:
    owner: str
    repo: str
    branch: str


@dataclass(frozen=True)
class DependencyResolution:
    enabled: bool = True
    max_depth: int = 2
    extra_packages: list[str] = field(default_factory=list)
    include_all_tfm_groups: bool = False


@dataclass(frozen=True)
class NuGetConfig:
    package_id: str
    version_policy: str
    pinned_version: str | None = None
    allow_prerelease: bool = False
    target_framework_preference: list[str] = field(
        default_factory=lambda: ["netstandard2.0"]
    )
    dependency_resolution: DependencyResolution = field(
        default_factory=DependencyResolution
    )


@dataclass(frozen=True)
class PluginDetection:
    namespace_patterns: list[str]
    fallback_strategy: str | None = None
    # namespace_source: LOWCODE (has namespace_patterns active) | NON_LOWCODE_PLUGIN (fallback_strategy set, no namespace)
    # public_repo_kind: LOWCODE_EXAMPLES | PLUGIN_EXAMPLES (derived from namespace_source)
    # folder_namespace_segment: 'lowcode' for LOWCODE, '' for NON_LOWCODE_PLUGIN in single-purpose repos

    @property
    def namespace_source(self) -> str:
        """Derived: LOWCODE if namespace patterns are primary; NON_LOWCODE_PLUGIN if fallback only."""
        return "NON_LOWCODE_PLUGIN" if self.fallback_strategy is not None and not self.namespace_patterns else "LOWCODE"

    @property
    def public_repo_kind(self) -> str:
        return "PLUGIN_EXAMPLES" if self.namespace_source == "NON_LOWCODE_PLUGIN" else "LOWCODE_EXAMPLES"

    @property
    def folder_namespace_segment(self) -> str:
        """Path segment for example folder: 'lowcode' for LowCode families, '' for plugin-only repos."""
        return "" if self.namespace_source == "NON_LOWCODE_PLUGIN" else "lowcode"


@dataclass(frozen=True)
class GitHubConfig:
    official_examples_repo: RepoRef
    published_plugin_examples_repo: RepoRef
    central_repo_allowed: bool = False


@dataclass(frozen=True)
class FixtureSource:
    type: str
    owner: str
    repo: str
    branch: str
    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FixturesConfig:
    sources: list[FixtureSource] = field(default_factory=list)


@dataclass(frozen=True)
class ExistingExamplesConfig:
    sources: list[FixtureSource] = field(default_factory=list)


@dataclass(frozen=True)
class GenerationConfig:
    min_examples_per_family: int
    max_examples_per_monthly_run: int
    allow_new_fixtures: bool = True
    allow_generated_input_files: bool = True
    allowed_types: list[str] = field(default_factory=list)
    preferred_methods_per_type: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationConfig:
    require_restore: bool = True
    require_build: bool = True
    require_run: bool = True
    require_output_validation: bool = True
    require_example_reviewer: bool = True
    runtime_runner: str = "auto"


@dataclass(frozen=True)
class LLMConfig:
    provider_order: list[str]


@dataclass(frozen=True)
class TemplateHints:
    default_input_extension: str = ".xlsx"
    default_input_filename: str = "input.xlsx"
    array_input_filenames: list[str] = field(
        default_factory=lambda: ["input1.xlsx", "input2.xlsx"]
    )
    input_creation_lines: list[str] = field(default_factory=list)
    merger_input_creation_lines: list[str] = field(default_factory=list)
    additional_usings: list[str] = field(default_factory=list)
    default_output_extension: str = ".out"
    default_fixture_extension: str = ".xlsx"


@dataclass(frozen=True)
class FamilyConfig:
    family: str
    display_name: str
    enabled: bool
    status: str
    nuget: NuGetConfig
    plugin_detection: PluginDetection
    github: GitHubConfig
    fixtures: FixturesConfig
    existing_examples: ExistingExamplesConfig
    generation: GenerationConfig
    validation: ValidationConfig
    llm: LLMConfig
    template_hints: TemplateHints = field(default_factory=TemplateHints)
    per_type_constraints: dict = field(default_factory=dict)
