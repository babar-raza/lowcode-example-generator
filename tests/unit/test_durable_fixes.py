"""Regression tests for durable generator fixes — Sprint lowcode-durable-full-closure-20260529.

Tests ensure the 6 previously broken examples will generate correctly from source
(template_first deterministic templates) without any workspace-level patches.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

# Ensure src is on path for direct imports
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root / "src"))

from plugin_examples.generator.code_generator import (
    _generate_deterministic_template_for_scenario,
    generate_example,
)
from plugin_examples.generator.packet_builder import PromptPacket


def _make_packet(scenario_id: str, target_type: str, namespace: str, ptc: dict) -> PromptPacket:
    return PromptPacket(
        scenario_id=scenario_id,
        target_type=target_type,
        target_namespace=namespace,
        per_type_constraints=ptc,
    )


class TestDiagramDeterministicTemplate:
    """DEF-004 + DEF-005: Diagram converter API fixes."""

    def _get_diagram_converter_code(self) -> str:
        p = _make_packet(
            "diagram-diagram-converter",
            "Aspose.Diagram.LowCode.DiagramConverter",
            "Aspose.Diagram.LowCode",
            {"DiagramConverter": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def _get_pdf_converter_code(self) -> str:
        p = _make_packet(
            "diagram-pdf-converter",
            "Aspose.Diagram.LowCode.PdfConverter",
            "Aspose.Diagram.LowCode",
            {"PdfConverter": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def test_diagram_converter_uses_draw_ellipse(self):
        code = self._get_diagram_converter_code()
        assert "DrawEllipse" in code, "diagram-converter must use page.DrawEllipse() not new Shape()"

    def test_diagram_converter_no_typeval_shape(self):
        code = self._get_diagram_converter_code()
        assert "TypeValue" not in code, "diagram-converter must not use TypeValue.Shape (does not exist)"
        assert "new Shape()" not in code, "diagram-converter must not use new Shape()"

    def test_diagram_converter_uses_process(self):
        code = self._get_diagram_converter_code()
        assert "DiagramConverter.Process" in code, "Must call DiagramConverter.Process"

    def test_diagram_converter_output_is_vdx(self):
        code = self._get_diagram_converter_code()
        assert "output.vdx" in code, "diagram-converter output must be .vdx"

    def test_pdf_converter_uses_draw_ellipse(self):
        code = self._get_pdf_converter_code()
        assert "DrawEllipse" in code, "pdf-converter must use page.DrawEllipse() not new Shape()"

    def test_pdf_converter_no_typeval_shape(self):
        code = self._get_pdf_converter_code()
        assert "TypeValue" not in code, "pdf-converter must not use TypeValue.Shape"

    def test_pdf_converter_uses_process(self):
        code = self._get_pdf_converter_code()
        assert "PdfConverter.Process" in code, "Must call PdfConverter.Process"

    def test_pdf_converter_output_is_pdf(self):
        code = self._get_pdf_converter_code()
        assert "output.pdf" in code, "pdf-converter output must be .pdf"

    def test_xform_uses_value_property(self):
        """XForm.PinX is DoubleValue — must use .Value not direct assignment."""
        code = self._get_diagram_converter_code()
        assert "PinX.Value" in code, "Must set XForm.PinX.Value (DoubleValue.Value)"
        assert "PinY.Value" in code, "Must set XForm.PinY.Value"


class TestCellsDeterministicTemplate:
    """DEF-001: cells-spreadsheet-merger fixture copy fix."""

    def _get_merger_code(self) -> str:
        p = _make_packet(
            "cells-spreadsheet-merger",
            "Aspose.Cells.LowCode.SpreadsheetMerger",
            "Aspose.Cells.LowCode",
            {"SpreadsheetMerger": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def test_spreadsheet_merger_uses_file_copy(self):
        code = self._get_merger_code()
        assert "File.Copy" in code, "cells-spreadsheet-merger must use File.Copy to create input1/input2"

    def test_spreadsheet_merger_calls_process(self):
        code = self._get_merger_code()
        assert "SpreadsheetMerger.Process" in code, "Must call SpreadsheetMerger.Process"

    def test_spreadsheet_merger_uses_array_inputs(self):
        code = self._get_merger_code()
        assert "input1" in code and "input2" in code, "Must create and use input1 and input2 paths"


class TestWordsDeterministicTemplate:
    """DEF-002 + DEF-003: words-merger and words-watermarker fixes."""

    def _get_merger_code(self) -> str:
        p = _make_packet(
            "words-merger",
            "Aspose.Words.LowCode.Merger",
            "Aspose.Words.LowCode",
            {"Merger": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def _get_watermarker_code(self) -> str:
        p = _make_packet(
            "words-watermarker",
            "Aspose.Words.LowCode.Watermarker",
            "Aspose.Words.LowCode",
            {"Watermarker": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def test_merger_uses_file_copy(self):
        code = self._get_merger_code()
        assert "File.Copy" in code, "words-merger must use File.Copy to create input1/input2"

    def test_merger_calls_merge(self):
        code = self._get_merger_code()
        assert "Merger.Merge" in code, "Must call Merger.Merge (static)"

    def test_merger_no_merger_create(self):
        code = self._get_merger_code()
        assert "Merger.Create" not in code, "Must not use Merger.Create() — does not exist"

    def test_watermarker_uses_bmp_bytes(self):
        code = self._get_watermarker_code()
        assert "bmpBytes" in code, "words-watermarker must create BMP bytes programmatically"

    def test_watermarker_calls_set_text(self):
        code = self._get_watermarker_code()
        assert "SetText" in code, "words-watermarker must call Watermarker.SetText"

    def test_watermarker_calls_set_image(self):
        code = self._get_watermarker_code()
        assert "SetImage" in code, "words-watermarker must call Watermarker.SetImage"

    def test_watermarker_no_sample_path(self):
        code = self._get_watermarker_code()
        # "sample" should only appear in the output filename, not as image path
        # The BMP bytes approach avoids "sample" image file reference
        assert '"sample"' not in code, 'Must not pass "sample" as image path — file does not exist'


class TestTemplateFirstConfig:
    """Verify template_first: true is set in family YAML configs for all 5 fixed types."""

    def _load_yaml(self, family: str) -> dict:
        path = _repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_diagram_yml_has_template_first_for_diagramconverter(self):
        cfg = self._load_yaml("diagram")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("DiagramConverter", {}).get("template_first") is True

    def test_diagram_yml_has_template_first_for_pdfconverter(self):
        cfg = self._load_yaml("diagram")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("PdfConverter", {}).get("template_first") is True

    def test_cells_yml_has_template_first_for_spreadsheetmerger(self):
        cfg = self._load_yaml("cells")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("SpreadsheetMerger", {}).get("template_first") is True

    def test_words_yml_has_template_first_for_merger(self):
        cfg = self._load_yaml("words")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("Merger", {}).get("template_first") is True

    def test_words_yml_has_template_first_for_watermarker(self):
        cfg = self._load_yaml("words")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("Watermarker", {}).get("template_first") is True

    def test_pdf_yml_has_template_first_for_tablegenerator(self):
        """TableGenerator was already fixed in prior sprint — verify it's still correct."""
        cfg = self._load_yaml("pdf")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("TableGenerator", {}).get("template_first") is True

    def test_slides_yml_has_template_first_for_convert(self):
        """Slides Convert type needs template_first to avoid System.Convert ambiguity."""
        cfg = self._load_yaml("slides")
        ptc = cfg.get("per_type_constraints", {})
        assert ptc.get("Convert", {}).get("template_first") is True


class TestPdfTableGeneratorFix:
    """DEF-008: pdf-table-generator TableOptions.Create() chain fix."""

    def _get_code(self) -> str:
        p = _make_packet(
            "pdf-table-generator",
            "Aspose.Pdf.LowCode.TableGenerator",
            "Aspose.Pdf.LowCode",
            {"TableGenerator": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def test_uses_new_table_options(self):
        """Template must use 'new TableOptions()' not TableOptions.Create() chain."""
        assert "new TableOptions()" in self._get_code()

    def test_no_table_options_create_fluent_chain(self):
        """TableOptions.Create()...chain causes CS1061 on AddInput — must NOT be present."""
        code = self._get_code()
        # The broken pattern was: var options = TableOptions.Create().InsertPageBefore(...)
        # which ends at TableCellBuilder, not TableOptions
        assert "var options = TableOptions.Create()" not in code

    def test_calls_add_input(self):
        """Must call options.AddInput() after building table."""
        assert "options.AddInput(new FileDataSource(" in self._get_code()

    def test_calls_add_output(self):
        """Must call options.AddOutput() after building table."""
        assert "options.AddOutput(new FileDataSource(" in self._get_code()

    def test_calls_table_generator_process(self):
        """Must call new TableGenerator().Process(options)."""
        assert "new TableGenerator().Process(options)" in self._get_code()


class TestSlidesConvertFix:
    """DEF-009: slides-convert System.Convert ambiguity fix."""

    def _get_code(self) -> str:
        p = _make_packet(
            "slides-convert",
            "Aspose.Slides.LowCode.Convert",
            "Aspose.Slides.LowCode",
            {"Convert": {"template_first": True}},
        )
        result = generate_example(p, llm_generate=None)
        assert result.status == "generated_template_first", f"Unexpected status: {result.status}"
        return result.code

    def test_uses_fully_qualified_convert(self):
        """Must use fully-qualified Aspose.Slides.LowCode.Convert to avoid CS0104."""
        assert "Aspose.Slides.LowCode.Convert.ToPdf(" in self._get_code()

    def test_no_bare_convert_call(self):
        """Bare 'Convert.ToPdf(' is ambiguous with System.Convert — must not appear alone."""
        code = self._get_code()
        # Check that Convert.ToPdf is always preceded by the full namespace
        import re
        bare_calls = re.findall(r"(?<!Aspose\.Slides\.LowCode\.)Convert\.ToPdf\(", code)
        assert not bare_calls, f"Found bare Convert.ToPdf calls: {bare_calls}"

    def test_creates_input_pptx(self):
        """Must create input PPTX programmatically."""
        assert "new Presentation()" in self._get_code()

    def test_uses_save_format_pptx(self):
        """Must save presentation as PPTX before calling Convert."""
        assert "SaveFormat.Pptx" in self._get_code()
