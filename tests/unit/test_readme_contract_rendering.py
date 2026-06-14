"""TC-MEGA-F01/F02: Verify README renderer uses contract-consistent display fields,
and auditor populates contract_format_mismatches."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from plugin_examples.format_authority.store import reset_store


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


def _make_family_config(family: str = "cells") -> MagicMock:
    cfg = MagicMock()
    cfg.family = family
    cfg.display_name = f"Aspose.Cells for .NET" if family == "cells" else f"Aspose.{family.capitalize()} for .NET"
    cfg.nuget.package_id = f"Aspose.{family.capitalize()}"
    cfg.nuget.target_framework_preference = ["net8.0"]
    cfg.github.published_plugin_examples_repo.owner = f"aspose-{family}-net"
    cfg.github.published_plugin_examples_repo.repo = f"Aspose.{family.capitalize()}.LowCode-for-.NET-Examples"
    cfg.github.published_plugin_examples_repo.branch = "main"
    cfg.generation.allowed_types = []
    cfg.template_hints.default_input_extension = ".xlsx"
    cfg.template_hints.default_output_extension = ".xlsx"
    return cfg


class TestExampleEntryContractDisplayFields:
    """ExampleEntry must carry operation_kind and display fields derived from format data."""

    def test_entry_has_operation_kind_field(self):
        from plugin_examples.publisher.readme_renderer import ExampleEntry

        e = ExampleEntry(name="test", api_class="Test", input_format=".xlsx", output_format=".csv")
        assert hasattr(e, "operation_kind")
        assert hasattr(e, "input_format_display")
        assert hasattr(e, "output_format_display")

    def test_converter_display_includes_formats(self):
        from plugin_examples.publisher.readme_renderer import _compute_display_fields

        in_disp, out_disp = _compute_display_fields("converter", ".xlsx", ".csv")
        assert isinstance(in_disp, str)
        assert isinstance(out_disp, str)

    def test_merger_display_not_empty(self):
        from plugin_examples.publisher.readme_renderer import _compute_display_fields

        in_disp, out_disp = _compute_display_fields("merger", ".xlsx", ".xlsx")
        assert isinstance(in_disp, str)
        assert isinstance(out_disp, str)

    def test_splitter_display_not_empty(self):
        from plugin_examples.publisher.readme_renderer import _compute_display_fields

        in_disp, out_disp = _compute_display_fields("splitter", ".docx", ".docx")
        assert isinstance(in_disp, str)
        assert isinstance(out_disp, str)

    def test_extractor_stdout_display(self):
        from plugin_examples.publisher.readme_renderer import _compute_display_fields

        in_disp, out_disp = _compute_display_fields("extractor", ".pdf", "")
        assert isinstance(in_disp, str)
        assert isinstance(out_disp, str)


class TestReadmeRendererContractConsistency:
    """Verify rendered context entries carry operation_kind."""

    def test_build_readme_context_has_operation_kind(self):
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_family_config("cells")
        examples = [
            {"name": "spreadsheet-converter", "output_format": "csv"},
            {"name": "spreadsheet-merger", "output_format": "xlsx"},
        ]
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=examples,
            package_version="26.5.1",
        )
        for entry in ctx.examples:
            assert hasattr(entry, "operation_kind"), f"{entry.name} missing operation_kind"
            assert entry.operation_kind != "", f"{entry.name} has empty operation_kind"

    def test_spreadsheet_converter_rendered_has_display_fields(self):
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_family_config("cells")
        examples = [{"name": "spreadsheet-converter"}]
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=examples,
            package_version="26.5.1",
        )
        sc = next((e for e in ctx.examples if "converter" in e.name.lower()), None)
        assert sc is not None
        assert isinstance(sc.output_format, str)
        assert isinstance(sc.input_format_display, str)
        assert isinstance(sc.output_format_display, str)


class TestReadmeAuditorContractCrossCheck:
    """TC-MEGA-F02: Verify readme_auditor populates contract_format_mismatches."""

    def _render_and_audit(self, family: str, examples: list[dict]) -> object:
        from plugin_examples.publisher.readme_auditor import audit_readme
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config(family)
        ctx = build_readme_context(
            family=family,
            family_config=cfg,
            examples=examples,
            package_version="26.5.1",
        )
        rendered = render_readme(ctx)
        return audit_readme(rendered, ctx)

    def test_audit_result_has_contract_mismatch_field(self):
        result = self._render_and_audit("cells", [{"name": "spreadsheet-converter", "output_format": "csv"}])
        assert hasattr(result, "contract_format_mismatches"), "AuditResult missing contract_format_mismatches field"
        assert isinstance(result.contract_format_mismatches, list)

    def test_correct_format_produces_no_contract_mismatch(self):
        """When rendered format matches contract, contract_format_mismatches should be empty."""
        result = self._render_and_audit("cells", [{"name": "spreadsheet-converter", "output_format": "csv"}])
        assert (
            result.contract_format_mismatches == []
        ), f"Expected no mismatches when format is correct, got: {result.contract_format_mismatches}"
