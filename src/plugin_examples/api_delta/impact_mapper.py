"""Map API delta to example impact — which examples need attention."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.api_delta.delta_engine import DeltaResult

logger = logging.getLogger(__name__)


@dataclass
class ExampleImpact:
    """Impact assessment for a single existing example."""
    example_id: str
    impact_type: str  # new_api_available, api_removed, api_modified, no_impact
    affected_symbols: list[str] = field(default_factory=list)
    action: str = ""  # regenerate, deprecate, update, none


@dataclass
class ImpactReport:
    """Overall impact assessment."""
    delta_summary: dict = field(default_factory=dict)
    new_api_examples_needed: list[dict] = field(default_factory=list)
    existing_example_impacts: list[ExampleImpact] = field(default_factory=list)
    initial_run: bool = False


def map_impact(
    delta: DeltaResult,
    existing_examples_index: dict | None = None,
) -> ImpactReport:
    """Map API delta to example impact.

    Args:
        delta: Computed API delta.
        existing_examples_index: Index of existing examples with their
            used symbols (from example miner). None if no existing examples.

    Returns:
        ImpactReport with needed actions.
    """
    report = ImpactReport(
        initial_run=delta.initial_run,
        delta_summary={
            "old_version": delta.old_version,
            "new_version": delta.new_version,
            "added_types": len(delta.added_types),
            "removed_types": len(delta.removed_types),
            "modified_types": len(delta.modified_types),
        },
    )

    # New types need new examples
    for td in delta.added_types:
        report.new_api_examples_needed.append({
            "full_name": td.full_name,
            "namespace": td.namespace,
            "methods": td.added_methods,
            "properties": td.added_properties,
        })

    if not existing_examples_index:
        return report

    # Check existing examples for impact
    examples = existing_examples_index.get("examples", [])
    removed_symbols = {td.full_name for td in delta.removed_types}
    modified_symbols = {td.full_name for td in delta.modified_types}

    for ex in examples:
        ex_id = ex.get("example_id", "unknown")
        used_symbols = set(ex.get("used_symbols", []))

        removed_hits = used_symbols & removed_symbols
        modified_hits = used_symbols & modified_symbols

        if removed_hits:
            report.existing_example_impacts.append(ExampleImpact(
                example_id=ex_id,
                impact_type="api_removed",
                affected_symbols=sorted(removed_hits),
                action="deprecate",
            ))
        elif modified_hits:
            report.existing_example_impacts.append(ExampleImpact(
                example_id=ex_id,
                impact_type="api_modified",
                affected_symbols=sorted(modified_hits),
                action="update",
            ))

    logger.info(
        "Impact: %d new APIs, %d existing impacts",
        len(report.new_api_examples_needed),
        len(report.existing_example_impacts),
    )
    return report


def write_impact_report(
    impact: ImpactReport,
    verification_dir: Path,
) -> Path:
    """Write example impact report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "example-impact-report.json"

    report = {
        "initial_run": impact.initial_run,
        "delta_summary": impact.delta_summary,
        "new_api_examples_needed": impact.new_api_examples_needed,
        "existing_example_impacts": [
            {
                "example_id": ei.example_id,
                "impact_type": ei.impact_type,
                "affected_symbols": ei.affected_symbols,
                "action": ei.action,
            }
            for ei in impact.existing_example_impacts
        ],
    }

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("Impact report written: %s", path)
    return path
