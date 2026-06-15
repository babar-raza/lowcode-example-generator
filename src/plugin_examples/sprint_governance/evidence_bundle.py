"""Evidence bundle creation and validation for the post-sprint loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STAGE_REQUIRED_ARTIFACTS: dict[str, list[str]] = {
    "stage1": [
        "stage1-sprint-audit-summary.md",
        "stage1-l1-execution-issues.yaml",
        "stage1-l2-integration-issues.yaml",
        "stage1-l3-system-weaknesses.yaml",
        "stage1-next-stage-recommendation.yaml",
    ],
    "stage2": [
        "stage2-enhanced-master-plan.md",
        "stage2-taskcard-index.yaml",
        "stage2-ready-for-execution-verdict.yaml",
    ],
    "stage3": [
        "stage3-final-sprint-summary.yaml",
        "stage3-quality-evaluations.yaml",
        "stage3-taskcard-status.yaml",
        "stage3-evidence-manifest.yaml",
    ],
    "loop": [
        "loop-summary-classification.yaml",
        "loop-decision.yaml",
    ],
}


def validate_bundle(
    bundle_dir: Path,
    stage: str,
) -> tuple[bool, list[str]]:
    """Validate that a bundle directory contains required artifacts for a stage.

    Args:
        bundle_dir: Path to the evidence bundle directory.
        stage: One of 'stage1', 'stage2', 'stage3', 'loop'.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors: list[str] = []
    required = STAGE_REQUIRED_ARTIFACTS.get(stage, [])

    if not required:
        errors.append(f"Unknown stage: {stage}")
        return False, errors

    if not bundle_dir.is_dir():
        errors.append(f"Bundle directory does not exist: {bundle_dir}")
        return False, errors

    for artifact in required:
        artifact_path = bundle_dir / artifact
        if not artifact_path.exists():
            errors.append(f"Missing required artifact: {artifact}")
        elif artifact_path.stat().st_size == 0:
            errors.append(f"Empty artifact: {artifact}")

    return len(errors) == 0, errors


def create_bundle_manifest(bundle_dir: Path) -> dict[str, Any]:
    """Create a manifest of all files in a bundle directory.

    Returns a dict with file names, sizes, and types.
    """
    if not bundle_dir.is_dir():
        return {"files": [], "total_files": 0, "bundle_path": str(bundle_dir)}

    files: list[dict[str, Any]] = []
    for path in sorted(bundle_dir.rglob("*")):
        if path.is_file():
            files.append({
                "name": str(path.relative_to(bundle_dir)),
                "size_bytes": path.stat().st_size,
                "suffix": path.suffix,
            })

    return {
        "files": files,
        "total_files": len(files),
        "bundle_path": str(bundle_dir),
    }


def validate_manifest_vs_contents(
    manifest: dict[str, Any],
    bundle_dir: Path,
) -> list[str]:
    """Validate that manifest entries match actual bundle contents.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    manifest_files = {f["name"] for f in manifest.get("files", [])}
    actual_files = set()

    if bundle_dir.is_dir():
        for path in bundle_dir.rglob("*"):
            if path.is_file():
                actual_files.add(str(path.relative_to(bundle_dir)))

    # Files in manifest but not on disk
    for name in manifest_files - actual_files:
        errors.append(f"Manifest references missing file: {name}")

    return errors


def save_manifest(manifest: dict[str, Any], path: Path) -> None:
    """Save a bundle manifest to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
