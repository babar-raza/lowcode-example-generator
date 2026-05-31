"""Sprint 67 Phase 5 — Operation-kind/cardinality matrix tests.

Verifies that format authority contract JSON files have correct cardinality
values for all 42 types. Derives expected values from the contract files
themselves and checks internal consistency.
"""
import json
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO / "pipeline/format-authority/contracts"

FAMILIES = ["cells", "words", "pdf", "diagram", "email", "slides"]


def load_contract(family: str) -> dict:
    path = CONTRACTS_DIR / f"{family}.json"
    assert path.exists(), f"Contract missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


class TestContractCardinality:
    """Each type in the contract must have consistent input/output cardinality."""

    def test_all_contracts_load(self):
        for fam in FAMILIES:
            c = load_contract(fam)
            assert "types" in c, f"{fam}: missing 'types' key"
            assert len(c["types"]) > 0, f"{fam}: empty types list"

    def test_each_type_has_input_artifacts(self):
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                name = t.get("type_name", "unknown")
                assert "input_artifacts" in t, f"{fam}/{name}: missing input_artifacts"
                assert len(t["input_artifacts"]) > 0, f"{fam}/{name}: empty input_artifacts"

    def test_each_type_has_output_artifacts(self):
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                name = t.get("type_name", "unknown")
                assert "output_artifacts" in t, f"{fam}/{name}: missing output_artifacts"
                assert len(t["output_artifacts"]) > 0, f"{fam}/{name}: empty output_artifacts"

    def test_each_type_has_operation_kind(self):
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                name = t.get("type_name", "unknown")
                op = t.get("operation_kind", "")
                assert op, f"{fam}/{name}: operation_kind is blank"
                assert op in {"converter", "transform", "merger", "splitter",
                               "extractor", "exporter", "processor"}, \
                    f"{fam}/{name}: unknown operation_kind '{op}'"

    def test_merger_types_have_multi_input(self):
        """All types with operation_kind=merger must have multi input_cardinality."""
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                if t.get("operation_kind") == "merger":
                    name = t["type_name"]
                    inp_card = t["input_artifacts"][0].get("cardinality", "single")
                    assert inp_card == "multi", \
                        f"{fam}/{name}: merger must have multi input_cardinality, got '{inp_card}'"

    def test_splitter_types_have_multi_output(self):
        """All types with operation_kind=splitter must have multi output_cardinality."""
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                if t.get("operation_kind") == "splitter":
                    name = t["type_name"]
                    out_card = t.get("output_cardinality", "single")
                    assert out_card == "multi", \
                        f"{fam}/{name}: splitter must have multi output_cardinality, got '{out_card}'"

    def test_output_cardinality_matches_output_artifacts(self):
        """output_cardinality field must match cardinality in output_artifacts."""
        for fam in FAMILIES:
            c = load_contract(fam)
            for t in c["types"]:
                name = t.get("type_name", "unknown")
                out_card_field = t.get("output_cardinality", "single")
                out_artifacts = t.get("output_artifacts", [])
                if out_artifacts:
                    artifact_card = out_artifacts[0].get("cardinality", "single")
                    assert out_card_field == artifact_card, \
                        f"{fam}/{name}: output_cardinality={out_card_field} != artifact.cardinality={artifact_card}"

    def test_known_multi_input_types_have_multi_input(self):
        """Explicit known-multi-input types are verified against contract."""
        expected_multi_input = {
            ("cells", "SpreadsheetMerger"),
            ("words", "Merger"),
            ("words", "Comparer"),
            ("pdf", "Merger"),
            ("slides", "Merger"),
        }
        for fam, type_name in expected_multi_input:
            c = load_contract(fam)
            types_by_name = {t["type_name"]: t for t in c["types"]}
            assert type_name in types_by_name, f"Type not found: {fam}/{type_name}"
            t = types_by_name[type_name]
            inp_card = t["input_artifacts"][0].get("cardinality", "single")
            assert inp_card == "multi", \
                f"{fam}/{type_name}: expected multi input, got '{inp_card}'"

    def test_known_multi_output_types_have_multi_output(self):
        """Explicit known-multi-output types are verified against contract."""
        expected_multi_output = {
            ("cells", "SpreadsheetSplitter"),
            ("words", "Splitter"),
            ("pdf", "Splitter"),
            ("pdf", "Jpeg"),
            ("pdf", "Png"),
            ("pdf", "ImageExtractor"),
            ("email", "Converter"),
        }
        for fam, type_name in expected_multi_output:
            c = load_contract(fam)
            types_by_name = {t["type_name"]: t for t in c["types"]}
            assert type_name in types_by_name, f"Type not found: {fam}/{type_name}"
            t = types_by_name[type_name]
            out_card = t.get("output_cardinality", "single")
            assert out_card == "multi", \
                f"{fam}/{type_name}: expected multi output, got '{out_card}'"

    def test_total_type_count_is_42(self):
        """Total types across all contracts must be 42 (canonical main-class workflow types only).

        words/Signer excluded: no Aspose.Words.LowCode.Signer class; SignerContext is CONTEXT_MODEL;
          DigitalSignatureUtil.Sign is in Aspose.Words.DigitalSignatures, not LowCode namespace.
        slides/ForEach excluded: ForEach is NON_RUNNABLE_HELPER (utility iterator), not main workflow.
        """
        total = sum(
            len(load_contract(fam)["types"]) for fam in FAMILIES
        )
        assert total == 42, f"Expected 42 total types, got {total}"
