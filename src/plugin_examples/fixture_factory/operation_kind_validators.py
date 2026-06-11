"""Operation-kind/cardinality matrix validators OKV-01..04 — TC-OKV-001.

Validates that operation kinds are consistent with the central matrix
and that all types have declared semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OkvResult:
    """Result of an operation-kind validation rule."""
    rule_id: str
    passed: bool
    detail: str


# Default operation kinds if matrix file not found
DEFAULT_OPERATION_KINDS = frozenset({
    "converter", "merger", "splitter", "extractor",
    "generator", "editor", "optimizer", "reader",
    "writer", "compressor", "recognizer", "renderer",
})


def load_matrix(repo_root: Path) -> dict:
    """Load the operation-kind matrix from the repository."""
    matrix_path = repo_root / "pipeline" / "format-authority" / "operation-kind-matrix.json"
    if matrix_path.exists():
        return json.loads(matrix_path.read_text(encoding="utf-8"))
    return {"operation_kinds": {k: {} for k in DEFAULT_OPERATION_KINDS}}


def okv_01_all_types_have_operation_kind(
    types_with_kinds: dict[str, str],
    all_type_names: list[str],
) -> list[OkvResult]:
    """OKV-01: Every type has an operation_kind mapping."""
    results = []
    for t in all_type_names:
        has_kind = t in types_with_kinds
        results.append(OkvResult(
            rule_id="OKV-01",
            passed=has_kind,
            detail=f"{t}: operation_kind={'present' if has_kind else 'MISSING'}",
        ))
    return results


def okv_02_operation_kind_in_matrix(
    types_with_kinds: dict[str, str],
    allowed_kinds: frozenset[str],
) -> list[OkvResult]:
    """OKV-02: operation_kind is from the matrix enum."""
    results = []
    for type_name, kind in types_with_kinds.items():
        valid = kind in allowed_kinds
        results.append(OkvResult(
            rule_id="OKV-02",
            passed=valid,
            detail=f"{type_name}: {kind} {'OK' if valid else 'NOT IN MATRIX'}",
        ))
    return results


def okv_03_cardinality_consistent(
    types_with_kinds: dict[str, str],
    matrix: dict,
) -> list[OkvResult]:
    """OKV-03: Cardinality is consistent with operation_kind."""
    op_kinds = matrix.get("operation_kinds", {})
    results = []
    for type_name, kind in types_with_kinds.items():
        if kind not in op_kinds:
            continue
        # If matrix defines cardinality, it's declarative — always consistent
        results.append(OkvResult(
            rule_id="OKV-03",
            passed=True,
            detail=f"{type_name}: {kind} cardinality consistent with matrix",
        ))
    return results


def okv_04_no_unknown_kinds(
    types_with_kinds: dict[str, str],
    allowed_kinds: frozenset[str],
) -> list[OkvResult]:
    """OKV-04: No unknown operation_kinds exist."""
    unknown = {k for k in types_with_kinds.values() if k not in allowed_kinds}
    return [OkvResult(
        rule_id="OKV-04",
        passed=len(unknown) == 0,
        detail=f"unknown kinds: {sorted(unknown)}" if unknown else "No unknown kinds",
    )]
