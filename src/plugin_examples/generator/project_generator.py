"""Generate SDK-style .NET project structure for examples."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.generator.code_generator import GeneratedExample

logger = logging.getLogger(__name__)


def generate_project(
    example: GeneratedExample,
    *,
    package_id: str,
    package_version: str = "*",
    target_framework: str = "net8.0",
    output_dir: Path,
    input_strategy: str = "none",
    input_files: list[str] | None = None,
) -> dict:
    """Generate an SDK-style .NET console project for an example.

    Args:
        example: Generated example with code.
        package_id: NuGet package ID (e.g., Aspose.Cells).
        target_framework: Target framework moniker.
        output_dir: Base output directory.
        input_strategy: How input files are provided.
        input_files: List of input filenames for the project.

    Returns:
        Dict with project paths and metadata.
    """
    input_files = input_files or []
    project_dir = output_dir / example.scenario_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # Ensure run-level build files exist
    _ensure_run_level_files(output_dir.parent, package_id, package_version, target_framework)

    # Generate fixture files if strategy requires them
    placed_fixtures: list[str] = []
    if input_strategy in ("generated_fixture_file", "existing_fixture") and input_files:
        from plugin_examples.fixture_registry.fixture_factory import generate_fixtures_for_scenario
        fixtures = generate_fixtures_for_scenario(input_files, project_dir)
        placed_fixtures = [f.path for f in fixtures if f.ready]

    # Write .csproj with fixture copy entries if needed
    csproj_content = _generate_csproj(package_id, target_framework, input_files if placed_fixtures else [])
    csproj_path = project_dir / f"{example.scenario_id}.csproj"
    csproj_path.write_text(csproj_content)

    # Write Program.cs
    program_path = project_dir / "Program.cs"
    program_path.write_text(example.code, encoding="utf-8")

    # Write README.md
    readme_path = project_dir / "README.md"
    readme_path.write_text(_generate_readme(example, package_id, target_framework), encoding="utf-8")

    # Write example.manifest.json
    manifest_path = project_dir / "example.manifest.json"
    manifest_data = {
        "scenario_id": example.scenario_id,
        "package_id": package_id,
        "package_version": package_version,
        "target_framework": target_framework,
        "claimed_symbols": example.claimed_symbols,
        "status": example.status,
        "input_strategy": input_strategy,
        "input_files": input_files,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2))

    # Write expected-output.json with semantic validation rules
    expected_output_path = project_dir / "expected-output.json"
    expected_output = {
        "must_contain": [f"Example: {example.scenario_id}"],
        "must_not_contain": ["Unhandled exception", "System.Exception",
                             "Console.ReadKey", "Console.ReadLine"],
        "has_output": True,
        "input_dependencies": input_files,
        "forbidden_code_patterns": [
            "Console.ReadKey(", "Console.ReadLine(",
            "TODO", "NotImplementedException",
        ],
    }
    expected_output_path.write_text(json.dumps(expected_output, indent=2))

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
        "input_strategy": input_strategy,
        "input_files": input_files,
        "placed_fixtures": placed_fixtures,
    }


def _ensure_run_level_files(
    run_generated_dir: Path,
    package_id: str,
    package_version: str,
    target_framework: str,
) -> None:
    """Write Directory.Packages.props, Directory.Build.props, and global.json at run level."""
    packages_props = run_generated_dir / "Directory.Packages.props"
    if not packages_props.exists():
        packages_props.write_text(f"""<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="{package_id}" Version="{package_version}" />
  </ItemGroup>
</Project>
""")

    build_props = run_generated_dir / "Directory.Build.props"
    if not build_props.exists():
        build_props.write_text(f"""<Project>
  <PropertyGroup>
    <TargetFramework>{target_framework}</TargetFramework>
    <OutputType>Exe</OutputType>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
""")

    global_json = run_generated_dir / "global.json"
    if not global_json.exists():
        global_json.write_text(json.dumps({
            "sdk": {"version": "8.0.100", "rollForward": "latestMajor"},
        }, indent=2))


def _generate_csproj(package_id: str, target_framework: str, input_files: list[str] | None = None) -> str:
    """Generate a minimal SDK-style .csproj — version managed by Directory.Packages.props."""
    fixture_items = ""
    if input_files:
        lines = []
        for f in input_files:
            lines.append(f'    <None Include="{f}">')
            lines.append(f'      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>')
            lines.append(f'    </None>')
        fixture_items = "\n\n  <ItemGroup>\n" + "\n".join(lines) + "\n  </ItemGroup>"

    return f"""<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{target_framework}</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="{package_id}" />
  </ItemGroup>{fixture_items}

</Project>
"""


def _generate_readme(example: GeneratedExample, package_id: str, target_framework: str) -> str:
    """Generate a README.md for an example project."""
    symbols = ", ".join(f"`{s}`" for s in example.claimed_symbols[:5]) if example.claimed_symbols else "N/A"
    return f"""# {example.scenario_id}

Auto-generated example for **{package_id}** ({target_framework}).

## API Symbols Used

{symbols}

## Run

```bash
dotnet restore
dotnet build
dotnet run
```
"""
