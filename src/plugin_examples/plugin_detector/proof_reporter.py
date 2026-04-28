"""Source-of-truth proof reporting and downstream gate."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.plugin_detector.detector import DetectionResult

logger = logging.getLogger(__name__)


class SourceOfTruthGateError(Exception):
    """Raised when source-of-truth eligibility gate fails."""


def write_product_inventory(
    *,
    family: str,
    package_id: str,
    resolved_version: str,
    detection_result: DetectionResult,
    manifests_dir: Path,
) -> Path:
    """Write product inventory to workspace/manifests/product-inventory.json.

    Creates or updates the inventory with the detection results for a family.

    Returns:
        Path to the written inventory file.
    """
    inventory_path = manifests_dir / "product-inventory.json"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    # Load existing inventory or create new
    inventory: dict = {}
    if inventory_path.exists():
        with open(inventory_path) as f:
            inventory = json.load(f)

    if "products" not in inventory:
        inventory["products"] = {}

    inventory["products"][family] = {
        "package_id": package_id,
        "resolved_version": resolved_version,
        "eligibility_status": "eligible" if detection_result.is_eligible else "not_eligible",
        "matched_plugin_namespaces": [
            m.namespace for m in detection_result.matched_namespaces
        ],
        "public_plugin_type_count": detection_result.public_plugin_type_count,
        "public_plugin_method_count": detection_result.public_plugin_method_count,
    }

    with open(inventory_path, "w") as f:
        json.dump(inventory, f, indent=2)

    logger.info("Product inventory updated: %s", inventory_path)
    return inventory_path


def write_source_of_truth_proof(
    *,
    family: str,
    package_id: str,
    resolved_version: str,
    nupkg_sha256: str | None,
    selected_target_framework: str | None,
    dll_path: str | None,
    xml_path: str | None,
    xml_warning: str | None,
    dependency_count: int,
    dependency_paths: list[str],
    api_catalog_path: str | None,
    detection_result: DetectionResult,
    verification_dir: Path,
) -> Path:
    """Write source-of-truth proof report.

    Writes to workspace/verification/latest/{family}-source-of-truth-proof.json.

    Returns:
        Path to the written proof file.
    """
    latest_dir = verification_dir / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)

    proof_path = latest_dir / f"{family}-source-of-truth-proof.json"

    eligibility_status = "eligible" if detection_result.is_eligible else "not_eligible"
    eligibility_reason: str
    if detection_result.is_eligible:
        matched_ns = [m.namespace for m in detection_result.matched_namespaces]
        eligibility_reason = (
            f"Plugin namespaces found: {', '.join(matched_ns)}"
        )
    else:
        eligibility_reason = (
            "No configured plugin namespace patterns matched any namespace in the API catalog"
        )

    proof = {
        "package_id": package_id,
        "resolved_version": resolved_version,
        "nupkg_sha256": nupkg_sha256,
        "selected_target_framework": selected_target_framework,
        "dll_path": dll_path,
        "xml_path": xml_path,
        "xml_warning": xml_warning,
        "dependency_count": dependency_count,
        "dependency_paths": dependency_paths,
        "api_catalog_path": api_catalog_path,
        "namespace_count": len(
            [ns for ns in (detection_result.matched_namespaces or [])]
        ) + len(detection_result.unmatched_patterns),
        "matched_plugin_namespaces": [
            {
                "namespace": m.namespace,
                "matched_by_pattern": m.matched_by_pattern,
                "public_type_count": m.public_type_count,
                "public_method_count": m.public_method_count,
            }
            for m in detection_result.matched_namespaces
        ],
        "unmatched_patterns": detection_result.unmatched_patterns,
        "public_plugin_type_count": detection_result.public_plugin_type_count,
        "public_plugin_method_count": detection_result.public_plugin_method_count,
        "eligibility_status": eligibility_status,
        "eligibility_reason": eligibility_reason,
    }

    with open(proof_path, "w") as f:
        json.dump(proof, f, indent=2)

    logger.info("Source-of-truth proof written: %s (status: %s)", proof_path, eligibility_status)
    return proof_path


def assert_source_of_truth_eligible(path: str) -> None:
    """Downstream gate: assert that a source-of-truth proof shows eligibility.

    Fails closed on:
        - Missing proof file
        - Invalid JSON
        - Missing eligibility_status field
        - eligibility_status != "eligible"

    Args:
        path: Path to the source-of-truth proof JSON file.

    Raises:
        SourceOfTruthGateError: If the gate check fails.
    """
    proof_path = Path(path)

    if not proof_path.exists():
        raise SourceOfTruthGateError(
            f"Source-of-truth proof file not found: {path}"
        )

    try:
        with open(proof_path) as f:
            proof = json.load(f)
    except json.JSONDecodeError as e:
        raise SourceOfTruthGateError(
            f"Source-of-truth proof contains invalid JSON: {e}"
        ) from e

    status = proof.get("eligibility_status")
    if status is None:
        raise SourceOfTruthGateError(
            "Source-of-truth proof missing 'eligibility_status' field"
        )

    if status != "eligible":
        reason = proof.get("eligibility_reason", "no reason provided")
        raise SourceOfTruthGateError(
            f"Source-of-truth gate failed: eligibility_status='{status}', "
            f"reason: {reason}"
        )

    logger.info("Source-of-truth gate PASSED: %s", path)
