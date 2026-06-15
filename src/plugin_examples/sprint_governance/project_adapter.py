"""Project adapter — portable project configuration for the autonomy loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ProjectAdapter:
    """Project-specific configuration for the sprint governance loop."""

    project_name: str = ""
    repo_root: str = ""
    default_branch: str = "main"
    evidence_paths: list[str] = field(default_factory=list)
    plan_paths: list[str] = field(default_factory=list)
    taskcard_paths: list[str] = field(default_factory=list)
    prompt_folder_path: str = ""
    prompt_registry_path: str = ""
    test_commands: dict[str, str] = field(default_factory=dict)
    lint_commands: dict[str, str] = field(default_factory=dict)
    validator_commands: list[str] = field(default_factory=list)
    build_commands: list[str] = field(default_factory=list)
    governance_commands: dict[str, str] = field(default_factory=dict)
    protected_paths: list[str] = field(default_factory=list)
    allowed_mutation_paths: list[str] = field(default_factory=list)
    docs_paths: list[str] = field(default_factory=list)
    skills_paths: list[str] = field(default_factory=list)
    agent_instruction_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "repo_root": self.repo_root,
            "default_branch": self.default_branch,
            "evidence_paths": self.evidence_paths,
            "plan_paths": self.plan_paths,
            "taskcard_paths": self.taskcard_paths,
            "prompt_folder_path": self.prompt_folder_path,
            "prompt_registry_path": self.prompt_registry_path,
            "test_commands": self.test_commands,
            "lint_commands": self.lint_commands,
            "validator_commands": self.validator_commands,
            "build_commands": self.build_commands,
            "governance_commands": self.governance_commands,
            "protected_paths": self.protected_paths,
            "allowed_mutation_paths": self.allowed_mutation_paths,
            "docs_paths": self.docs_paths,
            "skills_paths": self.skills_paths,
            "agent_instruction_paths": self.agent_instruction_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectAdapter:
        return cls(
            project_name=data.get("project_name", ""),
            repo_root=data.get("repo_root", ""),
            default_branch=data.get("default_branch", "main"),
            evidence_paths=data.get("evidence_paths", []),
            plan_paths=data.get("plan_paths", []),
            taskcard_paths=data.get("taskcard_paths", []),
            prompt_folder_path=data.get("prompt_folder_path", ""),
            prompt_registry_path=data.get("prompt_registry_path", ""),
            test_commands=data.get("test_commands", {}),
            lint_commands=data.get("lint_commands", {}),
            validator_commands=data.get("validator_commands", []),
            build_commands=data.get("build_commands", []),
            governance_commands=data.get("governance_commands", {}),
            protected_paths=data.get("protected_paths", []),
            allowed_mutation_paths=data.get("allowed_mutation_paths", []),
            docs_paths=data.get("docs_paths", []),
            skills_paths=data.get("skills_paths", []),
            agent_instruction_paths=data.get("agent_instruction_paths", []),
        )


def load_adapter(repo_root: Path) -> ProjectAdapter:
    """Load project adapter from sprint-governance-schema.yaml.

    Falls back to defaults if config not found.
    """
    config_path = repo_root / "pipeline" / "configs" / "sprint-governance-schema.yaml"
    if not config_path.exists():
        return ProjectAdapter(
            project_name=repo_root.name,
            repo_root=str(repo_root),
        )

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return ProjectAdapter(
            project_name=repo_root.name,
            repo_root=str(repo_root),
        )

    adapter_data = data.get("project_adapter", {})
    adapter = ProjectAdapter.from_dict(adapter_data)

    # Resolve repo_root
    if adapter.repo_root in {"", "."}:
        adapter.repo_root = str(repo_root)

    return adapter


def validate_adapter(adapter: ProjectAdapter) -> list[str]:
    """Validate that a project adapter has all required fields.

    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    if not adapter.project_name:
        errors.append("project_name is required")
    if not adapter.repo_root:
        errors.append("repo_root is required")
    if not adapter.evidence_paths:
        errors.append("evidence_paths must have at least one entry")
    if not adapter.prompt_folder_path:
        errors.append("prompt_folder_path is required")
    if not adapter.test_commands:
        errors.append("test_commands must have at least one entry")

    # Check for overlap between protected and mutation paths
    protected = set(adapter.protected_paths)
    allowed = set(adapter.allowed_mutation_paths)
    overlap = protected & allowed
    if overlap:
        errors.append(
            f"protected_paths and allowed_mutation_paths overlap: {sorted(overlap)}"
        )

    return errors
