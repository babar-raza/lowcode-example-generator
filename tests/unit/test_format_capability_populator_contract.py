"""TC-MEGA-G01: Verify format_capability populator uses FormatContract, not stale maps."""

from __future__ import annotations

import pytest

from plugin_examples.format_authority.store import reset_store


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


class TestPopulatorUsesContract:
    """Verify populate_manifest() reads from FormatContract, not _infer_output_format() maps."""

    def test_cells_spreadsheet_converter_csv_not_xlsx(self):
        from plugin_examples.format_capability.populator import populate_manifest

        m = populate_manifest("cells")
        sc = m.types.get("SpreadsheetConverter")
        assert sc is not None, "SpreadsheetConverter missing from cells manifest"
        assert sc.primary_output_format == ".csv", (
            f"SpreadsheetConverter primary_output_format is '{sc.primary_output_format}', "
            "expected '.csv' from contract (not '.xlsx' from stale map)"
        )

    def test_pdf_form_exporter_json_not_xml(self):
        from plugin_examples.format_capability.populator import populate_manifest

        m = populate_manifest("pdf")
        fe = m.types.get("FormExporter")
        assert fe is not None, "FormExporter missing from pdf manifest"
        assert fe.primary_output_format == ".json", (
            f"FormExporter primary_output_format is '{fe.primary_output_format}', "
            "expected '.json' from contract (not '.xml' from stale map)"
        )

    def test_no_dot_out_in_any_family(self):
        from plugin_examples.format_capability.populator import populate_manifest

        for family in ("cells", "words", "pdf", "diagram", "email", "slides"):
            m = populate_manifest(family)
            for type_name, cap in m.types.items():
                assert (
                    cap.primary_output_format != ".out"
                ), f"{family}:{type_name} primary_output_format is .out — contract not consumed"

    def test_all_six_families_populate(self):
        from plugin_examples.format_capability.populator import populate_manifest

        totals = 0
        for family in ("cells", "words", "pdf", "diagram", "email", "slides"):
            m = populate_manifest(family)
            assert len(m.types) > 0, f"Family {family} has no types in manifest"
            totals += len(m.types)
        assert totals == 42, f"Expected 42 total types across all families, got {totals}"

    def test_operation_kind_not_unknown_for_all_active(self):
        from plugin_examples.format_capability.populator import populate_manifest

        for family in ("cells", "words", "pdf", "diagram", "email", "slides"):
            m = populate_manifest(family)
            for type_name, cap in m.types.items():
                assert cap.operation_kind != "unknown", f"{family}:{type_name} has operation_kind=unknown"
