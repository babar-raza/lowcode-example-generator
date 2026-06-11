"""Family-specific template definitions for dry-run example generation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FamilyTemplate:
    family: str
    implementation_model: str
    nuget_package: str
    nuget_version: str
    dotnet_target: str = "net8.0"
    fixture_strategy: str = "none"
    fixture_description: str = ""
    output_format: str = "unknown"
    trial_caveat: Optional[str] = None
    known_limitations: list = field(default_factory=list)
    # Template code snippet (placeholder-based)
    program_cs_template: str = ""
    csproj_template: str = ""


FAMILY_TEMPLATES: dict[str, FamilyTemplate] = {
    "barcode": FamilyTemplate(
        family="barcode",
        implementation_model="STATIC_CONVERTER_CLASS",
        nuget_package="Aspose.BarCode",
        nuget_version="24.12.0",
        fixture_strategy="none",
        fixture_description="BarcodeGenerator creates output directly; no input fixture",
        output_format="PNG",
        trial_caveat="Trial mode adds evaluation watermark overlay on barcode image",
        program_cs_template="""// {PLUGIN_TITLE}
// Canonical: {CANONICAL_URL}
// Package: Aspose.BarCode {NUGET_VERSION}
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System.IO;
using System;

Directory.CreateDirectory("output");
// {PATTERN_COMMENT}
{CORE_CODE}
Console.WriteLine($"Output: {OUTPUT_FILE}");
""",
    ),
    "imaging": FamilyTemplate(
        family="imaging",
        implementation_model="LOAD_SAVE_OPTIONS",
        nuget_package="Aspose.Imaging",
        nuget_version="24.12.0",
        fixture_strategy="programmatic",
        fixture_description="Generate minimal BMP programmatically via Aspose.Imaging RasterImage",
        output_format="PNG/JPEG",
        trial_caveat="Trial mode adds evaluation watermark on output images",
        known_limitations=["System.Drawing not used; pure Aspose.Imaging for cross-platform support"],
    ),
    "zip": FamilyTemplate(
        family="zip",
        implementation_model="LOAD_SAVE_OPTIONS",
        nuget_package="Aspose.ZIP",
        nuget_version="24.12.0",
        fixture_strategy="programmatic",
        fixture_description="Create temp files/dir in code; no external fixture needed",
        output_format="ZIP",
    ),
    "html": FamilyTemplate(
        family="html",
        implementation_model="STATIC_CONVERTER_CLASS",
        nuget_package="Aspose.HTML",
        nuget_version="24.12.0",
        fixture_strategy="inline",
        fixture_description="HTML content is an inline string; no file fixture needed",
        output_format="PDF",
    ),
    "tasks": FamilyTemplate(
        family="tasks",
        implementation_model="LOAD_SAVE_OPTIONS",
        nuget_package="Aspose.Tasks",
        nuget_version="24.12.0",
        fixture_strategy="programmatic",
        fixture_description="Create Project() programmatically; no .mpp fixture needed",
        output_format="PDF",
    ),
    "svg": FamilyTemplate(
        family="svg",
        implementation_model="STATIC_CONVERTER_CLASS",
        nuget_package="Aspose.SVG",
        nuget_version="24.12.0",
        fixture_strategy="inline",
        fixture_description="SVG content is an inline XML string; no file fixture needed",
        output_format="PNG/PDF",
    ),
    "tex": FamilyTemplate(
        family="tex",
        implementation_model="DEDICATED_PLUGIN_CLASS",
        nuget_package="Aspose.TeX",
        nuget_version="24.12.0",
        fixture_strategy="inline",
        fixture_description="LaTeX formula/figure is an inline string; no file fixture needed",
        output_format="PNG",
        known_limitations=["FigureRendererPlugin requires TikZ environment support"],
    ),
    "ocr": FamilyTemplate(
        family="ocr",
        implementation_model="RECOGNITION_EXTRACTION_API",
        nuget_package="Aspose.OCR",
        nuget_version="24.12.0",
        fixture_strategy="programmatic",
        fixture_description="Generate test PNG using System.Drawing (Windows) or bundle minimal PNG",
        output_format="TXT",
        trial_caveat="Trial mode appends 'Trial License' text to recognition results",
    ),
    "psd": FamilyTemplate(
        family="psd",
        implementation_model="LOAD_SAVE_OPTIONS",
        nuget_package="Aspose.PSD",
        nuget_version="24.12.0",
        fixture_strategy="file",
        fixture_description=".psd fixture required; cannot generate programmatically",
        output_format="JPEG",
        known_limitations=["Requires .psd fixture file from GitHub examples repo"],
    ),
    "cad": FamilyTemplate(
        family="cad",
        implementation_model="LOAD_SAVE_OPTIONS",
        nuget_package="Aspose.CAD",
        nuget_version="24.12.0",
        fixture_strategy="file",
        fixture_description=".dwg/.dxf fixture required; cannot generate programmatically",
        output_format="PDF",
        known_limitations=["Requires .dwg/.dxf fixture file; deferred to Wave B"],
    ),
    "page": FamilyTemplate(
        family="page",
        implementation_model="DEDICATED_PLUGIN_CLASS",
        nuget_package="Aspose.Page",
        nuget_version="24.12.0",
        fixture_strategy="file",
        fixture_description=".ps/.xps fixture required",
        output_format="PDF",
        known_limitations=["Requires .ps or .xps fixture; deferred to Wave B"],
    ),
}


class FamilyTemplateRegistry:
    """Provides family templates for example generation."""

    def get(self, family: str) -> FamilyTemplate | None:
        return FAMILY_TEMPLATES.get(family)

    def available_families(self) -> list:
        return list(FAMILY_TEMPLATES.keys())

    def fixture_free_families(self) -> list:
        return [f for f, t in FAMILY_TEMPLATES.items() if t.fixture_strategy in ("none", "inline")]

    def template_map(self) -> dict:
        return {
            f: {
                "nuget_package": t.nuget_package,
                "nuget_version": t.nuget_version,
                "implementation_model": t.implementation_model,
                "fixture_strategy": t.fixture_strategy,
                "output_format": t.output_format,
            }
            for f, t in FAMILY_TEMPLATES.items()
        }
