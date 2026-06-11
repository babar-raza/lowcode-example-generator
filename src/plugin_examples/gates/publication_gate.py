"""Publication gate — blocks publication unless FormatContract authority is satisfied.

This gate checks that every example in a publication batch has:
1. A FormatContract in the store
2. Generated code that passes contract validation
3. Manifest with contract snapshot fields
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.format_authority.store import (
    get_contract,
    get_all_contracts,
    MissingFormatContractError,
)
from plugin_examples.gates.code_contract_validator import validate_code_against_contract

logger = logging.getLogger(__name__)

# Repo-local manifest must exist for publication to proceed
_REPO_ROOT = Path(__file__).resolve().parents[3]
_REPO_LOCAL_MANIFEST = _REPO_ROOT / "pipeline" / "format-authority" / "manifest.json"


@dataclass
class PublicationGateResult:
    """Result of publication gate evaluation for a single example."""

    scenario_id: str
    family: str
    type_name: str
    contract_exists: bool = False
    code_validates: bool = False
    manifest_has_contract: bool = False
    passed: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass
class BatchPublicationGateResult:
    """Result of publication gate evaluation for a batch of examples."""

    results: list[PublicationGateResult] = field(default_factory=list)
    all_passed: bool = False
    blocked_count: int = 0
    passed_count: int = 0


def check_repo_local_authority_exists() -> bool:
    """Check that repo-local format authority manifest exists."""
    return _REPO_LOCAL_MANIFEST.exists()


def evaluate_publication_gate(
    scenario_id: str,
    family: str,
    type_name: str,
    program_cs_path: Path | None = None,
    manifest_path: Path | None = None,
) -> PublicationGateResult:
    """Evaluate whether a single example is safe to publish.

    Returns a PublicationGateResult with pass/fail and reasons.
    """
    result = PublicationGateResult(
        scenario_id=scenario_id,
        family=family,
        type_name=type_name,
    )

    # Check 0: Repo-local authority must exist
    if not check_repo_local_authority_exists():
        result.reasons.append(
            f"Repo-local format authority missing: {_REPO_LOCAL_MANIFEST}. "
            f"Publication is FROZEN until format authority is committed."
        )
        return result

    # Check 1: FormatContract exists
    try:
        fc = get_contract(family, type_name)
        result.contract_exists = True
    except (MissingFormatContractError, KeyError) as exc:
        result.reasons.append(f"No FormatContract: {exc}")
        return result

    # Check 2: Generated code validates against contract
    if program_cs_path and program_cs_path.exists():
        code = program_cs_path.read_text(encoding="utf-8")
        validation = validate_code_against_contract(code, fc.to_dict())
        result.code_validates = validation.valid
        if not validation.valid:
            for check in validation.checks:
                if not check.get("passed", True):
                    result.reasons.append(
                        f"Code validation: {check.get('check', 'unknown')} — {check.get('detail', '')}"
                    )
    else:
        result.reasons.append("Program.cs not found — cannot validate code")

    # Check 3: Manifest has contract snapshot
    if manifest_path and manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            has_contract_id = bool(manifest.get("contract_id"))
            has_contract_hash = bool(manifest.get("contract_hash"))
            result.manifest_has_contract = has_contract_id and has_contract_hash
            if not result.manifest_has_contract:
                result.reasons.append("Manifest missing contract_id or contract_hash")
        except (json.JSONDecodeError, OSError) as exc:
            result.reasons.append(f"Manifest read error: {exc}")
    else:
        result.reasons.append("Manifest not found — cannot verify contract snapshot")

    result.passed = result.contract_exists and result.code_validates and result.manifest_has_contract

    if result.passed:
        logger.info("Publication gate PASSED: %s", scenario_id)
    else:
        logger.warning("Publication gate BLOCKED: %s — %s", scenario_id, "; ".join(result.reasons))

    return result


def evaluate_batch_publication_gate(
    examples: list[dict],
) -> BatchPublicationGateResult:
    """Evaluate publication gate for a batch of examples.

    Each dict in examples must have: scenario_id, family, type_name,
    and optionally project_dir (Path to the example project directory).
    """
    batch = BatchPublicationGateResult()

    for ex in examples:
        scenario_id = ex["scenario_id"]
        family = ex["family"]
        type_name = ex["type_name"]
        project_dir = ex.get("project_dir")

        program_cs = Path(project_dir) / "Program.cs" if project_dir else None
        manifest = Path(project_dir) / "example.manifest.json" if project_dir else None

        result = evaluate_publication_gate(
            scenario_id=scenario_id,
            family=family,
            type_name=type_name,
            program_cs_path=program_cs,
            manifest_path=manifest,
        )
        batch.results.append(result)

    batch.passed_count = sum(1 for r in batch.results if r.passed)
    batch.blocked_count = sum(1 for r in batch.results if not r.passed)
    batch.all_passed = batch.blocked_count == 0

    return batch


# --- Unfreeze criteria ---

UNFREEZE_CRITERIA = [
    "All 42 active types have FormatContract in store",
    "All components consume FormatContract (planner, codegen, manifest, populator)",
    "Contract-vs-system drift matrix has zero critical mismatches",
    "Code contract validator passes for all generated examples",
    "Stale-map guard tests pass (test_format_authority_no_stale_maps.py)",
    "Full test regression passes with no new failures",
    "Target repo correction plan documented for any defective examples",
]


@dataclass
class UnfreezeCheckResult:
    """Result of publication unfreeze criteria check."""

    criteria: list[dict] = field(default_factory=list)
    all_met: bool = False
    recommendation: str = "PUBLICATION_FROZEN"


def check_unfreeze_criteria() -> UnfreezeCheckResult:
    """Check whether publication unfreeze criteria are met.

    This is a lightweight check — it verifies store coverage and
    basic contract validity, not full pipeline integration.
    """
    from plugin_examples.format_capability.populator import _ACTIVE_TYPES

    result = UnfreezeCheckResult()

    # Criterion 1: All 42 types have contracts
    missing = []
    for family, types in _ACTIVE_TYPES.items():
        for type_name in types:
            try:
                get_contract(family, type_name)
            except (MissingFormatContractError, KeyError):
                missing.append(f"{family}:{type_name}")

    result.criteria.append(
        {
            "criterion": UNFREEZE_CRITERIA[0],
            "met": len(missing) == 0,
            "detail": f"{42 - len(missing)}/42 covered" + (f", missing: {missing}" if missing else ""),
        }
    )

    # Criterion 2: Components consume contract (structural check — just verify imports work)
    component_checks = []
    try:
        from plugin_examples.scenario_planner.planner import _infer_output_format

        component_checks.append("planner")
    except ImportError:
        pass
    try:
        from plugin_examples.generator.code_generator import _infer_output_extension

        component_checks.append("codegen")
    except ImportError:
        pass
    try:
        from plugin_examples.format_capability.populator import populate_manifest

        component_checks.append("populator")
    except ImportError:
        pass

    result.criteria.append(
        {
            "criterion": UNFREEZE_CRITERIA[1],
            "met": len(component_checks) >= 3,
            "detail": f"Components importable: {component_checks}",
        }
    )

    # Criteria 3-7 require test runs / external checks — record as "requires_verification"
    for crit in UNFREEZE_CRITERIA[2:]:
        result.criteria.append(
            {
                "criterion": crit,
                "met": None,
                "detail": "Requires test execution to verify",
            }
        )

    met_count = sum(1 for c in result.criteria if c["met"] is True)
    total = len(result.criteria)
    result.all_met = all(c["met"] is True for c in result.criteria)
    result.recommendation = (
        "PUBLICATION_UNFROZEN" if result.all_met else f"PUBLICATION_FROZEN ({met_count}/{total} criteria verifiable)"
    )

    return result
