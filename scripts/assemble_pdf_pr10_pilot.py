"""Assemble pdf-controlled-pilot-pr10 for the 5 template-repaired PDF examples.

These 5 examples were repaired in the multi-mega-train sprint via template_first:
  pdf-merger, pdf-optimizer, pdf-splitter, pdf-pdf-aconverter, pdf-text-extractor

Source: workspace/runs/pilot-pdf-repair-20260530/generated/pdf/
Destination: workspace/pr-dry-run/pdf-controlled-pilot-pr10/

This script is the repeatable pipeline mechanism (not a manual patch).
Same pattern as assemble_controlled_pilots.py.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PR_DRY_RUN = REPO_ROOT / "workspace" / "pr-dry-run"
SOURCE_RUN = "pilot-pdf-repair-20260530"

# The 5 examples to assemble (source dir name -> slug in package)
# Source dirs are named pdf-<slug> under generated/pdf/
EXAMPLES = [
    "pdf-merger",
    "pdf-optimizer",
    "pdf-splitter",
    "pdf-pdf-aconverter",
    "pdf-text-extractor",
]

COPY_FILES = {"Program.cs", "README.md", "expected-output.json", "example.manifest.json"}

PACKAGE_NAME = "pdf-controlled-pilot-pr10"
PACKAGE_ID = "Aspose.PDF"
PACKAGE_VERSION = "26.5.0"


def assemble_pr10():
    pkg_path = PR_DRY_RUN / PACKAGE_NAME
    pkg_path.mkdir(parents=True, exist_ok=True)

    # Directory.Build.props
    (pkg_path / "Directory.Build.props").write_text(
        "<Project>\n"
        "  <PropertyGroup>\n"
        "    <TargetFramework>net8.0</TargetFramework>\n"
        "    <OutputType>Exe</OutputType>\n"
        "    <Nullable>enable</Nullable>\n"
        "    <ImplicitUsings>enable</ImplicitUsings>\n"
        "  </PropertyGroup>\n"
        "</Project>\n",
        encoding="utf-8",
    )

    # Directory.Packages.props
    (pkg_path / "Directory.Packages.props").write_text(
        "<Project>\n"
        "  <PropertyGroup>\n"
        "    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>\n"
        "  </PropertyGroup>\n"
        "  <ItemGroup>\n"
        f"    <PackageVersion Include=\"{PACKAGE_ID}\" Version=\"{PACKAGE_VERSION}\" />\n"
        "  </ItemGroup>\n"
        "</Project>\n",
        encoding="utf-8",
    )

    # global.json
    (pkg_path / "global.json").write_text(
        json.dumps({"sdk": {"version": "8.0.100", "rollForward": "latestMajor"}}, indent=2),
        encoding="utf-8",
    )

    source_root = REPO_ROOT / "workspace" / "runs" / SOURCE_RUN / "generated" / "pdf"
    examples_lowcode = pkg_path / "examples" / "pdf" / "lowcode"

    print(f"\nAssembling {PACKAGE_NAME} from {SOURCE_RUN}...")
    assembled = []

    for example_name in EXAMPLES:
        src_dir = source_root / example_name
        if not src_dir.exists():
            print(f"  WARNING: source not found: {src_dir}")
            continue

        # Slug: strip 'pdf-' prefix
        slug = example_name[4:]  # "pdf-merger" -> "merger"

        dest_dir = examples_lowcode / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy specific files
        for fname in COPY_FILES:
            src_file = src_dir / fname
            if src_file.exists():
                shutil.copy2(src_file, dest_dir / fname)

        # Copy .csproj (rename to match slug)
        for src_file in src_dir.glob("*.csproj"):
            dest_name = f"{slug}.csproj"
            shutil.copy2(src_file, dest_dir / dest_name)

        assembled.append(slug)
        print(f"  + {slug}")

    print(f"\nPackage: {pkg_path}")
    print(f"Assembled {len(assembled)}/{len(EXAMPLES)} examples: {assembled}")
    return pkg_path, assembled


def verify_build(pkg_path: Path):
    """Run dotnet build to verify the package builds."""
    import subprocess
    print(f"\nVerifying build: {pkg_path}")
    result = subprocess.run(
        ["dotnet", "build", "--nologo", "-v", "q"],
        cwd=pkg_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0:
        print("  BUILD: PASS")
    else:
        print(f"  BUILD: FAIL (exit {result.returncode})")
        print(result.stdout[-2000:] if result.stdout else "")
        print(result.stderr[-2000:] if result.stderr else "")
    return result.returncode == 0


if __name__ == "__main__":
    pkg_path, assembled = assemble_pr10()
    if assembled:
        verify_build(pkg_path)
    print("\nDone.")
