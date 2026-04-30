"""Tests for the Runtime Scenario Selection Healing Sprint.

Covers: type classification, consumer mapping, entrypoint scoring,
strict scenario readiness, runtime failure feedback, and reporting.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.scenario_planner.type_classifier import (
    STANDALONE_ROLES,
    NON_STANDALONE_ROLES,
    WORKFLOW_ROOT,
    OPERATION_FACADE,
    PROVIDER_CALLBACK,
    OPTIONS,
    ABSTRACT_BASE,
    INTERFACE_CONTRACT,
    ENUM,
    classify_type,
    classify_catalog,
)
from plugin_examples.scenario_planner.consumer_mapper import build_consumer_map
from plugin_examples.scenario_planner.entrypoint_scorer import (
    score_entrypoint,
    EntrypointScore,
)
from plugin_examples.scenario_planner.runtime_feedback import (
    classify_runtime_failure,
    RuntimeFailureClassification,
)
from plugin_examples.scenario_planner.planner import plan_scenarios, Scenario


def _make_proof(tmp_path: Path, eligible: bool = True) -> str:
    proof_path = tmp_path / "proof.json"
    proof_path.write_text(json.dumps({
        "eligibility_status": "eligible" if eligible else "not_eligible",
        "eligibility_reason": "test",
    }))
    return str(proof_path)


def _make_workflow_root_type(name="SpreadsheetConverter", full_name=None):
    return {
        "name": name,
        "full_name": full_name or f"Aspose.Cells.LowCode.{name}",
        "kind": "class",
        "is_obsolete": False,
        "methods": [
            {"name": "Process", "return_type": "void", "is_static": True,
             "is_obsolete": False, "parameters": [
                 {"name": "loadOptions", "type": "Aspose.Cells.LowCode.LowCodeLoadOptions"},
                 {"name": "saveOptions", "type": "Aspose.Cells.LowCode.LowCodeSaveOptions"},
             ]},
        ],
        "properties": [],
        "constructors": [],
    }


def _make_provider_type(name="LowCodeSaveOptionsProviderOfAssembling", full_name=None):
    return {
        "name": name,
        "full_name": full_name or f"Aspose.Cells.LowCode.{name}",
        "kind": "class",
        "is_obsolete": False,
        "methods": [
            {"name": "GetSaveOptions", "return_type": "LowCodeSaveOptions",
             "is_static": False, "is_obsolete": False,
             "parameters": [
                 {"name": "splitPartInfo", "type": "Aspose.Cells.LowCode.SplitPartInfo"},
             ]},
        ],
        "properties": [
            {"name": "BuildPathWithSheetAlways", "type": "System.Boolean"},
        ],
        "constructors": [{"parameters": []}],
    }


def _make_options_type(name="LowCodeSaveOptions", full_name=None):
    return {
        "name": name,
        "full_name": full_name or f"Aspose.Cells.LowCode.{name}",
        "kind": "class",
        "is_obsolete": False,
        "methods": [],
        "properties": [
            {"name": "SaveFormat", "type": "System.Int32"},
            {"name": "OutputFileName", "type": "System.String"},
        ],
        "constructors": [{"parameters": []}],
    }


def _make_catalog_with_types(types):
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [{
            "namespace": "Aspose.Cells.LowCode",
            "types": types,
        }],
    }


class TestTypeClassifier:
    """Test 1: Type role classification correctly identifies roles."""

    def test_workflow_root_classified(self):
        role = classify_type(_make_workflow_root_type())
        assert role.role == WORKFLOW_ROOT

    def test_provider_classified(self):
        role = classify_type(_make_provider_type())
        assert role.role == PROVIDER_CALLBACK

    def test_options_classified(self):
        role = classify_type(_make_options_type())
        assert role.role == OPTIONS

    def test_abstract_classified(self):
        role = classify_type({
            "name": "AbstractLowCodeLoadOptionsProvider",
            "full_name": "Aspose.Cells.LowCode.AbstractLowCodeLoadOptionsProvider",
            "kind": "abstract_class", "is_obsolete": False,
            "methods": [], "properties": [], "constructors": [],
        })
        assert role.role == ABSTRACT_BASE

    def test_enum_classified(self):
        role = classify_type({
            "name": "SaveFormat", "full_name": "Aspose.Cells.LowCode.SaveFormat",
            "kind": "enum", "is_obsolete": False,
        })
        assert role.role == ENUM

    def test_classify_catalog_returns_all(self):
        types = [_make_workflow_root_type(), _make_provider_type(), _make_options_type()]
        catalog = _make_catalog_with_types(types)
        roles = classify_catalog(catalog, ["Aspose.Cells.LowCode"])
        assert len(roles) == 3


class TestConsumerMapper:
    """Test 2: Consumer relationship mapping finds consumers."""

    def test_finds_consumers_for_options(self):
        workflow = _make_workflow_root_type()
        options = _make_options_type()
        catalog = _make_catalog_with_types([workflow, options])
        cmap = build_consumer_map(catalog, ["Aspose.Cells.LowCode"])
        # SpreadsheetConverter.Process takes LowCodeSaveOptions as parameter
        consumers = cmap.get("Aspose.Cells.LowCode.LowCodeSaveOptions", [])
        assert len(consumers) >= 1
        assert consumers[0]["consumer_type"] == "Aspose.Cells.LowCode.SpreadsheetConverter"

    def test_provider_has_no_consumers_when_alone(self):
        provider = _make_provider_type()
        catalog = _make_catalog_with_types([provider])
        cmap = build_consumer_map(catalog, ["Aspose.Cells.LowCode"])
        consumers = cmap.get("Aspose.Cells.LowCode.LowCodeSaveOptionsProviderOfAssembling", [])
        assert len(consumers) == 0


class TestEntrypointScorer:
    """Test 3: Entrypoint scoring rejects non-standalone types."""

    def test_workflow_root_is_runnable(self):
        t = _make_workflow_root_type()
        role = classify_type(t)
        score = score_entrypoint(t, role, {})
        assert score.runnable is True
        assert score.score > 0

    def test_provider_not_runnable(self):
        t = _make_provider_type()
        role = classify_type(t)
        score = score_entrypoint(t, role, {})
        assert score.runnable is False
        assert score.rejection_reason is not None

    def test_options_not_runnable(self):
        t = _make_options_type()
        role = classify_type(t)
        score = score_entrypoint(t, role, {})
        assert score.runnable is False


class TestStricterScenarioReadiness:
    """Test 4: Planner enforces strict readiness with type roles."""

    def test_provider_type_blocked_not_ready(self, tmp_path):
        """Provider/callback types must NOT be standalone scenario roots."""
        proof = _make_proof(tmp_path)
        catalog = _make_catalog_with_types([
            _make_workflow_root_type(),
            _make_provider_type(),
        ])
        result = plan_scenarios(
            family="cells",
            catalog=catalog,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        ready_types = [s.target_type for s in result.ready_scenarios]
        blocked_types = [s.target_type for s in result.blocked_scenarios]
        assert "Aspose.Cells.LowCode.LowCodeSaveOptionsProviderOfAssembling" not in ready_types
        assert "Aspose.Cells.LowCode.LowCodeSaveOptionsProviderOfAssembling" in blocked_types

    def test_workflow_root_is_ready(self, tmp_path):
        """Workflow root types should be ready scenarios."""
        proof = _make_proof(tmp_path)
        catalog = _make_catalog_with_types([_make_workflow_root_type()])
        result = plan_scenarios(
            family="cells",
            catalog=catalog,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        ready_types = [s.target_type for s in result.ready_scenarios]
        assert "Aspose.Cells.LowCode.SpreadsheetConverter" in ready_types

    def test_options_type_blocked(self, tmp_path):
        """Options types must NOT be standalone scenario roots."""
        proof = _make_proof(tmp_path)
        catalog = _make_catalog_with_types([_make_options_type()])
        result = plan_scenarios(
            family="cells",
            catalog=catalog,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        ready_types = [s.target_type for s in result.ready_scenarios]
        assert "Aspose.Cells.LowCode.LowCodeSaveOptions" not in ready_types

    def test_only_standalone_roles_become_ready(self, tmp_path):
        """No non-standalone role should ever appear in ready scenarios."""
        proof = _make_proof(tmp_path)
        catalog = _make_catalog_with_types([
            _make_workflow_root_type(),
            _make_provider_type(),
            _make_options_type(),
            {
                "name": "AbstractBase", "full_name": "Aspose.Cells.LowCode.AbstractBase",
                "kind": "abstract_class", "is_obsolete": False,
                "methods": [{"name": "M", "return_type": "void", "is_static": False,
                             "is_obsolete": False, "parameters": []}],
                "properties": [], "constructors": [],
            },
        ])
        result = plan_scenarios(
            family="cells",
            catalog=catalog,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        for s in result.ready_scenarios:
            role = classify_type(_find_type_in_catalog(catalog, s.target_type))
            assert role.role in STANDALONE_ROLES, (
                f"Ready scenario {s.scenario_id} has non-standalone role {role.role}"
            )


class TestRuntimeFailureFeedback:
    """Test 5: Runtime failure feedback classifies errors correctly."""

    def test_nullref_classified_as_context_required(self):
        result = classify_runtime_failure(
            scenario_id="test-1", exit_code=1,
            stderr="Unhandled exception. System.NullReferenceException: Object reference not set",
        )
        assert result.classification == "blocked_runtime_context_required"
        assert result.actionable is True

    def test_file_not_found_classified(self):
        result = classify_runtime_failure(
            scenario_id="test-2", exit_code=1,
            stderr="System.IO.FileNotFoundException: Could not find file 'input.xlsx'",
        )
        assert result.classification == "blocked_missing_fixture"
        assert result.actionable is True

    def test_unknown_failure_classified(self):
        result = classify_runtime_failure(
            scenario_id="test-3", exit_code=42,
            stderr="Something unexpected happened",
        )
        assert result.classification == "unknown_runtime_failure"

    def test_argument_null_classified(self):
        result = classify_runtime_failure(
            scenario_id="test-4", exit_code=1,
            stderr="System.ArgumentNullException: Value cannot be null. (Parameter 'path')",
        )
        assert result.classification == "blocked_null_argument"
        assert result.actionable is True


class TestReportingLanguage:
    """Test 6: Reporting uses 'stages executed' not 'stages passed'."""

    def test_main_output_says_executed(self):
        # Verify the __main__.py template uses correct language
        import importlib.util
        spec = importlib.util.find_spec("plugin_examples.__main__")
        source = Path(spec.origin).read_text(encoding="utf-8")
        assert "stages executed" in source
        assert '"stages passed"' not in source and "stages passed" not in source.split("stages executed")[0]


class TestEvidenceFiles:
    """Test evidence file writing for new modules."""

    def test_type_classification_evidence(self, tmp_path):
        from plugin_examples.scenario_planner.type_classifier import write_type_role_classification
        roles = classify_catalog(
            _make_catalog_with_types([_make_workflow_root_type(), _make_provider_type()]),
            ["Aspose.Cells.LowCode"],
        )
        path = write_type_role_classification(roles, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total_types"] == 2
        assert "workflow_root" in data["role_summary"]

    def test_entrypoint_scores_evidence(self, tmp_path):
        from plugin_examples.scenario_planner.entrypoint_scorer import write_entrypoint_scores
        t = _make_workflow_root_type()
        role = classify_type(t)
        scores = [score_entrypoint(t, role, {})]
        path = write_entrypoint_scores(scores, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["runnable_count"] >= 1

    def test_runtime_feedback_evidence(self, tmp_path):
        from plugin_examples.scenario_planner.runtime_feedback import (
            write_runtime_failure_classifications,
        )
        classifications = [
            classify_runtime_failure("s1", 1, stderr="System.NullReferenceException: test"),
        ]
        path = write_runtime_failure_classifications(classifications, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total_failures"] == 1
        assert "blocked_runtime_context_required" in data["classification_summary"]


def _find_type_in_catalog(catalog: dict, full_name: str) -> dict:
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            if t.get("full_name") == full_name:
                return t
    return {}
