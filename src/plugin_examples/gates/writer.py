"""Write gate results to evidence directory."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from plugin_examples.gates.models import GateVerdict

logger = logging.getLogger(__name__)


def write_gate_results(verdict: GateVerdict, evidence_dir: Path) -> Path:
    """Write gate evaluation results to evidence directory.

    Args:
        verdict: The gate verdict to serialize.
        evidence_dir: Base evidence directory (contains a latest/ subdirectory).

    Returns:
        Path to the written JSON file.
    """
    latest = evidence_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "gate-results.json"

    data = {
        "verdict": verdict.verdict,
        "publishable": verdict.publishable,
        "all_required_passed": verdict.all_required_passed,
        "blocking_gates": verdict.blocking_gates,
        "gates": [
            {
                "gate_id": g.gate_id,
                "name": g.name,
                "status": g.status,
                "required": g.required,
                "evidence_files": g.evidence_files,
                "failure_reason": g.failure_reason,
                "downstream_blocked": g.downstream_blocked,
                "stage_name": g.stage_name,
            }
            for g in verdict.gates
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Gate results written: %s (verdict: %s)", path, verdict.verdict)
    return path
