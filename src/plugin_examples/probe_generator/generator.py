"""Probe generator: validates candidates against reflection and renders probe C# code.

Enforces PR-01 through PR-03 before generating any code:
  PR-01: type_name must exist in catalog.types[].name (exact match)
  PR-02: method_name must exist in that type's methods[].name (exact match)
  PR-03: type must not be abstract or interface; must have public constructor or static factory
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from plugin_examples.plugin_detector.heuristic_matcher import (
    CandidateMapping,
    ReflectionCatalog,
)

# Jinja2 template paths
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_CS_TEMPLATE = _TEMPLATES_DIR / "console_probe.cs.j2"
_CSPROJ_TEMPLATE = _TEMPLATES_DIR / "console_probe.csproj.j2"


class CandidateNotReflectedError(ValueError):
    """Raised when the candidate type or method is not confirmed in DllReflector output."""


@dataclass
class ProbeFiles:
    """Generated probe code files."""
    cs_path: Path
    csproj_path: Path
    cs_content: str
    csproj_content: str


class ProbeGenerator:
    """Validate a CandidateMapping against the reflection catalog and generate probe code.

    All three probe rules must pass before any code is written:
      PR-01: type in catalog
      PR-02: method in type
      PR-03: not abstract/interface; has constructor or static factory
    """

    def validate_candidate(
        self, candidate: CandidateMapping, catalog: ReflectionCatalog
    ) -> None:
        """Validate candidate against catalog.

        Raises:
            CandidateNotReflectedError: if PR-01, PR-02, or PR-03 fail.
        """
        type_info = next(
            (t for t in catalog.types if t.name == candidate.type_name), None
        )
        if type_info is None:
            raise CandidateNotReflectedError(
                f"PR-01 FAIL: type '{candidate.type_name}' not found in catalog"
            )

        method_found = any(m.name == candidate.method_name for m in type_info.methods)
        if not method_found:
            raise CandidateNotReflectedError(
                f"PR-02 FAIL: method '{candidate.method_name}' not found on type '{candidate.type_name}'"
            )

        if type_info.is_abstract or type_info.is_interface:
            raise CandidateNotReflectedError(
                f"PR-03 FAIL: type '{candidate.type_name}' is abstract or interface"
            )
        has_factory = any(m.is_static for m in type_info.methods)
        if not type_info.has_public_constructor and not has_factory:
            raise CandidateNotReflectedError(
                f"PR-03 FAIL: type '{candidate.type_name}' has no public constructor or static factory"
            )

    def generate(
        self,
        candidate: CandidateMapping,
        catalog: ReflectionCatalog,
        package_id: str,
        package_version: str,
        output_dir: Path,
    ) -> ProbeFiles:
        """Generate probe C# code after validating the candidate.

        Args:
            candidate: The CandidateMapping (must be PROBE_CANDIDATE status).
            catalog: DllReflector reflection catalog.
            package_id: NuGet package ID (e.g. Aspose.BarCode).
            package_version: Package version string.
            output_dir: Directory where probe files will be written.

        Returns:
            ProbeFiles with paths and content of generated files.

        Raises:
            CandidateNotReflectedError: if validation fails.
        """
        self.validate_candidate(candidate, catalog)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cs_content = self._render_cs(candidate, package_id)
        csproj_content = self._render_csproj(package_id, package_version)

        cs_path = output_dir / "Program.cs"
        csproj_path = output_dir / f"{_slug(candidate.type_name)}Probe.csproj"

        cs_path.write_text(cs_content, encoding="utf-8")
        csproj_path.write_text(csproj_content, encoding="utf-8")

        return ProbeFiles(
            cs_path=cs_path,
            csproj_path=csproj_path,
            cs_content=cs_content,
            csproj_content=csproj_content,
        )

    def _render_cs(self, candidate: CandidateMapping, package_id: str) -> str:
        return _CS_TEMPLATE_CONTENT.format(
            namespace=candidate.namespace,
            type_name=candidate.type_name,
            method_name=candidate.method_name,
            package_id=package_id,
        )

    def _render_csproj(self, package_id: str, package_version: str) -> str:
        return _CSPROJ_TEMPLATE_CONTENT.format(
            package_id=package_id,
            package_version=package_version,
        )


def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


# Inline templates (avoids Jinja2 dependency for core probe generation)
_CS_TEMPLATE_CONTENT = """\
// Auto-generated probe — DO NOT EDIT
// PR-01 and PR-02 confirmed before this file was generated.
using System;
using {namespace};

var outputPath = args.Length > 0 ? args[0] : "probe-output.bin";
var obj = new {type_name}();
obj.{method_name}(outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""

_CSPROJ_TEMPLATE_CONTENT = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{package_id}" Version="{package_version}" />
  </ItemGroup>
</Project>
"""
