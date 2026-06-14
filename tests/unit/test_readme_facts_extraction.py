"""Tests for multi-extension extraction in readme_facts."""

import pytest

from plugin_examples.publisher.readme_facts import (
    _INPUT_EXTENDED_PATTERNS,
    _INPUT_PATTERN,
    _OUTPUT_EXTENDED_PATTERNS,
    _OUTPUT_PATTERN,
    ExampleFact,
    _extract_all_extensions,
    _extract_extension,
)


class TestExtractAllExtensions:
    """Test the _extract_all_extensions helper."""

    def test_single_output(self):
        source = 'Converter.Process("input.pdf", "output.docx");'
        result = _extract_all_extensions([_OUTPUT_PATTERN], source)
        assert result == ["docx"]

    def test_multiple_outputs(self):
        source = (
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.docx"));\n'
        )
        result = _extract_all_extensions([_OUTPUT_PATTERN], source)
        assert result == ["pdf", "docx"]

    def test_multiple_inputs(self):
        source = (
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddInput(new FileDataSource("input1.pdf"));\n'
            'options.AddInput(new FileDataSource("input2.pdf"));\n'
        )
        result = _extract_all_extensions([_INPUT_PATTERN] + _INPUT_EXTENDED_PATTERNS, source)
        # "pdf" appears multiple times but should be deduplicated
        assert result == ["pdf"]

    def test_merger_multi_input_formats(self):
        source = (
            'options.AddInput(new FileDataSource("input.xlsx"));\n'
            'options.AddInput(new FileDataSource("input1.xlsx"));\n'
        )
        result = _extract_all_extensions([_INPUT_PATTERN] + _INPUT_EXTENDED_PATTERNS, source)
        assert "xlsx" in result

    def test_no_matches(self):
        source = "Console.WriteLine('Hello World');"
        result = _extract_all_extensions([_OUTPUT_PATTERN], source)
        assert result == []

    def test_extended_patterns(self):
        source = 'File.WriteAllText("result.json", data);\n' 'options.AddOutput(new FileDataSource("output.pdf"));\n'
        result = _extract_all_extensions([_OUTPUT_PATTERN] + _OUTPUT_EXTENDED_PATTERNS, source)
        assert "pdf" in result
        assert "json" in result

    def test_deduplication_order_preserved(self):
        source = '"output.pdf"\n' '"result.pdf"\n' '"output.docx"\n'
        result = _extract_all_extensions([_OUTPUT_PATTERN] + _OUTPUT_EXTENDED_PATTERNS, source)
        assert result == ["pdf", "docx"]


class TestExampleFactDataclass:
    """Test that ExampleFact has the new list fields."""

    def test_default_empty_lists(self):
        fact = ExampleFact(
            example_name="test",
            api_symbol="Converter.Process",
            source_file_path="examples/test/Program.cs",
            source_file_sha256="abc",
            snippet_mode="full_file",
            snippet_content="code",
            snippet_content_sha256="def",
            input_extension="pdf",
            output_extension="docx",
            input_extension_source="program_cs:line1:input.pdf",
            output_extension_source="program_cs:line2:output.docx",
            proof_source="program_cs",
            validation_status="verified",
        )
        assert fact.all_input_extensions == []
        assert fact.all_output_extensions == []

    def test_populated_lists(self):
        fact = ExampleFact(
            example_name="test",
            api_symbol="Merger.Process",
            source_file_path="examples/test/Program.cs",
            source_file_sha256="abc",
            snippet_mode="full_file",
            snippet_content="code",
            snippet_content_sha256="def",
            input_extension="pdf",
            output_extension="pdf",
            all_input_extensions=["pdf", "pdf"],
            all_output_extensions=["pdf"],
            input_extension_source="program_cs:line1:input.pdf",
            output_extension_source="program_cs:line2:output.pdf",
            proof_source="program_cs",
            validation_status="verified",
        )
        assert fact.all_input_extensions == ["pdf", "pdf"]
        assert fact.all_output_extensions == ["pdf"]
        # Backward compat: scalar fields still work
        assert fact.input_extension == "pdf"
        assert fact.output_extension == "pdf"
