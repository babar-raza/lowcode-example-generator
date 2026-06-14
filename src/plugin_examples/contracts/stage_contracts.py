"""Declarative stage I/O contracts for the pipeline.

Each stage declares which PipelineContext fields it reads (requires)
and which it writes (produces).  Contract tests verify that:

1. Every required field is produced by a prior stage.
2. No stage reads a field that no upstream stage produces.
3. The critical-path chain is acyclic and complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageContract:
    """Declares the I/O surface of a single pipeline stage."""

    stage_name: str
    order: int
    requires: frozenset[str] = field(default_factory=frozenset)
    produces: frozenset[str] = field(default_factory=frozenset)
    optional_reads: frozenset[str] = field(default_factory=frozenset)


# ---------------------------------------------------------------------------
# Critical-path stage contracts (ordered by pipeline execution)
# ---------------------------------------------------------------------------

STAGE_CONTRACTS: list[StageContract] = [
    StageContract(
        stage_name="load_config",
        order=1,
        requires=frozenset({"family"}),
        produces=frozenset({"config"}),
    ),
    StageContract(
        stage_name="nuget_fetch",
        order=2,
        requires=frozenset({"config"}),
        produces=frozenset({"download_manifest"}),
    ),
    StageContract(
        stage_name="extraction",
        order=4,
        requires=frozenset({"config", "download_manifest"}),
        produces=frozenset({"extraction"}),
    ),
    StageContract(
        stage_name="reflection",
        order=5,
        requires=frozenset({"extraction"}),
        produces=frozenset({"catalog", "catalog_path"}),
    ),
    StageContract(
        stage_name="plugin_detection",
        order=6,
        requires=frozenset({"catalog", "config"}),
        produces=frozenset({"detection", "proof_path"}),
        optional_reads=frozenset({"download_manifest"}),
    ),
    StageContract(
        stage_name="scenario_planning",
        order=12,
        requires=frozenset({"detection", "catalog", "config"}),
        produces=frozenset({"planning"}),
        optional_reads=frozenset({"fallback_candidates"}),
    ),
    StageContract(
        stage_name="generation",
        order=14,
        requires=frozenset({"planning", "config", "catalog"}),
        produces=frozenset({"generated_projects", "lifecycle_registry"}),
        optional_reads=frozenset({"llm_router", "llm_available", "template_mode"}),
    ),
    StageContract(
        stage_name="validation",
        order=15,
        requires=frozenset({"generated_projects"}),
        produces=frozenset({"validation_results"}),
        optional_reads=frozenset({"skip_run", "llm_available"}),
    ),
]

# Frozen lookup by stage name
CONTRACTS_BY_NAME: dict[str, StageContract] = {c.stage_name: c for c in STAGE_CONTRACTS}


def get_cumulative_produces(up_to_order: int) -> frozenset[str]:
    """Return the union of all fields produced by stages with order <= up_to_order.

    The 'family' field is always available (it's a PipelineContext init field).
    """
    init_fields = frozenset({"family", "run_id", "dry_run", "skip_run",
                             "template_mode", "require_llm",
                             "require_validation", "require_reviewer",
                             "repo_root", "run_dir", "evidence_dir"})
    produced = set(init_fields)
    for c in STAGE_CONTRACTS:
        if c.order <= up_to_order:
            produced |= c.produces
    return frozenset(produced)


def check_contract_consistency() -> list[str]:
    """Verify that every stage's requires are satisfied by prior stages.

    Returns a list of error messages (empty = all consistent).
    """
    errors: list[str] = []
    for contract in STAGE_CONTRACTS:
        available = get_cumulative_produces(contract.order - 1)
        missing = contract.requires - available
        if missing:
            errors.append(
                f"Stage '{contract.stage_name}' (order={contract.order}) "
                f"requires {sorted(missing)} but no prior stage produces them"
            )
    return errors
