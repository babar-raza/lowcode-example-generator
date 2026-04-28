"""Generate SDK-style .NET project structure for examples."""

from __future__ import annotations

import logging
from pathlib import Path

from plugin_examples.generator.code_generator import GeneratedExample

logger = logging.getLogger(__name__)


def generate_project(
    example: GeneratedExample,
    *,
    package_id: str,
    target_framework: str = "net8.0",
    output_dir: Path,
) -> dict:
    """Generate an SDK-style .NET console project for an example.

    Args:
        example: Generated example with code.
        package_id: NuGet package ID (e.g., Aspose.Cells).
        target_framework: Target framework moniker.
        output_dir: Base output directory.

    Returns:
        Dict with project paths and metadata.
    """
    project_dir = output_dir / example.scenario_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write .csproj
    csproj_content = _generate_csproj(package_id, target_framework)
    csproj_path = project_dir / f"{example.scenario_id}.csproj"
    csproj_path.write_text(csproj_content)

    # Write Program.cs
    program_path = project_dir / "Program.cs"
    program_path.write_text(example.code)

    logger.info("Project generated: %s", project_dir)

    return {
        "scenario_id": example.scenario_id,
        "project_dir": str(project_dir),
        "csproj_path": str(csproj_path),
        "program_path": str(program_path),
        "target_framework": target_framework,
        "package_id": package_id,
        "claimed_symbols": example.claimed_symbols,
        "status": example.status,
    }


def _generate_csproj(package_id: str, target_framework: str) -> str:
    """Generate a minimal SDK-style .csproj."""
    return f"""<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{target_framework}</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="{package_id}" />
  </ItemGroup>

</Project>
"""
