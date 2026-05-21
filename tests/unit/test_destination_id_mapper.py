"""Tests for DestinationIdMapper — Sprint 60 Phase 2.

Covers the four destination content gaps found in Sprint 59:

1. pdf-image-extractor PARTIAL: result-collection output policy
2. pdf-pdfa-converter PRESENT_NO_AUTHORITY: naming convention mismatch
3. diagram-diagram-diagram-converter PRESENT_NO_AUTHORITY: double-prefix bug
4. diagram-diagram-pdf-converter PRESENT_NO_AUTHORITY: double-prefix bug

Test names:
    test_cells_standard_prefix_stripping
    test_words_standard_prefix_stripping
    test_pdf_standard_prefix_stripping
    test_slides_standard_prefix_stripping
    test_email_standard_prefix_stripping
    test_diagram_dir_name_is_scenario_id
    test_diagram_no_double_prefix_for_diagram_converter
    test_diagram_no_double_prefix_for_pdf_converter
    test_pdfa_converter_alias
    test_image_extractor_result_collection_policy
    test_double_family_prefix_detection_diagram
    test_double_family_prefix_not_triggered_for_standard
    test_round_trip_all_standard_families
    test_round_trip_diagram_family
    test_round_trip_pdfa_alias
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.publisher.destination_id_mapper import DestinationIdMapper


class TestStandardFamilyPrefixStripping(unittest.TestCase):
    """Standard families: scenario_id = family + '-' + dir_name."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_cells_standard_prefix_stripping(self):
        sid = self.mapper.dir_name_to_scenario_id("cells", "html-converter")
        self.assertEqual(sid, "cells-html-converter")

    def test_words_standard_prefix_stripping(self):
        sid = self.mapper.dir_name_to_scenario_id("words", "converter")
        self.assertEqual(sid, "words-converter")

    def test_pdf_standard_prefix_stripping(self):
        sid = self.mapper.dir_name_to_scenario_id("pdf", "doc-converter")
        self.assertEqual(sid, "pdf-doc-converter")

    def test_slides_standard_prefix_stripping(self):
        sid = self.mapper.dir_name_to_scenario_id("slides", "compress")
        self.assertEqual(sid, "slides-compress")

    def test_email_standard_prefix_stripping(self):
        sid = self.mapper.dir_name_to_scenario_id("email", "converter")
        self.assertEqual(sid, "email-converter")


class TestDiagramFamilyNoPrefixAdded(unittest.TestCase):
    """Diagram dir names already include the family prefix — do not add again."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_diagram_dir_name_is_scenario_id(self):
        """diagram-diagram-converter dir → scenario_id = diagram-diagram-converter, not triple."""
        sid = self.mapper.dir_name_to_scenario_id("diagram", "diagram-diagram-converter")
        self.assertEqual(sid, "diagram-diagram-converter")

    def test_diagram_no_double_prefix_for_diagram_converter(self):
        """Sprint 59 bug: do NOT produce diagram-diagram-diagram-converter."""
        sid = self.mapper.dir_name_to_scenario_id("diagram", "diagram-diagram-converter")
        self.assertNotIn("diagram-diagram-diagram", sid,
                         "Triple-prefix scenario_id must not be produced")

    def test_diagram_no_double_prefix_for_pdf_converter(self):
        """Sprint 59 bug: do NOT produce diagram-diagram-pdf-converter."""
        sid = self.mapper.dir_name_to_scenario_id("diagram", "diagram-pdf-converter")
        self.assertNotEqual(sid, "diagram-diagram-pdf-converter",
                            "Double-prefix scenario_id must not be produced for diagram-pdf-converter")
        self.assertEqual(sid, "diagram-pdf-converter")


class TestPdfAConverterAlias(unittest.TestCase):
    """pdf-pdfa-converter (repo path) ↔ pdf-pdf-aconverter (canonical pipeline ID)."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_pdfa_converter_alias(self):
        """pdfa-converter dir → canonical pdf-pdf-aconverter, not pdf-pdfa-converter."""
        sid = self.mapper.dir_name_to_scenario_id("pdf", "pdfa-converter")
        self.assertEqual(sid, "pdf-pdf-aconverter",
                         "pdfa-converter must resolve to canonical pdf-pdf-aconverter")

    def test_pdfa_alias_not_pdfa_converter(self):
        """pdf-pdfa-converter is the wrong ID — must not be returned for pdfa-converter dir."""
        sid = self.mapper.dir_name_to_scenario_id("pdf", "pdfa-converter")
        self.assertNotEqual(sid, "pdf-pdfa-converter")

    def test_pdfa_reverse_mapping(self):
        """Canonical pdf-pdf-aconverter → repo dir pdfa-converter."""
        dir_name = self.mapper.scenario_id_to_dir_name("pdf-pdf-aconverter", "pdf")
        self.assertEqual(dir_name, "pdfa-converter")


class TestResultCollectionOutputPolicy(unittest.TestCase):
    """ImageExtractor uses ResultCollection output — not a literal .png file path."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_image_extractor_result_collection_policy(self):
        """pdf-image-extractor is a result-collection output API."""
        self.assertTrue(self.mapper.is_result_collection_output("pdf-image-extractor"))

    def test_text_extractor_result_collection_policy(self):
        """pdf-text-extractor is also a result-collection output API."""
        self.assertTrue(self.mapper.is_result_collection_output("pdf-text-extractor"))

    def test_standard_converter_not_result_collection(self):
        """Standard converters write to file paths, not ResultCollection."""
        self.assertFalse(self.mapper.is_result_collection_output("pdf-doc-converter"))
        self.assertFalse(self.mapper.is_result_collection_output("cells-html-converter"))


class TestDoubleFamilyPrefixDetection(unittest.TestCase):
    """is_double_family_prefix catches Sprint 59-style bugs."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_double_family_prefix_detection_diagram(self):
        """diagram-diagram-diagram-converter is triple-prefix (family applied twice)."""
        self.assertTrue(
            self.mapper.is_double_family_prefix("diagram", "diagram-diagram-diagram-converter")
        )

    def test_double_family_prefix_not_triggered_for_standard(self):
        """diagram-diagram-converter is the canonical id — NOT a double-prefix error."""
        self.assertFalse(
            self.mapper.is_double_family_prefix("diagram", "diagram-diagram-converter"),
            "diagram-diagram-converter is canonical; only triple+ counts as double-prefix bug"
        )

    def test_double_prefix_not_triggered_for_cells(self):
        """cells-html-converter has no double prefix."""
        self.assertFalse(
            self.mapper.is_double_family_prefix("cells", "cells-html-converter")
        )


class TestRoundTripMappings(unittest.TestCase):
    """dir_name → scenario_id → dir_name round-trip consistency."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_round_trip_all_standard_families(self):
        """Standard family round-trips are consistent."""
        cases = [
            ("cells", "html-converter"),
            ("cells", "spreadsheet-converter"),
            ("words", "converter"),
            ("words", "mail-merger"),
            ("pdf", "doc-converter"),
            ("pdf", "image-extractor"),
            ("slides", "compress"),
            ("email", "converter"),
        ]
        for family, dir_name in cases:
            with self.subTest(family=family, dir_name=dir_name):
                sid = self.mapper.dir_name_to_scenario_id(family, dir_name)
                back = self.mapper.scenario_id_to_dir_name(sid, family)
                self.assertEqual(back, dir_name, f"Round-trip failed for {family}/{dir_name}")

    def test_round_trip_diagram_family(self):
        """Diagram family round-trips preserve full scenario_id."""
        cases = [
            ("diagram", "diagram-diagram-converter"),
            ("diagram", "diagram-pdf-converter"),
        ]
        for family, dir_name in cases:
            with self.subTest(family=family, dir_name=dir_name):
                sid = self.mapper.dir_name_to_scenario_id(family, dir_name)
                back = self.mapper.scenario_id_to_dir_name(sid, family)
                self.assertEqual(back, dir_name)

    def test_round_trip_pdfa_alias(self):
        """pdfa-converter alias round-trips to canonical id and back."""
        sid = self.mapper.dir_name_to_scenario_id("pdf", "pdfa-converter")
        self.assertEqual(sid, "pdf-pdf-aconverter")
        back = self.mapper.scenario_id_to_dir_name(sid, "pdf")
        self.assertEqual(back, "pdfa-converter")


class TestPresentNoAuthorityMustNotOccur(unittest.TestCase):
    """Regression tests: the Sprint 59 PRESENT_NO_AUTHORITY cases must not recur."""

    def setUp(self):
        self.mapper = DestinationIdMapper()

    def test_diagram_diagram_converter_maps_to_canonical(self):
        """diagram-diagram-converter dir → diagram-diagram-converter (matches lifecycle record)."""
        sid = self.mapper.dir_name_to_scenario_id("diagram", "diagram-diagram-converter")
        self.assertEqual(sid, "diagram-diagram-converter",
                         "Must match lifecycle canonical id to avoid PRESENT_NO_AUTHORITY")

    def test_diagram_pdf_converter_maps_to_canonical(self):
        """diagram-pdf-converter dir → diagram-pdf-converter."""
        sid = self.mapper.dir_name_to_scenario_id("diagram", "diagram-pdf-converter")
        self.assertEqual(sid, "diagram-pdf-converter")

    def test_pdfa_converter_maps_to_canonical(self):
        """pdfa-converter dir → pdf-pdf-aconverter."""
        sid = self.mapper.dir_name_to_scenario_id("pdf", "pdfa-converter")
        self.assertEqual(sid, "pdf-pdf-aconverter")
