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


@dataclass(frozen=True)
class GitHubConfig:
    official_examples_repo: RepoRef
    published_plugin_examples_repo: RepoRef


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
