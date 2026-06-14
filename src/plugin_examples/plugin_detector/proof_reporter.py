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
        "matched_plugin_namespaces": [m.namespace for m in detection_result.matched_namespaces],
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
        eligibility_reason = f"Plugin namespaces found: {', '.join(matched_ns)}"
    else:
        eligibility_reason = "No configured plugin namespace patterns matched any namespace in the API catalog"

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
        "namespace_count": len([ns for ns in (detection_result.matched_namespaces or [])])
        + len(detection_result.unmatched_patterns),
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
        raise SourceOfTruthGateError(f"Source-of-truth proof file not found: {path}")

    try:
        with open(proof_path) as f:
            proof = json.load(f)
    except json.JSONDecodeError as e:
        raise SourceOfTruthGateError(f"Source-of-truth proof contains invalid JSON: {e}") from e

    status = proof.get("eligibility_status")
    if status is None:
        raise SourceOfTruthGateError("Source-of-truth proof missing 'eligibility_status' field")

    if status != "eligible":
        reason = proof.get("eligibility_reason", "no reason provided")
        raise SourceOfTruthGateError(
            f"Source-of-truth gate failed: eligibility_status='{status}', " f"reason: {reason}"
        )

    logger.info("Source-of-truth gate PASSED: %s", path)


# ---------------------------------------------------------------------------
# Non-LowCode source-of-truth proof and gate
# ---------------------------------------------------------------------------

_GENERATION_READY_STATUSES = frozenset({"PROBE_CONFIRMED", "VERIFIED_PUBLISHABLE"})


def write_nonlowcode_source_of_truth_proof(
    *,
    family: str,
    registry_entries: list[dict],
    verification_dir: Path,
) -> Path:
    """Write source-of-truth proof for a non-LowCode family.

    Non-LowCode families derive authority from the capability registry
    (PROBE_CONFIRMED / VERIFIED_PUBLISHABLE entries) and optionally
    from plugin page hashes on products.aspose.net.

    Returns:
        Path to the written proof file.
    """
    latest_dir = verification_dir / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)

    proof_path = latest_dir / f"{family}-nonlowcode-source-of-truth-proof.json"

    generation_ready = [
        e for e in registry_entries
        if isinstance(e, dict) and e.get("status") in _GENERATION_READY_STATUSES
    ]

    # Collect page hashes (may be null)
    page_hashes = [
        e.get("plugin_page_hash") for e in generation_ready
        if e.get("plugin_page_hash")
    ]

    eligible = len(generation_ready) >= 1
    eligibility_status = "eligible" if eligible else "not_eligible"

    if eligible:
        slugs = [e.get("plugin_slug", "unknown") for e in generation_ready]
        eligibility_reason = (
            f"{len(generation_ready)} PROBE_CONFIRMED/VERIFIED_PUBLISHABLE entries: "
            + ", ".join(slugs)
        )
    else:
        eligibility_reason = (
            "No PROBE_CONFIRMED or VERIFIED_PUBLISHABLE entries in capability registry"
        )

    proof = {
        "proof_type": "nonlowcode_registry",
        "family": family,
        "registry_entry_count": len(generation_ready),
        "total_registry_entries": len(registry_entries),
        "registry_entry_statuses": [
            {
                "plugin_slug": e.get("plugin_slug", "unknown"),
                "status": e.get("status"),
                "confidence_score": e.get("confidence_score"),
                "probe_evidence": e.get("probe_evidence"),
                "assembly_fingerprint": e.get("assembly_fingerprint"),
            }
            for e in generation_ready
        ],
        "plugin_page_hash_count": len(page_hashes),
        "page_hash_source": "website_catalog" if page_hashes else "NOT_POPULATED",
        "eligibility_status": eligibility_status,
        "eligibility_reason": eligibility_reason,
    }

    with open(proof_path, "w") as f:
        json.dump(proof, f, indent=2)

    logger.info(
        "Non-LowCode SOT proof written: %s (status: %s, entries: %d)",
        proof_path,
        eligibility_status,
        len(generation_ready),
    )
    return proof_path


def assert_nonlowcode_source_of_truth_eligible(path: str) -> None:
    """Downstream gate: assert non-LowCode source-of-truth proof shows eligibility.

    Checks:
        1. Proof file exists and is valid JSON
        2. proof_type == "nonlowcode_registry"
        3. eligibility_status == "eligible"
        4. registry_entry_count >= 1

    Warns (not fails) when plugin_page_hash is not populated.

    Raises:
        SourceOfTruthGateError: If the gate check fails.
    """
    proof_path = Path(path)

    if not proof_path.exists():
        raise SourceOfTruthGateError(
            f"Non-LowCode SOT proof file not found: {path}"
        )

    try:
        with open(proof_path) as f:
            proof = json.load(f)
    except json.JSONDecodeError as e:
        raise SourceOfTruthGateError(
            f"Non-LowCode SOT proof contains invalid JSON: {e}"
        ) from e

    proof_type = proof.get("proof_type")
    if proof_type != "nonlowcode_registry":
        raise SourceOfTruthGateError(
            f"Non-LowCode SOT proof has wrong proof_type: '{proof_type}' "
            f"(expected 'nonlowcode_registry')"
        )

    status = proof.get("eligibility_status")
    if status is None:
        raise SourceOfTruthGateError(
            "Non-LowCode SOT proof missing 'eligibility_status' field"
        )

    if status != "eligible":
        reason = proof.get("eligibility_reason", "no reason provided")
        raise SourceOfTruthGateError(
            f"Non-LowCode SOT gate failed: eligibility_status='{status}', "
            f"reason: {reason}"
        )

    entry_count = proof.get("registry_entry_count", 0)
    if entry_count < 1:
        raise SourceOfTruthGateError(
            f"Non-LowCode SOT gate failed: registry_entry_count={entry_count} "
            f"(need >= 1 PROBE_CONFIRMED/VERIFIED_PUBLISHABLE)"
        )

    # Warn (not fail) when page hashes are not populated
    page_hash_source = proof.get("page_hash_source", "NOT_POPULATED")
    if page_hash_source == "NOT_POPULATED":
        logger.warning(
            "Non-LowCode SOT: plugin_page_hash not populated for '%s' — "
            "run 'catalog-discover' to enrich registry with page hashes",
            proof.get("family", "unknown"),
        )

    logger.info("Non-LowCode SOT gate PASSED: %s", path)
