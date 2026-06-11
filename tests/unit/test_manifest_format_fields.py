"""Tests for format fields in example.manifest.json."""

import pytest

from plugin_examples.generator.project_generator import (
    _infer_manifest_format,
    _infer_manifest_format_from_code,
    _infer_operation_kind,
)


class TestInferManifestFormat:
    def test_input_format_from_files(self):
        assert _infer_manifest_format(["input.pdf"], "input") == ".pdf"

    def test_input_format_from_xlsx(self):
        assert _infer_manifest_format(["input.xlsx"], "input") == ".xlsx"

    def test_no_files_returns_none(self):
        assert _infer_manifest_format(None, "input") is None

    def test_empty_files_returns_none(self):
        assert _infer_manifest_format([], "input") is None


class TestInferFormatFromCode:
    def test_output_docx(self):
        class FakeExample:
            code = 'options.AddOutput(new FileDataSource("output.docx"));'

        assert _infer_manifest_format_from_code(FakeExample()) == ".docx"

    def test_output_pdf(self):
        class FakeExample:
            code = 'Converter.Process(input, "output.pdf");'

        assert _infer_manifest_format_from_code(FakeExample()) == ".pdf"

    def test_no_output_returns_none(self):
        class FakeExample:
            code = "Console.WriteLine('Hello');"

        assert _infer_manifest_format_from_code(FakeExample()) is None

    def test_no_code_returns_none(self):
        class FakeExample:
            code = ""

        assert _infer_manifest_format_from_code(FakeExample()) is None


class TestInferOperationKind:
    def test_merger(self):
        assert _infer_operation_kind("pdf-merger") == "merger"

    def test_splitter(self):
        assert _infer_operation_kind("words-splitter") == "splitter"

    def test_converter(self):
        assert _infer_operation_kind("cells-spreadsheet-converter") == "converter"

    def test_convert(self):
        assert _infer_operation_kind("slides-convert") == "converter"

    def test_extractor(self):
        assert _infer_operation_kind("pdf-text-extractor") == "extractor"

    def test_optimizer_is_transform(self):
        assert _infer_operation_kind("pdf-optimizer") == "transform"

    def test_security_is_transform(self):
        assert _infer_operation_kind("pdf-security") == "transform"

    def test_form_flattener(self):
        assert _infer_operation_kind("pdf-form-flattener") == "form_processor"

    def test_form_exporter(self):
        assert _infer_operation_kind("pdf-formexporter") == "form_exporter"

    def test_generator(self):
        assert _infer_operation_kind("pdf-toc-generator") == "generator"

    def test_unknown(self):
        assert _infer_operation_kind("something-weird") == "unknown"
