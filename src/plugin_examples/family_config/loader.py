"""Family config loader with validation and disabled-config rejection."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from plugin_examples.family_config.models import (
    DependencyResolution,
    ExistingExamplesConfig,
    FamilyConfig,
    FixtureSource,
    FixturesConfig,
    GenerationConfig,
    GitHubConfig,
    LLMConfig,
    NuGetConfig,
    PluginDetection,
    RepoRef,
    TemplateHints,
    ValidationConfig,
)
from plugin_examples.family_config.validator import validate_family_config

logger = logging.getLogger(__name__)


class DisabledFamilyError(Exception):
    """Raised when a family config is disabled and should not be processed."""


def load_family_config(path: str | Path) -> FamilyConfig:
    """Load and validate a family config YAML file.

    Raises:
        DisabledFamilyError: If the config is disabled by path, field, or status.
        jsonschema.ValidationError: If the config fails schema validation.
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path).resolve()

    # Reject configs under disabled/ directory regardless of field values
    if "disabled" in path.parts:
        logger.info("[SKIP] %s — disabled", path)
        raise DisabledFamilyError(f"Config is in disabled directory: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    # Check enabled field before schema validation (may be partial config)
    if not data.get("enabled", True):
        logger.info("[SKIP] %s — disabled", path)
        raise DisabledFamilyError(f"Config has enabled=false: {path}")

    if data.get("status") == "disabled":
        logger.info("[SKIP] %s — disabled", path)
        raise DisabledFamilyError(f"Config has status=disabled: {path}")

    # Full schema validation
    validate_family_config(data)

    return _build_model(data)


def _build_model(data: dict) -> FamilyConfig:
    """Convert a validated dict into a FamilyConfig dataclass."""
    nuget_data = data["nuget"]
    dep_res = nuget_data.get("dependency_resolution", {})

    nuget = NuGetConfig(
        package_id=nuget_data["package_id"],
        version_policy=nuget_data["version_policy"],
        pinned_version=nuget_data.get("pinned_version"),
        allow_prerelease=nuget_data.get("allow_prerelease", False),
        target_framework_preference=nuget_data.get(
            "target_framework_preference", ["netstandard2.0"]
        ),
        dependency_resolution=DependencyResolution(
            enabled=dep_res.get("enabled", True),
            max_depth=dep_res.get("max_depth", 2),
        ),
    )

    plugin_detection = PluginDetection(
        namespace_patterns=data["plugin_detection"]["namespace_patterns"]
    )

    github_data = data["github"]
    github = GitHubConfig(
        official_examples_repo=RepoRef(**github_data["official_examples_repo"]),
        published_plugin_examples_repo=RepoRef(
            **github_data["published_plugin_examples_repo"]
        ),
    )

    fixtures = FixturesConfig(
        sources=[FixtureSource(**s) for s in data["fixtures"].get("sources", [])]
    )

    existing_examples = ExistingExamplesConfig(
        sources=[
            FixtureSource(**s)
            for s in data["existing_examples"].get("sources", [])
        ]
    )

    gen_data = data["generation"]
    generation = GenerationConfig(
        min_examples_per_family=gen_data["min_examples_per_family"],
        max_examples_per_monthly_run=gen_data["max_examples_per_monthly_run"],
        allow_new_fixtures=gen_data.get("allow_new_fixtures", True),
        allow_generated_input_files=gen_data.get(
            "allow_generated_input_files", True
        ),
    )

    val_data = data.get("validation", {})
    validation = ValidationConfig(
        require_restore=val_data.get("require_restore", True),
        require_build=val_data.get("require_build", True),
        require_run=val_data.get("require_run", True),
        require_output_validation=val_data.get("require_output_validation", True),
        require_example_reviewer=val_data.get("require_example_reviewer", True),
        runtime_runner=val_data.get("runtime_runner", "auto"),
    )

    llm = LLMConfig(provider_order=data["llm"]["provider_order"])

    hints_data = data.get("template_hints", {})
    template_hints = TemplateHints(
        default_input_extension=hints_data.get("default_input_extension", ".xlsx"),
        default_input_filename=hints_data.get("default_input_filename", "input.xlsx"),
        array_input_filenames=hints_data.get(
            "array_input_filenames", ["input1.xlsx", "input2.xlsx"]
        ),
        input_creation_lines=hints_data.get("input_creation_lines", []),
        merger_input_creation_lines=hints_data.get("merger_input_creation_lines", []),
        additional_usings=hints_data.get("additional_usings", []),
        default_output_extension=hints_data.get("default_output_extension", ".out"),
        default_fixture_extension=hints_data.get("default_fixture_extension", ".xlsx"),
    )

    return FamilyConfig(
        family=data["family"],
        display_name=data["display_name"],
        enabled=data["enabled"],
        status=data["status"],
        nuget=nuget,
        plugin_detection=plugin_detection,
        github=github,
        fixtures=fixtures,
        existing_examples=existing_examples,
        generation=generation,
        validation=validation,
        llm=llm,
        template_hints=template_hints,
    )
