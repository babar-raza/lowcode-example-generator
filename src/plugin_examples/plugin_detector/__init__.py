"""Plugin namespace detection and source-of-truth proof reporting."""

from plugin_examples.plugin_detector.detector import detect_plugin_namespaces
from plugin_examples.plugin_detector.proof_reporter import (
    assert_source_of_truth_eligible,
    write_product_inventory,
    write_source_of_truth_proof,
)

__all__ = [
    "detect_plugin_namespaces",
    "assert_source_of_truth_eligible",
    "write_product_inventory",
    "write_source_of_truth_proof",
]
