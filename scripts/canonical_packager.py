"""Canonical packager — generalized assembly of any LowCode example package.

Replaces hardcoded scripts like assemble_pdf_pr10_pilot.py.

Usage (manifest-driven):
  python scripts/canonical_packager.py --manifest path/to/assemble-manifest.json

Usage (CLI):
  python scripts/canonical_packager.py \\
    --family pdf \\
    --package-name pdf-controlled-pilot-pr10 \\
    --package-id Aspose.PDF \\
    --package-version 26.5.0 \\
    --source-run workspace/runs/pilot-pdf-repair-20260530/generated/pdf \\
    --family-prefix pdf \\
    [--examples merger optimizer splitter] \\
    [--verify-build]

Assemble manifest schema:
  {
    "family": "pdf",
    "package_name": "pdf-controlled-pilot-pr10",
    "package_id": "Aspose.PDF",
    "package_version": "26.5.0",
    "source_run": "workspace/runs/pilot-pdf-repair-20260530/generated/pdf",
    "family_prefix": "pdf",
    "examples": ["pdf-merger", "pdf-optimizer"],  // optional — auto-discovers if omitted
    "verify_build": true
  }
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PR_DRY_RUN = REPO_ROOT / "workspace" / "pr-dry-run"

COPY_FILES = {"Program.cs", "README.md", "expected-output.json", "example.manifest.json"}

# Directories to skip when copying example content
SKIP_DIRS = {"bin", "obj", ".vs"}

# Extensions to copy as fixture/data files
FIXTURE_EXTENSIONS = {
    ".docx", ".xlsx", ".pptx", ".vsdx", ".pdf", ".html", ".htm",
    ".xml", ".json", ".txt", ".msg", ".eml", ".csv",
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".svg",
}

DIRECTORY_BUILD_PROPS = """\
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
"""

DIRECTORY_PACKAGES_PROPS_TEMPLATE = """\
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="{package_id}" Version="{package_version}" />
  </ItemGroup>
</Project>
"""

GLOBAL_JSON = json.dumps(
    {"sdk": {"version": "8.0.100", "rollForward": "latestMajor"}}, indent=2
)


def discover_examples(source_root: Path, family_prefix: str) -> list[str]:
    """Auto-discover example directories in source_root matching family_prefix-<slug>."""
    dirs = sorted(
        d.name for d in source_root.iterdir()
        if d.is_dir() and d.name.startswith(f"{family_prefix}-")
    )
    return dirs


def assemble_package(
    family: str,
    package_name: str,
    package_id: str,
    package_version: str,
    source_run: str | Path,
    family_prefix: str,
    examples: list[str] | None = None,
    verify_build: bool = False,
) -> dict:
    source_root = REPO_ROOT / source_run if not Path(source_run).is_absolute() else Path(source_run)

    if examples is None:
        examples = discover_examples(source_root, family_prefix)
        print(f"Auto-discovered {len(examples)} examples: {examples}")

    pkg_path = PR_DRY_RUN / package_name
    pkg_path.mkdir(parents=True, exist_ok=True)

    # Write package scaffolding files
    (pkg_path / "Directory.Build.props").write_text(DIRECTORY_BUILD_PROPS, encoding="utf-8")
    (pkg_path / "Directory.Packages.props").write_text(
        DIRECTORY_PACKAGES_PROPS_TEMPLATE.format(
            package_id=package_id, package_version=package_version
        ),
        encoding="utf-8",
    )
    (pkg_path / "global.json").write_text(GLOBAL_JSON, encoding="utf-8")

    prefix_len = len(family_prefix) + 1  # len("pdf-")
    examples_lowcode = pkg_path / "examples" / family / "lowcode"
    assembled = []
    warnings = []

    print(f"\nAssembling {package_name} from {source_root.name}...")

    for example_name in examples:
        src_dir = source_root / example_name
        if not src_dir.exists():
            warnings.append(f"source not found: {src_dir}")
            print(f"  WARNING: source not found: {src_dir}")
            continue

        # Derive slug: strip "family-" prefix
        slug = example_name[prefix_len:] if example_name.startswith(f"{family_prefix}-") else example_name
        dest_dir = examples_lowcode / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy named standard files
        for fname in COPY_FILES:
            src_file = src_dir / fname
            if src_file.exists():
                shutil.copy2(src_file, dest_dir / fname)

        # Copy .csproj (renamed to slug)
        for src_file in src_dir.glob("*.csproj"):
            shutil.copy2(src_file, dest_dir / f"{slug}.csproj")
            break  # only first csproj

        # Copy fixture/data files (all top-level files with known fixture extensions)
        for src_file in src_dir.iterdir():
            if src_file.is_file() and src_file.suffix.lower() in FIXTURE_EXTENSIONS:
                if not (dest_dir / src_file.name).exists():  # don't overwrite already-copied
                    shutil.copy2(src_file, dest_dir / src_file.name)

        assembled.append(slug)
        print(f"  + {slug}")

    print(f"\nPackage: {pkg_path}")
    print(f"Assembled {len(assembled)}/{len(examples)} examples: {assembled}")

    build_result = None
    if verify_build and assembled:
        build_result = _verify_build(pkg_path)

    return {
        "package_path": str(pkg_path),
        "examples_requested": len(examples),
        "examples_assembled": len(assembled),
        "assembled": assembled,
        "warnings": warnings,
        "build_pass": build_result,
    }


def _verify_build(pkg_path: Path) -> bool:
    """Build each example csproj individually (package root has no solution file)."""
    csproj_files = sorted(pkg_path.glob("examples/**/*.csproj"))
    if not csproj_files:
        print(f"  WARNING: no .csproj files found under {pkg_path.name}")
        return False

    print(f"\nVerifying build: {pkg_path.name} ({len(csproj_files)} project(s))")
    all_pass = True
    for csproj in csproj_files:
        result = subprocess.run(
            ["dotnet", "build", str(csproj), "--nologo", "-v", "q"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"  [{status}] {csproj.parent.name}")
        if result.returncode != 0:
            all_pass = False
            out = (result.stdout or "") + (result.stderr or "")
            print(out[-1500:] if out else "(no output)")
    return all_pass


def _load_manifest(manifest_path: Path) -> dict:
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Canonical packager for LowCode examples.")
    parser.add_argument("--manifest", help="Path to assemble-manifest.json")
    parser.add_argument("--family", help="Family name (e.g. pdf, words, cells)")
    parser.add_argument("--package-name", dest="package_name", help="Output package directory name")
    parser.add_argument("--package-id", dest="package_id", help="NuGet package ID")
    parser.add_argument("--package-version", dest="package_version", help="NuGet package version")
    parser.add_argument("--source-run", dest="source_run", help="Source run directory (relative to repo root)")
    parser.add_argument("--family-prefix", dest="family_prefix", help="Family prefix used in example dirs (e.g. 'pdf')")
    parser.add_argument("--examples", nargs="*", help="Explicit list of example dir names")
    parser.add_argument("--verify-build", dest="verify_build", action="store_true", default=False)
    args = parser.parse_args()

    if args.manifest:
        cfg = _load_manifest(Path(args.manifest))
    elif args.family and args.package_name and args.package_id and args.source_run:
        cfg = {
            "family": args.family,
            "package_name": args.package_name,
            "package_id": args.package_id,
            "package_version": args.package_version or "*",
            "source_run": args.source_run,
            "family_prefix": args.family_prefix or args.family,
            "examples": args.examples or None,
            "verify_build": args.verify_build,
        }
    else:
        parser.print_help()
        sys.exit(1)

    result = assemble_package(
        family=cfg["family"],
        package_name=cfg["package_name"],
        package_id=cfg["package_id"],
        package_version=cfg.get("package_version", "*"),
        source_run=cfg["source_run"],
        family_prefix=cfg.get("family_prefix", cfg["family"]),
        examples=cfg.get("examples"),
        verify_build=cfg.get("verify_build", False),
    )

    print(f"\nResult: {json.dumps(result, indent=2)}")
    if result["build_pass"] is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
