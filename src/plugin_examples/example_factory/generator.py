"""Registry-driven example package generator."""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

from ..plugin_code_registry.models import PluginEntry
from .templates import FamilyTemplate, FamilyTemplateRegistry

CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>{TARGET}</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{PACKAGE}" Version="{VERSION}" />
{EXTRA_PACKAGES}  </ItemGroup>
</Project>
"""

README_TEMPLATE = """\
# {TITLE}

**Family**: {FAMILY}
**Plugin**: {SLUG}
**Canonical URL**: {CANONICAL_URL}
**Package**: {PACKAGE} {VERSION}
**Implementation Model**: {IMPL_MODEL}

## Prerequisites

- .NET 8 SDK
- NuGet package: `{PACKAGE}` (auto-restored)

## Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Output

Output file(s) will be generated in the `output/` directory.

## Source Provenance

See `source-provenance.json` for canonical page and code evidence links.

{TRIAL_CAVEAT}
"""

SOURCE_PROVENANCE_TEMPLATE = """\
{{
  "family": "{FAMILY}",
  "plugin_slug": "{SLUG}",
  "canonical_url": "{CANONICAL_URL}",
  "implementation_model": "{IMPL_MODEL}",
  "nuget_package": "{PACKAGE}",
  "nuget_version": "{VERSION}",
  "github_links": {GITHUB_LINKS},
  "code_hashes": {CODE_HASHES},
  "sprint": "{SPRINT}",
  "generated_at": "{GENERATED_AT}"
}}
"""

PACKAGE_MANIFEST_TEMPLATE = """\
{{
  "family": "{FAMILY}",
  "plugin_slug": "{SLUG}",
  "canonical_url": "{CANONICAL_URL}",
  "implementation_model": "{IMPL_MODEL}",
  "nuget_package": "{PACKAGE}",
  "nuget_version": "{VERSION}",
  "sprint": "{SPRINT}",
  "generated_at": "{GENERATED_AT}",
  "dryrun_root": "{DRYRUN_ROOT}",
  "required_files": ["Program.cs", "README.md", "source-provenance.json", "output-validation.json"],
  "external_repo_write": false,
  "publication_pr_created": false
}}
"""


_EXTERNAL_REPO_PREFIXES = (
    ".local/clones/",
    "external/",
)


def _guard_no_external_write(path: Path) -> None:
    """Raise if path is inside an external repo clone directory."""
    path_str = str(path).replace("\\", "/")
    for prefix in _EXTERNAL_REPO_PREFIXES:
        if prefix in path_str:
            raise ValueError(f"SAFETY: write to external repo path blocked: {path}")


class ExamplePackageGenerator:
    """Generates dry-run example packages from registry entries."""

    SPRINT = "lowcode-plugin-example-factory-parallel-wave-20260605"
    GENERATED_AT = "2026-06-05"

    def __init__(
        self,
        output_root: Path,
        template_registry: FamilyTemplateRegistry | None = None,
        sprint: str = SPRINT,
        generated_at: str = GENERATED_AT,
    ):
        self.output_root = output_root
        self.templates = template_registry or FamilyTemplateRegistry()
        self.sprint = sprint
        self.generated_at = generated_at
        _guard_no_external_write(output_root)

    def package_dir(self, entry: PluginEntry) -> Path:
        return self.output_root / entry.family / entry.plugin_slug

    def generate_scaffold(self, entry: PluginEntry, program_cs: str, extra_packages: list | None = None) -> Path:
        """Generate the package scaffold (csproj, README, provenance). Returns package dir."""
        template = self.templates.get(entry.family)
        if not template:
            raise ValueError(f"No template for family '{entry.family}'")

        pkg_dir = self.package_dir(entry)
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "output").mkdir(exist_ok=True)

        # .csproj
        extra_pkg_lines = ""
        if extra_packages:
            extra_pkg_lines = (
                "\n".join(f'    <PackageReference Include="{p}" Version="{v}" />' for p, v in extra_packages) + "\n"
            )

        csproj_content = CSPROJ_TEMPLATE.format(
            TARGET=template.dotnet_target,
            PACKAGE=template.nuget_package,
            VERSION=template.nuget_version,
            EXTRA_PACKAGES=extra_pkg_lines,
        )
        (pkg_dir / f"{entry.family}-{entry.plugin_slug}.csproj").write_text(csproj_content)

        # Program.cs
        (pkg_dir / "Program.cs").write_text(program_cs, encoding="utf-8")

        # README.md
        trial_caveat = f"\n## Trial Mode Note\n\n{template.trial_caveat}\n" if template.trial_caveat else ""
        readme = README_TEMPLATE.format(
            TITLE=f"{entry.family}/{entry.plugin_slug}",
            FAMILY=entry.family,
            SLUG=entry.plugin_slug,
            CANONICAL_URL=entry.canonical_url or "N/A",
            PACKAGE=template.nuget_package,
            VERSION=template.nuget_version,
            IMPL_MODEL=entry.implementation_model or "N/A",
            TRIAL_CAVEAT=trial_caveat,
        )
        (pkg_dir / "README.md").write_text(readme)

        # source-provenance.json
        provenance = SOURCE_PROVENANCE_TEMPLATE.format(
            FAMILY=entry.family,
            SLUG=entry.plugin_slug,
            CANONICAL_URL=entry.canonical_url or "",
            IMPL_MODEL=entry.implementation_model or "",
            PACKAGE=template.nuget_package,
            VERSION=template.nuget_version,
            GITHUB_LINKS=json.dumps(entry.github_links),
            CODE_HASHES=json.dumps(entry.code_hashes),
            SPRINT=self.sprint,
            GENERATED_AT=self.generated_at,
        )
        (pkg_dir / "source-provenance.json").write_text(provenance)

        # package-manifest.json
        manifest = PACKAGE_MANIFEST_TEMPLATE.format(
            FAMILY=entry.family,
            SLUG=entry.plugin_slug,
            CANONICAL_URL=entry.canonical_url or "",
            IMPL_MODEL=entry.implementation_model or "",
            PACKAGE=template.nuget_package,
            VERSION=template.nuget_version,
            SPRINT=self.sprint,
            GENERATED_AT=self.generated_at,
            DRYRUN_ROOT=str(self.output_root),
        )
        (pkg_dir / "package-manifest.json").write_text(manifest)

        return pkg_dir

    def build_and_run(self, pkg_dir: Path) -> dict:
        """Run dotnet restore, build, run. Returns result dict with logs."""
        result: dict[str, Any] = {"restore": None, "build": None, "run": None, "output_files": [], "verdict": "UNKNOWN"}

        for step, cmd in [
            ("restore", ["dotnet", "restore"]),
            ("build", ["dotnet", "build"]),
            ("run", ["dotnet", "run"]),
        ]:
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(pkg_dir), timeout=120)
            log = proc.stdout + proc.stderr
            result[step] = {
                "exit_code": proc.returncode,
                "log": log,
                "status": "SUCCESS" if proc.returncode == 0 else "FAILED",
            }
            log_path = pkg_dir / f"{step}.log"
            log_path.write_text(log)
            if proc.returncode != 0 and step != "run":
                result["verdict"] = f"{step.upper()}_FAILED"
                return result

        # Check outputs
        output_dir = pkg_dir / "output"
        if output_dir.exists():
            for f in output_dir.iterdir():
                if f.is_file():
                    result["output_files"].append({"path": str(f), "size": f.stat().st_size})

        has_output = any(o["size"] > 0 for o in result["output_files"])
        run_ok = result["run"]["exit_code"] == 0
        result["verdict"] = "PASS" if (run_ok and has_output) else ("RUN_FAILED" if not run_ok else "OUTPUT_MISSING")

        # Write output-validation.json
        validation = {
            "package_dir": str(pkg_dir),
            "restore_status": result["restore"]["status"],
            "build_status": result["build"]["status"],
            "run_status": result["run"]["status"],
            "output_files": result["output_files"],
            "verdict": result["verdict"],
        }
        (pkg_dir / "output-validation.json").write_text(json.dumps(validation, indent=2))

        return result
