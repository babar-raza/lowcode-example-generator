"""Tests for family-scoped programmatic fixture few-shot guidance in packet_builder."""

from __future__ import annotations

import pytest

from plugin_examples.generator.packet_builder import (
    PromptPacket,
    build_packet,
    _PROGRAMMATIC_FIXTURE_GUIDANCE,
    _build_programmatic_fixture_guidance,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_diagram_catalog(type_name: str = "PdfConverter", full_name: str = "Aspose.Diagram.LowCode.PdfConverter"):
    return {
        "assembly_name": "Aspose.Diagram",
        "assembly_version": "26.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Diagram.LowCode",
                "types": [
                    {
                        "name": type_name,
                        "full_name": full_name,
                        "kind": "class",
                        "is_obsolete": False,
                        "constructors": [],
                        "properties": [],
                        "methods": [
                            {
                                "name": "Process",
                                "return_type": "void",
                                "is_static": True,
                                "is_obsolete": False,
                                "parameters": [
                                    {"name": "inputFile", "type": "System.String", "is_optional": False},
                                    {"name": "outputFile", "type": "System.String", "is_optional": False},
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _make_diagram_scenario(
    type_name: str = "PdfConverter",
    full_name: str = "Aspose.Diagram.LowCode.PdfConverter",
    input_strategy: str = "programmatic_input",
):
    return {
        "scenario_id": f"diagram-{type_name.lower()}-process",
        "title": f"Convert VSDX using {type_name}",
        "target_type": full_name,
        "target_namespace": "Aspose.Diagram.LowCode",
        "target_methods": ["Process"],
        "required_symbols": [
            "Aspose.Diagram.LowCode",
            full_name,
            f"{full_name}.Process",
        ],
        "input_strategy": input_strategy,
        "input_files": [],
        "output_plan": "output.pdf" if type_name == "PdfConverter" else "output.vdx",
    }


def _make_cells_catalog():
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "SpreadsheetLocker",
                        "full_name": "Aspose.Cells.LowCode.SpreadsheetLocker",
                        "kind": "class",
                        "is_obsolete": False,
                        "constructors": [],
                        "properties": [],
                        "methods": [
                            {
                                "name": "Process",
                                "return_type": "void",
                                "is_static": True,
                                "is_obsolete": False,
                                "parameters": [
                                    {"name": "templateFile", "type": "System.String", "is_optional": False},
                                    {"name": "resultFile", "type": "System.String", "is_optional": False},
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


def _make_cells_scenario():
    return {
        "scenario_id": "cells-spreadsheetlocker-process",
        "title": "Lock spreadsheet",
        "target_type": "Aspose.Cells.LowCode.SpreadsheetLocker",
        "target_namespace": "Aspose.Cells.LowCode",
        "target_methods": ["Process"],
        "required_symbols": [
            "Aspose.Cells.LowCode",
            "Aspose.Cells.LowCode.SpreadsheetLocker",
            "Aspose.Cells.LowCode.SpreadsheetLocker.Process",
        ],
        "input_strategy": "programmatic_input",
        "input_files": [],
    }


# ---------------------------------------------------------------------------
# Tests: Guidance registry
# ---------------------------------------------------------------------------


class TestProgrammaticFixtureGuidanceRegistry:
    def test_diagram_entry_exists(self):
        assert "diagram" in _PROGRAMMATIC_FIXTURE_GUIDANCE

    def test_diagram_has_fixture_code(self):
        g = _PROGRAMMATIC_FIXTURE_GUIDANCE["diagram"]
        assert "fixture_code" in g
        assert "Aspose.Diagram.Diagram()" in g["fixture_code"]
        assert "Shape" in g["fixture_code"]
        assert "SaveFileFormat.Vsdx" in g["fixture_code"]

    def test_diagram_has_operation_examples(self):
        g = _PROGRAMMATIC_FIXTURE_GUIDANCE["diagram"]
        ops = g["operation_examples"]
        assert "pdfconverter" in ops
        assert "diagramconverter" in ops
        assert "PdfConverter.Process" in ops["pdfconverter"]
        assert "DiagramConverter.Process" in ops["diagramconverter"]

    def test_diagram_forbidden_patterns(self):
        g = _PROGRAMMATIC_FIXTURE_GUIDANCE["diagram"]
        forbidden = g["forbidden_patterns"]
        texts = " ".join(forbidden)
        assert "File.WriteAllBytes" in texts
        assert "raw byte" in texts.lower() or "raw ZIP" in texts
        assert "empty placeholder" in texts
        assert "DiagramConverter" in texts and "PDF" in texts

    def test_diagram_required_patterns(self):
        g = _PROGRAMMATIC_FIXTURE_GUIDANCE["diagram"]
        required = g["required_patterns"]
        texts = " ".join(required)
        # DEF-004 fix: diagram fixture now uses page.DrawEllipse() instead of
        # new Shape() / Aspose.Diagram.Diagram() (which was the broken API).
        # The DrawEllipse approach is the only correct way to create shapes.
        assert "DrawEllipse" in texts
        assert "XForm" in texts


# ---------------------------------------------------------------------------
# Tests: _build_programmatic_fixture_guidance function
# ---------------------------------------------------------------------------


class TestBuildProgrammaticFixtureGuidance:
    def test_returns_empty_for_non_programmatic_input(self):
        constraints, appendix = _build_programmatic_fixture_guidance(
            "diagram",
            "pdfconverter",
            "generated_fixture_file",
        )
        assert constraints == []
        assert appendix == ""

    def test_returns_empty_for_unknown_family(self):
        constraints, appendix = _build_programmatic_fixture_guidance(
            "unknown_family",
            "something",
            "programmatic_input",
        )
        assert constraints == []
        assert appendix == ""

    def test_returns_constraints_for_diagram(self):
        constraints, appendix = _build_programmatic_fixture_guidance(
            "diagram",
            "pdfconverter",
            "programmatic_input",
        )
        assert len(constraints) > 0
        texts = " ".join(constraints)
        assert "FORBIDDEN" in texts
        assert "REQUIRED" in texts

    def test_returns_fixture_code_appendix_for_diagram(self):
        constraints, appendix = _build_programmatic_fixture_guidance(
            "diagram",
            "pdfconverter",
            "programmatic_input",
        )
        assert "Aspose.Diagram.Diagram()" in appendix
        assert "REFERENCE PATTERN" in appendix

    def test_includes_operation_example_for_pdfconverter(self):
        _, appendix = _build_programmatic_fixture_guidance(
            "diagram",
            "pdfconverter",
            "programmatic_input",
        )
        assert "PdfConverter.Process" in appendix
        assert "LOWCODE OPERATION" in appendix

    def test_includes_operation_example_for_diagramconverter(self):
        _, appendix = _build_programmatic_fixture_guidance(
            "diagram",
            "diagramconverter",
            "programmatic_input",
        )
        assert "DiagramConverter.Process" in appendix
        assert "Visio format" in appendix


# ---------------------------------------------------------------------------
# Tests: build_packet integration for Diagram
# ---------------------------------------------------------------------------


class TestDiagramPacketIntegration:
    def test_diagram_packet_includes_vsdx_fixture_guidance(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        all_constraints = " ".join(packet.constraints)
        assert "Aspose.Diagram.Diagram()" in all_constraints

    def test_diagram_packet_forbids_raw_zip(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        all_constraints = " ".join(packet.constraints)
        assert "File.WriteAllBytes" in all_constraints

    def test_diagram_packet_pdfconverter_for_pdf_output(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        all_constraints = " ".join(packet.constraints)
        assert "PdfConverter" in all_constraints
        # System prompt should mention Diagram rules
        assert "Diagram" in packet.system_prompt

    def test_diagram_packet_diagramconverter_visio_only(self):
        packet = build_packet(
            _make_diagram_scenario(
                "DiagramConverter",
                "Aspose.Diagram.LowCode.DiagramConverter",
            ),
            _make_diagram_catalog(
                "DiagramConverter",
                "Aspose.Diagram.LowCode.DiagramConverter",
            ),
        )
        all_constraints = " ".join(packet.constraints)
        assert "DiagramConverter" in all_constraints
        # Must warn that DiagramConverter does NOT support PDF
        assert "PDF" in all_constraints

    def test_diagram_packet_separates_fixture_from_operation(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        all_constraints = " ".join(packet.constraints)
        assert "INPUT FIXTURE CREATION" in all_constraints or "fixture" in all_constraints.lower()
        assert "LOWCODE OPERATION" in all_constraints or "LowCode" in all_constraints

    def test_diagram_system_prompt_mentions_diagram_rules(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        assert "Diagram LowCode API rules" in packet.system_prompt
        assert "raw ZIP" in packet.system_prompt

    def test_diagram_user_prompt_includes_fixture_code(self):
        packet = build_packet(
            _make_diagram_scenario("PdfConverter"),
            _make_diagram_catalog("PdfConverter"),
        )
        assert "Aspose.Diagram.Diagram()" in packet.user_prompt
        assert "REFERENCE PATTERN" in packet.user_prompt


# ---------------------------------------------------------------------------
# Tests: Non-Diagram families do NOT receive Diagram guidance
# ---------------------------------------------------------------------------


class TestNonDiagramFamiliesExcluded:
    def test_cells_packet_no_diagram_guidance(self):
        packet = build_packet(
            _make_cells_scenario(),
            _make_cells_catalog(),
        )
        all_constraints = " ".join(packet.constraints)
        assert "Aspose.Diagram" not in all_constraints
        assert "VSDX" not in all_constraints
        assert "DiagramConverter" not in all_constraints
        assert "Diagram LowCode" not in packet.system_prompt

    def test_cells_packet_no_fixture_code_appendix(self):
        packet = build_packet(
            _make_cells_scenario(),
            _make_cells_catalog(),
        )
        assert "SaveFileFormat.Vsdx" not in packet.user_prompt
