"""Registry probe generator: render probe C# code from capability-registry entries.

Unlike ProbeGenerator (which requires CandidateMapping + ReflectionCatalog),
this module generates probe code directly from registry entry dicts using
family-aware templates derived from proven W18-W20 sprint patterns.

Each family template reads the entry's ``selected_api_mapping`` fields to
render C# that actually matches the API's usage pattern (constructors,
factory methods, save options, etc.).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProbeFiles:
    """Generated probe code files."""

    cs_path: Path
    csproj_path: Path
    cs_content: str
    csproj_content: str


class NoApiMappingError(ValueError):
    """Raised when a registry entry has no usable API mapping and no family renderer.

    This is a clean failure — not a code bug. The registry entry needs either a
    type_name+namespace populated via DLL reflection, or a family-specific renderer
    registered in _FAMILY_RENDERERS.
    """


# ---------------------------------------------------------------------------
# Family-specific C# template renderers
# ---------------------------------------------------------------------------

def _render_drawing_convert(entry: dict, _mapping: dict) -> str:
    """Drawing conversion: Bitmap(filename) -> Save(outputPath, ImageFormat)."""
    return """\
// Auto-generated registry probe — Aspose.Drawing convert
using System;
using System.Drawing;
using System.Drawing.Imaging;

var outputPath = args.Length > 0 ? args[0] : "probe-output.png";
// Create a simple bitmap and save it
using var bmp = new Bitmap(100, 100);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.White);
g.DrawString("Probe", SystemFonts.DefaultFont, Brushes.Black, 10, 10);
bmp.Save(outputPath, ImageFormat.Png);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_drawing_create(entry: dict, _mapping: dict) -> str:
    """Drawing creation: Bitmap(w,h) -> Graphics -> draw -> Save."""
    return """\
// Auto-generated registry probe — Aspose.Drawing create
using System;
using System.Drawing;
using System.Drawing.Imaging;

var outputPath = args.Length > 0 ? args[0] : "probe-output.png";
using var bmp = new Bitmap(200, 200);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.CornflowerBlue);
g.DrawRectangle(Pens.Red, 20, 20, 160, 160);
g.DrawString("Hello Drawing", SystemFonts.DefaultFont, Brushes.White, 30, 80);
bmp.Save(outputPath, ImageFormat.Png);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_finance(entry: dict, mapping: dict) -> str:
    """Finance XBRL: XbrlDocument() -> Save(outputPath). Proven W18."""
    ns = mapping.get("namespace", entry.get("namespace", "Aspose.Finance.Xbrl"))
    type_name = mapping.get("type_name", entry.get("type_name", "XbrlDocument"))
    return f"""\
// Auto-generated registry probe — Aspose.Finance
using System;
using {ns};

var outputPath = args.Length > 0 ? args[0] : "probe-output.xml";
var doc = new {type_name}();
doc.XbrlInstances.Add();  // Add empty instance so output is non-zero
doc.Save(outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_page_xps(entry: dict, mapping: dict) -> str:
    """Page XpsDocument: needs an XPS input file (creates minimal one)."""
    return """\
// Auto-generated registry probe — Aspose.Page (XPS)
using System;
using System.IO;
using Aspose.Page.XPS;

var outputPath = args.Length > 0 ? args[0] : "probe-output.pdf";
// Create a minimal XPS document
using var doc = new XpsDocument();
doc.AddPage();
doc.Save(outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_page_plugin(entry: dict, mapping: dict) -> str:
    """Page PsConverter: plugin-based API — PsConverter.Process()."""
    return """\
// Auto-generated registry probe — Aspose.Page (Plugin)
using System;
using Aspose.Page.Plugins;

var outputPath = args.Length > 0 ? args[0] : "probe-output.pdf";
// Verify PsConverter type is accessible (instantiation probe)
var converter = new PsConverter();
Console.WriteLine("PsConverter type accessible: " + converter.GetType().FullName);
Console.WriteLine("Probe complete: " + outputPath);
// Note: actual conversion requires PS/EPS input file
File.WriteAllText(outputPath, "PsConverter probe: type accessible");
"""


def _render_html(entry: dict, mapping: dict) -> str:
    """HTML conversion: Converter.ConvertHTML(content, options, path). Proven W20."""
    slug = entry.get("plugin_slug", "")
    if "image" in slug:
        save_options = "new ImageSaveOptions(Aspose.Html.Rendering.Image.ImageFormat.Png)"
        ext = "png"
    elif "word" in slug:
        save_options = "new DocSaveOptions()"
        ext = "docx"
    else:
        save_options = "new PdfSaveOptions()"
        ext = "pdf"
    return f"""\
// Auto-generated registry probe — Aspose.HTML
using System;
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;

var outputPath = args.Length > 0 ? args[0] : "probe-output.{ext}";
var htmlContent = "<html><body><h1>Probe Test</h1><p>Generated by registry probe.</p></body></html>";
using var doc = new HTMLDocument(htmlContent, ".");
Converter.ConvertHTML(doc, {save_options}, outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_svg(entry: dict, mapping: dict) -> str:
    """SVG conversion: Converter.ConvertSVG(). Proven W20."""
    slug = entry.get("plugin_slug", "")
    if "png" in slug or "image" in slug:
        save_options = "new ImageSaveOptions(Aspose.Svg.Rendering.Image.ImageFormat.Png)"
        ext = "png"
    else:
        save_options = "new PdfSaveOptions()"
        ext = "pdf"
    return f"""\
// Auto-generated registry probe — Aspose.SVG
using System;
using Aspose.Svg;
using Aspose.Svg.Converters;
using Aspose.Svg.Saving;

var outputPath = args.Length > 0 ? args[0] : "probe-output.{ext}";
var svgContent = @"<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'>
  <rect width='200' height='200' fill='blue'/>
  <text x='20' y='100' fill='white' font-size='20'>Probe</text>
</svg>";
using var doc = new SVGDocument(svgContent, ".");
Converter.ConvertSVG(doc, {save_options}, outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_threed(entry: dict, mapping: dict) -> str:
    """3D: Scene + Box + Save. Proven W18 (pin Aspose.3D 24.12.0)."""
    return """\
// Auto-generated registry probe — Aspose.3D
using System;
using Aspose.ThreeD;
using Aspose.ThreeD.Entities;

var outputPath = args.Length > 0 ? args[0] : "probe-output.fbx";
var scene = new Scene();
scene.RootNode.CreateChildNode(new Box(2, 2, 2));
scene.Save(outputPath, FileFormat.FBX7400ASCII);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_omr(entry: dict, mapping: dict) -> str:
    """OMR: OmrEngine instantiation probe (template generation requires markup)."""
    return """\
// Auto-generated registry probe — Aspose.OMR
using System;
using Aspose.OMR.Api;

var outputPath = args.Length > 0 ? args[0] : "probe-output.txt";
var engine = new OmrEngine();
Console.WriteLine("OmrEngine type accessible: " + engine.GetType().FullName);
// Template generation requires a text markup file; verify type access only
File.WriteAllText(outputPath, "OmrEngine probe: type accessible");
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_gis(entry: dict, mapping: dict) -> str:
    """GIS: VectorLayer type accessibility probe (static API, needs input files)."""
    return """\
// Auto-generated registry probe — Aspose.GIS
using System;
using Aspose.Gis;

var outputPath = args.Length > 0 ? args[0] : "probe-output.txt";
// VectorLayer uses static factory methods — verify type accessibility
var driver = Drivers.GeoJson;
Console.WriteLine("GIS driver accessible: " + driver.GetType().FullName);
File.WriteAllText(outputPath, "GIS probe: driver type = " + driver.GetType().FullName);
Console.WriteLine("Probe complete: " + outputPath);
"""


def _render_generic(entry: dict, mapping: dict) -> str:
    """Generic fallback: new Type(); obj.Method(outputPath)."""
    ns = mapping.get("namespace") or entry.get("namespace") or "Unknown"
    type_name = mapping.get("type_name") or entry.get("type_name") or "Unknown"
    method = mapping.get("method_name") or entry.get("method_name") or "Save"
    return f"""\
// Auto-generated registry probe — generic fallback
using System;
using {ns};

var outputPath = args.Length > 0 ? args[0] : "probe-output.bin";
var obj = new {type_name}();
obj.{method}(outputPath);
Console.WriteLine("Probe complete: " + outputPath);
"""


# ---------------------------------------------------------------------------
# Template dispatcher
# ---------------------------------------------------------------------------

_FAMILY_RENDERERS: dict[str, Callable[..., str] | None] = {
    "drawing": None,  # dispatched by slug below
    "finance": _render_finance,
    "html": _render_html,
    "svg": _render_svg,
    "threed": _render_threed,
    "omr": _render_omr,
    "gis": _render_gis,
}


def _select_renderer(entry: dict) -> Callable[..., str]:
    """Select the best renderer for the given registry entry."""
    family = entry.get("family", "")
    slug = entry.get("plugin_slug", "")

    if family == "drawing":
        if "create" in slug:
            return _render_drawing_create
        return _render_drawing_convert

    if family == "page":
        type_name = entry.get("type_name", "")
        if "PsConverter" in type_name or "Plugin" in entry.get("namespace", ""):
            return _render_page_plugin
        return _render_page_xps

    renderer = _FAMILY_RENDERERS.get(family)
    if renderer is not None:
        return renderer

    return _render_generic


# ---------------------------------------------------------------------------
# .csproj template
# ---------------------------------------------------------------------------

_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="{package_id}" Version="{package_version}" />
{extra_refs}  </ItemGroup>
</Project>
"""

# Some families need extra NuGet packages for their probe to compile.
_EXTRA_PACKAGES: dict[str, list[tuple[str, str]]] = {
    # Aspose.Drawing IS System.Drawing replacement — do NOT add System.Drawing.Common (CS0433)
    "html": [("Microsoft.Extensions.Logging.Abstractions", "8.0.0")],
    "svg": [("Microsoft.Extensions.Logging.Abstractions", "8.0.0")],
}


def _render_csproj(entry: dict) -> str:
    """Render the .csproj file for a registry probe."""
    package_id = entry.get("package_id", "Aspose.Unknown")
    package_version = entry.get("last_reflected_package_version") or "26.5.0"

    family = entry.get("family", "")
    extra_refs_lines = []
    for pkg_id, pkg_ver in _EXTRA_PACKAGES.get(family, []):
        extra_refs_lines.append(f'    <PackageReference Include="{pkg_id}" Version="{pkg_ver}" />\n')

    return _CSPROJ_TEMPLATE.format(
        package_id=package_id,
        package_version=package_version,
        extra_refs="".join(extra_refs_lines),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", name)


def generate_probe_from_registry(
    entry: dict,
    output_dir: Path,
) -> ProbeFiles:
    """Generate probe C# code from a capability-registry entry.

    Args:
        entry: A single registry entry dict (from YAML).
        output_dir: Directory to write Program.cs and .csproj.

    Returns:
        ProbeFiles with paths and content.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapping = entry.get("selected_api_mapping") or {}
    if isinstance(mapping, str):
        mapping = {}

    # Guard: entries with no API mapping and no dedicated family renderer cannot
    # produce meaningful probe code. Fail cleanly with NoApiMappingError rather
    # than generating broken C# that fails to compile or triggering a TypeError
    # from _slug(None) when type_name is null in the YAML.
    family = entry.get("family", "")
    _has_dedicated_renderer = family in _FAMILY_RENDERERS or family in ("drawing", "page")
    if (
        not _has_dedicated_renderer
        and not mapping
        and not entry.get("type_name")
        and not entry.get("namespace")
    ):
        slug = entry.get("plugin_slug", "unknown")
        raise NoApiMappingError(
            f"{family}/{slug}: no API mapping available (type_name, namespace, and "
            "selected_api_mapping are all null) and no dedicated family renderer is "
            "registered. Provide type_name+namespace in the registry entry or add a "
            "renderer to _FAMILY_RENDERERS."
        )

    renderer = _select_renderer(entry)
    cs_content = renderer(entry, mapping)
    csproj_content = _render_csproj(entry)

    cs_path = output_dir / "Program.cs"
    type_name = entry.get("type_name") or "Probe"
    csproj_path = output_dir / f"{_slug(type_name)}Probe.csproj"

    cs_path.write_text(cs_content, encoding="utf-8")
    csproj_path.write_text(csproj_content, encoding="utf-8")

    return ProbeFiles(
        cs_path=cs_path,
        csproj_path=csproj_path,
        cs_content=cs_content,
        csproj_content=csproj_content,
    )
