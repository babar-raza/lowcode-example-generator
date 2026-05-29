"""Assemble cells and words controlled-pilot packages from verified examples.

Creates the package structure needed by render-root-readme and publish-readme tests.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PR_DRY_RUN = REPO_ROOT / "workspace" / "pr-dry-run"

# Families to assemble
FAMILIES = {
    "cells": {
        "source_run": "pilot-cells-final-20260528",
        "package_id": "Aspose.Cells",
        "package_version": "25.5.0",
    },
    "words": {
        "source_run": "pilot-words-heal2-20260528",
        "package_id": "Aspose.Words",
        "package_version": "25.5.0",
    },
}

# Files to copy from generated example (exclude build artifacts)
COPY_EXTENSIONS = {".cs", ".csproj", ".json", ".md"}
COPY_FILES = {"Program.cs", "README.md", "expected-output.json", "example.manifest.json"}


def get_example_dirs(source_run: str, family: str) -> list[Path]:
    """Get all generated example dirs for a family from a source run."""
    gen_dir = REPO_ROOT / "workspace" / "runs" / source_run / "generated" / family
    if not gen_dir.exists():
        return []
    return sorted(d for d in gen_dir.iterdir() if d.is_dir() and d.name.startswith(family))


def assemble_family(family: str, config: dict):
    pkg_name = f"{family}-controlled-pilot"
    pkg_path = PR_DRY_RUN / pkg_name
    examples_lowcode = pkg_path / "examples" / family / "lowcode"

    print(f"\nAssembling {pkg_name}...")

    # Create package root files
    pkg_path.mkdir(parents=True, exist_ok=True)

    # Directory.Build.props
    (pkg_path / "Directory.Build.props").write_text(
        '<Project>\n'
        '  <PropertyGroup>\n'
        '    <TargetFramework>net8.0</TargetFramework>\n'
        '    <OutputType>Exe</OutputType>\n'
        '    <Nullable>enable</Nullable>\n'
        '    <ImplicitUsings>enable</ImplicitUsings>\n'
        '  </PropertyGroup>\n'
        '</Project>\n',
        encoding="utf-8",
    )

    # Directory.Packages.props
    pkg_id = config["package_id"]
    pkg_ver = config["package_version"]
    (pkg_path / "Directory.Packages.props").write_text(
        '<Project>\n'
        '  <PropertyGroup>\n'
        '    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>\n'
        '  </PropertyGroup>\n'
        '  <ItemGroup>\n'
        f'    <PackageVersion Include="{pkg_id}" Version="{pkg_ver}" />\n'
        '  </ItemGroup>\n'
        '</Project>\n',
        encoding="utf-8",
    )

    # global.json
    (pkg_path / "global.json").write_text(
        json.dumps({"sdk": {"version": "8.0.100", "rollForward": "latestMajor"}}, indent=2),
        encoding="utf-8",
    )

    # Copy examples
    source_dirs = get_example_dirs(config["source_run"], family)
    print(f"  Found {len(source_dirs)} example dirs in {config['source_run']}")

    for src_dir in source_dirs:
        # Example slug: strip family prefix
        slug = src_dir.name[len(family) + 1:]  # e.g. "cells-html-converter" -> "html-converter"
        dest_dir = examples_lowcode / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy specific files
        for fname in COPY_FILES:
            src_file = src_dir / fname
            if src_file.exists():
                shutil.copy2(src_file, dest_dir / fname)

        # Copy .csproj (renamed)
        for src_file in src_dir.glob("*.csproj"):
            # Rename to match slug
            dest_name = f"{slug}.csproj"
            shutil.copy2(src_file, dest_dir / dest_name)

        print(f"  + {slug}")

    print(f"  Package: {pkg_path}")
    return pkg_path


def main():
    for family, config in FAMILIES.items():
        assemble_family(family, config)
    print("\nDone.")


if __name__ == "__main__":
    main()
