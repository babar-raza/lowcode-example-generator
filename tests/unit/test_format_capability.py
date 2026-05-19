"""Tests for format_capability package — manifest, classifier, populator, validator, serializer."""

import pytest

from plugin_examples.format_capability.manifest import (
    FormatCapabilityManifest,
    TypeFormatCapability,
)
from plugin_examples.format_capability.classifier import classify_operation_kind
from plugin_examples.format_capability.populator import (
    populate_manifest,
    _ACTIVE_TYPES,
    _FAMILY_DEFAULTS,
)
from plugin_examples.format_capability.validator import validate_manifest
from plugin_examples.format_capability.serializer import (
    serialize_manifest,
    deserialize_manifest,
)


# --- Classifier tests ---

class TestClassifyOperationKind:
    def test_converter(self):
        assert classify_operation_kind("DocConverter") == "converter"

    def test_merger(self):
        assert classify_operation_kind("Merger") == "merger"

    def test_splitter(self):
        assert classify_operation_kind("Splitter") == "splitter"

    def test_text_extractor(self):
        assert classify_operation_kind("TextExtractor") == "extractor"

    def test_image_extractor(self):
        assert classify_operation_kind("ImageExtractor") == "image_extractor"

    def test_optimizer(self):
        assert classify_operation_kind("Optimizer") == "transform"

    def test_security(self):
        assert classify_operation_kind("Security") == "transform"

    def test_form_flattener(self):
        assert classify_operation_kind("FormFlattener") == "form_processor"

    def test_form_exporter(self):
        assert classify_operation_kind("FormExporter") == "form_exporter"

    def test_toc_generator(self):
        assert classify_operation_kind("TocGenerator") == "generator"

    def test_email_converter(self):
        assert classify_operation_kind("Converter", "email") == "directory_output"

    def test_words_converter(self):
        assert classify_operation_kind("Converter", "words") == "converter"

    def test_unknown(self):
        assert classify_operation_kind("SomethingWeird") == "unknown"

    def test_slides_convert(self):
        assert classify_operation_kind("Convert") == "converter"

    def test_comparer(self):
        assert classify_operation_kind("Comparer") == "transform"

    def test_watermarker(self):
        assert classify_operation_kind("Watermarker") == "transform"

    def test_signature(self):
        assert classify_operation_kind("Signature") == "transform"

    def test_pdfa_converter(self):
        assert classify_operation_kind("PdfAConverter") == "transform"


# --- Populator tests ---

class TestPopulateManifest:
    @pytest.mark.parametrize("family", list(_ACTIVE_TYPES.keys()))
    def test_populate_all_families(self, family):
        manifest = populate_manifest(family)
        assert manifest.family == family
        assert len(manifest.types) == len(_ACTIVE_TYPES[family])

    def test_unknown_family_raises(self):
        with pytest.raises(ValueError, match="Unknown family"):
            populate_manifest("nonexistent")

    def test_cells_spreadsheet_converter(self):
        m = populate_manifest("cells")
        cap = m.types["SpreadsheetConverter"]
        assert cap.operation_kind == "converter"
        assert cap.input_format == ".xlsx"
        assert cap.primary_output_format == ".xlsx"

    def test_pdf_doc_converter(self):
        m = populate_manifest("pdf")
        cap = m.types["DocConverter"]
        assert cap.operation_kind == "converter"
        assert cap.input_format == ".pdf"
        assert cap.primary_output_format == ".docx"

    def test_pdf_text_extractor(self):
        m = populate_manifest("pdf")
        cap = m.types["TextExtractor"]
        assert cap.operation_kind == "extractor"
        assert cap.primary_output_format == ""
        assert cap.output_kind == "stdout"
        assert cap.output_cardinality == "none"

    def test_pdf_merger(self):
        m = populate_manifest("pdf")
        cap = m.types["Merger"]
        assert cap.operation_kind == "merger"
        assert cap.input_cardinality == "multi"
        assert cap.primary_output_format == ".pdf"

    def test_email_converter(self):
        m = populate_manifest("email")
        cap = m.types["Converter"]
        assert cap.operation_kind == "directory_output"
        assert cap.output_kind == "directory"

    def test_no_dot_out_in_any_manifest(self):
        for family in _ACTIVE_TYPES:
            m = populate_manifest(family)
            for type_name, cap in m.types.items():
                assert cap.primary_output_format != ".out", (
                    f"{family}:{type_name} has .out output"
                )

    def test_total_type_count(self):
        total = sum(len(types) for types in _ACTIVE_TYPES.values())
        assert total == 42


# --- Validator tests ---

class TestValidateManifest:
    def test_valid_manifest(self):
        m = populate_manifest("cells")
        result = validate_manifest(m)
        assert result.valid

    @pytest.mark.parametrize("family", list(_ACTIVE_TYPES.keys()))
    def test_all_families_valid(self, family):
        m = populate_manifest(family)
        result = validate_manifest(m)
        assert result.valid, (
            f"{family} validation failed: "
            + "; ".join(f"{i.type_name}: {i.message}" for i in result.issues if i.severity == "error")
        )

    def test_dot_out_detected(self):
        m = FormatCapabilityManifest(family="test", types={
            "Bad": TypeFormatCapability(
                family="test", type_name="Bad", operation_kind="converter",
                input_format=".pdf", input_cardinality="single",
                primary_output_format=".out", output_cardinality="single",
                output_kind="file",
            ),
        })
        result = validate_manifest(m)
        assert not result.valid
        assert any(".out" in i.message for i in result.issues)

    def test_missing_input_format_detected(self):
        m = FormatCapabilityManifest(family="test", types={
            "Bad": TypeFormatCapability(
                family="test", type_name="Bad", operation_kind="converter",
                input_format="", input_cardinality="single",
                primary_output_format=".pdf", output_cardinality="single",
                output_kind="file",
            ),
        })
        result = validate_manifest(m)
        assert not result.valid


# --- Serializer tests ---

class TestSerializer:
    def test_round_trip(self):
        m = populate_manifest("cells")
        json_str = serialize_manifest(m)
        m2 = deserialize_manifest(json_str)
        assert m2.family == m.family
        assert len(m2.types) == len(m.types)
        for name in m.types:
            assert m2.types[name].input_format == m.types[name].input_format
            assert m2.types[name].primary_output_format == m.types[name].primary_output_format

    def test_serialization_contains_all_fields(self):
        m = populate_manifest("pdf")
        json_str = serialize_manifest(m)
        assert '"operation_kind"' in json_str
        assert '"input_cardinality"' in json_str
        assert '"template_first"' in json_str
