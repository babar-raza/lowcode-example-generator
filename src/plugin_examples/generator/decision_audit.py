"""Generation decision audit — TC-AUDIT-001.

Writes a per-scenario decision audit JSON recording which generation
strategy was selected and why.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_generation_decision_audit(ctx) -> Path | None:
    """Write generation decision audit JSON to evidence directory.

    Args:
        ctx: PipelineContext with generated_projects populated.

    Returns:
        Path to the written audit file, or None if no projects.
    """
    if not ctx.generated_projects:
        return None

    records = []
    for proj in ctx.generated_projects:
        record = {
            "scenario_id": proj.get("scenario_id", ""),
            "family": ctx.family,
            "type_name": proj.get("type_name", proj.get("target_type", "")),
            "operation_kind": proj.get("operation_kind", ""),
            "generation_strategy": proj.get("generation_strategy", "unknown"),
            "template_first_eligible": proj.get("template_first_eligible", False),
            "llm_available": ctx.llm_available,
            "status": proj.get("status", ""),
            "failure_reason": proj.get("failure_reason"),
            "repair_attempts": proj.get("repair_attempts", 0),
        }
        records.append(record)

    audit = {
        "audit_type": "generation_decision",
        "family": ctx.family,
        "run_id": ctx.run_id,
        "total_scenarios": len(records),
        "strategy_counts": _count_strategies(records),
        "records": records,
    }

    output_path = Path(ctx.evidence_dir) / "generation-decision-audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    logger.info("Generation decision audit written to %s (%d records)", output_path, len(records))
    return output_path


def _count_strategies(records: list[dict]) -> dict[str, int]:
    """Count occurrences of each generation strategy."""
    counts: dict[str, int] = {}
    for r in records:
        strategy = r.get("generation_strategy", "unknown")
        counts[strategy] = counts.get(strategy, 0) + 1
    return counts
