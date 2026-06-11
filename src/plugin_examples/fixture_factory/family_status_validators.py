"""Family status validators FSV-01..06 — TC-FSV-001.

Validates that family YAML configs have correct status fields and that
status claims match pipeline/contracts/ ground truth.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class FsvResult:
    """Result of a single FSV validation rule."""
    rule_id: str
    passed: bool
    detail: str


# Allowed status values per pipeline/schemas/family-config.schema.json
ALLOWED_STATUSES = frozenset({"active", "disabled", "experimental", "discovery_only"})


def _load_family_configs(families_dir: Path) -> list[dict]:
    """Load all family YAML configs from directory."""
    configs = []
    for f in sorted(families_dir.iterdir()):
        if f.suffix not in (".yml", ".yaml"):
            continue
        with open(f, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        data["_filename"] = f.name
        data["_family_name"] = f.stem
        configs.append(data)
    return configs


def fsv_01_status_field_present(configs: list[dict]) -> list[FsvResult]:
    """FSV-01: Every family YAML has a 'status' field."""
    results = []
    for cfg in configs:
        has_status = "status" in cfg
        results.append(FsvResult(
            rule_id="FSV-01",
            passed=has_status,
            detail=f"{cfg['_filename']}: status={'present' if has_status else 'MISSING'}",
        ))
    return results


def fsv_02_status_value_valid(configs: list[dict]) -> list[FsvResult]:
    """FSV-02: Status value is from the allowed enum."""
    results = []
    for cfg in configs:
        status = cfg.get("status", "")
        valid = status in ALLOWED_STATUSES
        results.append(FsvResult(
            rule_id="FSV-02",
            passed=valid,
            detail=f"{cfg['_filename']}: status='{status}' {'OK' if valid else 'NOT IN ENUM ' + str(sorted(ALLOWED_STATUSES))}",
        ))
    return results


def fsv_03_active_has_contracts(configs: list[dict], contracts_dir: Path) -> list[FsvResult]:
    """FSV-03: Active families must have at least 1 contract directory."""
    results = []
    contract_families = set()
    if contracts_dir.is_dir():
        contract_families = {d.name for d in contracts_dir.iterdir() if d.is_dir()}
    for cfg in configs:
        if cfg.get("status") != "active":
            continue
        family = cfg["_family_name"]
        has_contract = family in contract_families
        results.append(FsvResult(
            rule_id="FSV-03",
            passed=has_contract,
            detail=f"{family}: active, contracts={'present' if has_contract else 'MISSING'}",
        ))
    return results


def fsv_04_discovery_not_published(configs: list[dict]) -> list[FsvResult]:
    """FSV-04: discovery_only/experimental families must not claim published status."""
    results = []
    for cfg in configs:
        status = cfg.get("status", "")
        if status not in ("discovery_only", "experimental"):
            continue
        # discovery_mode should not be 'publication' for discovery_only families
        disc_mode = cfg.get("discovery_mode", "")
        is_ok = disc_mode != "publication"
        results.append(FsvResult(
            rule_id="FSV-04",
            passed=is_ok,
            detail=f"{cfg['_family_name']}: status={status}, discovery_mode={disc_mode or 'unset'} {'OK' if is_ok else 'OVERCLAIM'}",
        ))
    return results


def fsv_05_active_count_matches_contracts(configs: list[dict], contracts_dir: Path) -> list[FsvResult]:
    """FSV-05: Count of active families matches contract subdirectory count."""
    active_families = [c["_family_name"] for c in configs if c.get("status") == "active"]
    contract_families = set()
    if contracts_dir.is_dir():
        contract_families = {d.name for d in contracts_dir.iterdir() if d.is_dir()}
    matches = set(active_families) == contract_families
    return [FsvResult(
        rule_id="FSV-05",
        passed=matches,
        detail=f"active={sorted(active_families)}, contracts={sorted(contract_families)}, match={matches}",
    )]


def fsv_06_no_orphan_references(configs: list[dict], contracts_dir: Path) -> list[FsvResult]:
    """FSV-06: No config references non-existent contract directory."""
    contract_families = set()
    if contracts_dir.is_dir():
        contract_families = {d.name for d in contracts_dir.iterdir() if d.is_dir()}
    results = []
    for cfg in configs:
        if cfg.get("status") != "active":
            continue
        family = cfg["_family_name"]
        exists = family in contract_families
        results.append(FsvResult(
            rule_id="FSV-06",
            passed=exists,
            detail=f"{family}: contract dir {'exists' if exists else 'MISSING'}",
        ))
    return results


def validate_all(
    repo_root: Path | None = None,
) -> list[FsvResult]:
    """Run all FSV validators against the repository."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    families_dir = repo_root / "pipeline" / "configs" / "families"
    contracts_dir = repo_root / "pipeline" / "contracts"

    if not families_dir.is_dir():
        return [FsvResult(rule_id="FSV-00", passed=False, detail=f"families dir not found: {families_dir}")]

    configs = _load_family_configs(families_dir)
    results = []
    results.extend(fsv_01_status_field_present(configs))
    results.extend(fsv_02_status_value_valid(configs))
    results.extend(fsv_03_active_has_contracts(configs, contracts_dir))
    results.extend(fsv_04_discovery_not_published(configs))
    results.extend(fsv_05_active_count_matches_contracts(configs, contracts_dir))
    results.extend(fsv_06_no_orphan_references(configs, contracts_dir))
    return results
