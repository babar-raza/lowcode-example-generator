"""Tests for registry probe code generator (TC-PSAL-23)."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin_examples.probe_generator.registry_probe import (
    _render_csproj,
    _select_renderer,
    generate_probe_from_registry,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_entry(family: str, slug: str, type_name: str = "Foo", namespace: str = "Bar",
                method: str = "Save", mapping: dict | None = None, **extra) -> dict:
    entry = {
        "family": family,
        "plugin_slug": slug,
        "type_name": type_name,
        "namespace": namespace,
        "method_name": method,
        "package_id": f"Aspose.{family.title()}",
        "last_reflected_package_version": "26.5.0",
        "selected_api_mapping": mapping,
        "status": "REFLECTION_CANDIDATE",
    }
    entry.update(extra)
    return entry


# ---------------------------------------------------------------------------
# Template selection tests
# ---------------------------------------------------------------------------

class TestRendererSelection:
    def test_drawing_convert_selected(self):
        entry = _make_entry("drawing", "convert-drawing")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_drawing_convert"

    def test_drawing_create_selected(self):
        entry = _make_entry("drawing", "create-drawing")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_drawing_create"

    def test_finance_selected(self):
        entry = _make_entry("finance", "convert-xbrl")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_finance"

    def test_page_xps_selected(self):
        entry = _make_entry("page", "convert-xps", type_name="XpsDocument", namespace="Aspose.Page.XPS")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_page_xps"

    def test_page_plugin_selected(self):
        entry = _make_entry("page", "convert-eps", type_name="PsConverter", namespace="Aspose.Page.Plugins")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_page_plugin"

    def test_html_selected(self):
        entry = _make_entry("html", "convert-html-to-pdf")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_html"

    def test_svg_selected(self):
        entry = _make_entry("svg", "convert-svg-to-pdf")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_svg"

    def test_threed_selected(self):
        entry = _make_entry("threed", "convert-3d-model")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_threed"

    def test_omr_selected(self):
        entry = _make_entry("omr", "recognize-omr")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_omr"

    def test_unknown_family_uses_generic(self):
        entry = _make_entry("unknownfamily", "some-slug")
        r = _select_renderer(entry)
        assert r.__name__ == "_render_generic"


# ---------------------------------------------------------------------------
# Template rendering tests
# ---------------------------------------------------------------------------

class TestTemplateRendering:
    def test_drawing_convert_has_using_and_bitmap(self):
        entry = _make_entry("drawing", "convert-drawing", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-draw"))
        assert "using System.Drawing" in files.cs_content
        assert "Bitmap" in files.cs_content
        assert "probe-output" in files.cs_content.lower() or "outputPath" in files.cs_content

    def test_finance_has_xbrl(self):
        entry = _make_entry("finance", "convert-xbrl", type_name="XbrlDocument",
                            namespace="Aspose.Finance.Xbrl",
                            mapping={"type_name": "XbrlDocument", "namespace": "Aspose.Finance.Xbrl"})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-fin"))
        assert "XbrlDocument" in files.cs_content
        assert "Aspose.Finance.Xbrl" in files.cs_content

    def test_html_pdf_has_converter(self):
        entry = _make_entry("html", "convert-html-to-pdf", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-html"))
        assert "Converter.ConvertHTML" in files.cs_content
        assert "PdfSaveOptions" in files.cs_content

    def test_html_image_has_image_save_options(self):
        entry = _make_entry("html", "convert-html-to-image", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-html-img"))
        assert "ImageSaveOptions" in files.cs_content

    def test_svg_pdf_has_converter(self):
        entry = _make_entry("svg", "convert-svg-to-pdf", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-svg"))
        assert "Converter.ConvertSVG" in files.cs_content
        assert "PdfSaveOptions" in files.cs_content

    def test_svg_png_has_image_options(self):
        entry = _make_entry("svg", "convert-svg-to-png", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-svg-png"))
        assert "ImageSaveOptions" in files.cs_content

    def test_threed_has_scene(self):
        entry = _make_entry("threed", "convert-3d-model", mapping={})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-3d"))
        assert "Scene" in files.cs_content
        assert "Box" in files.cs_content

    def test_generic_fallback(self):
        entry = _make_entry("unknownfamily", "some-op", type_name="MyType",
                            namespace="My.Namespace", method="DoStuff",
                            mapping={"type_name": "MyType", "namespace": "My.Namespace", "method_name": "DoStuff"})
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-generic"))
        assert "MyType" in files.cs_content
        assert "My.Namespace" in files.cs_content
        assert "DoStuff" in files.cs_content

    def test_null_mapping_uses_entry_fields(self):
        entry = _make_entry("unknownfamily", "slug", type_name="FooBar",
                            namespace="Ns.FooBar", method="Run", mapping=None)
        files = generate_probe_from_registry(entry, Path("/tmp/test-probe-null"))
        assert "FooBar" in files.cs_content
        assert "Ns.FooBar" in files.cs_content


# ---------------------------------------------------------------------------
# .csproj rendering tests
# ---------------------------------------------------------------------------

class TestCsprojRendering:
    def test_correct_package_ref(self):
        entry = _make_entry("finance", "convert-xbrl")
        csproj = _render_csproj(entry)
        assert 'Include="Aspose.Finance"' in csproj
        assert 'Version="26.5.0"' in csproj

    def test_drawing_no_system_drawing_common(self):
        """Aspose.Drawing IS the System.Drawing replacement — no extra package needed."""
        entry = _make_entry("drawing", "convert-drawing")
        csproj = _render_csproj(entry)
        assert "System.Drawing.Common" not in csproj
        assert csproj.count("PackageReference") == 1

    def test_html_gets_logging_abstractions(self):
        entry = _make_entry("html", "convert-html")
        csproj = _render_csproj(entry)
        assert "Microsoft.Extensions.Logging.Abstractions" in csproj

    def test_svg_gets_logging_abstractions(self):
        entry = _make_entry("svg", "convert-svg")
        csproj = _render_csproj(entry)
        assert "Microsoft.Extensions.Logging.Abstractions" in csproj

    def test_no_extra_packages_for_finance(self):
        entry = _make_entry("finance", "convert-xbrl")
        csproj = _render_csproj(entry)
        # Should have only the main package reference
        assert csproj.count("PackageReference") == 1


# ---------------------------------------------------------------------------
# File writing tests
# ---------------------------------------------------------------------------

class TestFileWriting:
    def test_files_created(self, tmp_path):
        entry = _make_entry("finance", "convert-xbrl", mapping={})
        files = generate_probe_from_registry(entry, tmp_path / "probe")
        assert files.cs_path.exists()
        assert files.csproj_path.exists()
        assert files.cs_path.name == "Program.cs"
        assert files.csproj_path.suffix == ".csproj"

    def test_uses_entry_package_version(self, tmp_path):
        entry = _make_entry("finance", "convert-xbrl",
                            mapping={}, last_reflected_package_version="25.1.0")
        files = generate_probe_from_registry(entry, tmp_path / "probe-ver")
        assert 'Version="25.1.0"' in files.csproj_content
