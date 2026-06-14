"""Central gate engine for pipeline validation."""

from plugin_examples.gates.evaluator import (
    determine_verdict,
    evaluate_gates,
    is_publishable,
    is_publishable_verdict,
)
from plugin_examples.gates.example_gates import (
    AggregateGateResult,
    ExampleGateResult,
    build_pr_candidate_manifest,
    build_scenario_feedback,
    compute_aggregate_gates,
    compute_partitioned_verdict,
    evaluate_example_gates,
)
from plugin_examples.gates.models import GateResult, GateVerdict
from plugin_examples.gates.writer import write_gate_results

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
