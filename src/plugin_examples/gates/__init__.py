"""Central gate engine for pipeline validation."""

from plugin_examples.gates.models import GateResult, GateVerdict
from plugin_examples.gates.evaluator import (
    evaluate_gates,
    determine_verdict,
    is_publishable,
    is_publishable_verdict,
)
from plugin_examples.gates.writer import write_gate_results
from plugin_examples.gates.example_gates import (
    ExampleGateResult,
    AggregateGateResult,
    evaluate_example_gates,
    compute_aggregate_gates,
    compute_partitioned_verdict,
    build_pr_candidate_manifest,
    build_scenario_feedback,
)

__all__ = [
    "GateResult",
    "GateVerdict",
    "ExampleGateResult",
    "AggregateGateResult",
    "evaluate_gates",
    "evaluate_example_gates",
    "compute_aggregate_gates",
    "compute_partitioned_verdict",
    "build_pr_candidate_manifest",
    "build_scenario_feedback",
    "determine_verdict",
    "is_publishable",
    "is_publishable_verdict",
    "write_gate_results",
]
