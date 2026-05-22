"""Evidence Contract Computer — Sprint 63.

Computes the status of each category in an evidence-contract.json file by
inspecting actual bundle files. Replaces manual/hardcoded PENDING statuses.

Status values:
  PRESENT          — file exists, nonzero, semantic validation passed
  MISSING          — file does not exist
  ZERO_BYTES       — file exists but is empty (0 bytes)
  SEMANTIC_FAILED  — file exists and nonzero but semantic validation failed
  PENDING          — not yet computed (invalid at closure — this module eliminates PENDING)

Usage::

    from plugin_examples.evidence_contract_computer import EvidenceContractComputer
    computer = EvidenceContractComputer(
        contract_path=Path("reports/sprint63/evidence-contract.json"),
        repo_root=Path("."),
    )
    result = computer.compute()
    print(result.to_dict())
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


# Semantic validators keyed by partial string match on the semantic field
_SEMANTIC_IN_PROGRESS_PATTERN = re.compile(r"IN_PROGRESS")
_UNCHECKED_TODO_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
_TEST_ZERO_FAILED_PATTERN = re.compile(r"\b0 failed\b|\b0\s+fail", re.IGNORECASE)
_GIT_HEADER_PATTERNS = ["On branch", "HEAD detached at", "nothing to commit"]


@dataclass
class CategoryResult:
    """Result for one evidence contract category."""
    id: str
    name: str
    file: str
    blocking: bool
    status: str        # PRESENT | MISSING | ZERO_BYTES | SEMANTIC_FAILED | PENDING
    detail: str = ""   # Reason for failure


@dataclass
class ContractComputeResult:
    """Full computed result for an evidence contract."""
    contract_id: str
    computed_at: str
    total_categories: int
    present_count: int
    missing_count: int
    zero_bytes_count: int
    semantic_failed_count: int
    pending_count: int
    blocking_failures: int
    closure_valid: bool
    categories: list[CategoryResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "computed_at": self.computed_at,
            "total_categories": self.total_categories,
            "present": self.present_count,
            "missing": self.missing_count,
            "zero_bytes": self.zero_bytes_count,
            "semantic_failed": self.semantic_failed_count,
            "pending": self.pending_count,
            "blocking_failures": self.blocking_failures,
            "closure_valid": self.closure_valid,
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "file": c.file,
                    "blocking": c.blocking,
                    "status": c.status,
                    "detail": c.detail,
                }
                for c in self.categories
            ],
        }


class EvidenceContractComputer:
    """Computes evidence contract status from actual bundle files."""

    def __init__(self, contract_path: Path, repo_root: Path) -> None:
        self.contract_path = contract_path
        self.repo_root = repo_root

    def compute(self) -> ContractComputeResult:
        """Read the contract and compute status for every category."""
        contract = json.loads(self.contract_path.read_text(encoding="utf-8"))
        contract_id = contract.get("sprint_id", "unknown")

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        categories: list[CategoryResult] = []
        for cat in contract.get("required_evidence_categories", []):
            result = self._check_category(cat)
            categories.append(result)

        present = sum(1 for c in categories if c.status == "PRESENT")
        missing = sum(1 for c in categories if c.status == "MISSING")
        zero_bytes = sum(1 for c in categories if c.status == "ZERO_BYTES")
        semantic_failed = sum(1 for c in categories if c.status == "SEMANTIC_FAILED")
        pending = sum(1 for c in categories if c.status == "PENDING")
        blocking_failures = sum(
            1 for c in categories
            if c.blocking and c.status in ("MISSING", "ZERO_BYTES", "SEMANTIC_FAILED", "PENDING")
        )

        return ContractComputeResult(
            contract_id=contract_id,
            computed_at=now,
            total_categories=len(categories),
            present_count=present,
            missing_count=missing,
            zero_bytes_count=zero_bytes,
            semantic_failed_count=semantic_failed,
            pending_count=pending,
            blocking_failures=blocking_failures,
            closure_valid=(blocking_failures == 0),
            categories=categories,
        )

    def _check_category(self, cat: dict) -> CategoryResult:
        """Check a single category and return its status."""
        cat_id = cat.get("id", "?")
        cat_name = cat.get("name", "?")
        file_rel = cat.get("file", "")
        blocking = cat.get("blocking", True)
        semantic = cat.get("semantic", "")

        file_path = self.repo_root / file_rel

        if not file_path.exists():
            return CategoryResult(
                id=cat_id, name=cat_name, file=file_rel,
                blocking=blocking, status="MISSING",
                detail=f"File not found: {file_rel}",
            )

        size = file_path.stat().st_size
        if size == 0:
            return CategoryResult(
                id=cat_id, name=cat_name, file=file_rel,
                blocking=blocking, status="ZERO_BYTES",
                detail="File is empty (0 bytes)",
            )

        if semantic:
            fail_detail = self._check_semantic(file_path, semantic)
            if fail_detail:
                return CategoryResult(
                    id=cat_id, name=cat_name, file=file_rel,
                    blocking=blocking, status="SEMANTIC_FAILED",
                    detail=fail_detail,
                )

        return CategoryResult(
            id=cat_id, name=cat_name, file=file_rel,
            blocking=blocking, status="PRESENT",
        )

    def _check_semantic(self, file_path: Path, semantic: str) -> str:
        """Run semantic validation. Returns failure detail string, or '' on pass."""
        text = ""
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"Cannot read file: {exc}"

        # "must not contain IN_PROGRESS at closure"
        if "IN_PROGRESS" in semantic.upper() and "NOT" in semantic.upper():
            if "IN_PROGRESS" in text:
                return "File contains IN_PROGRESS marker"

        # "must have no unchecked [ ] items"
        if "unchecked" in semantic.lower() or "[ ]" in semantic:
            unchecked = _UNCHECKED_TODO_PATTERN.findall(text)
            if unchecked:
                return f"{len(unchecked)} unchecked [ ] items remain"

        # "must show 0 failed"
        if "0 failed" in semantic.lower():
            if not _TEST_ZERO_FAILED_PATTERN.search(text):
                return "File does not contain '0 failed' test result indicator"

        # "must show overall_valid=false"
        if "overall_valid=false" in semantic.lower():
            try:
                data = json.loads(text)
                if data.get("overall_valid", True) is not False:
                    return f"overall_valid is not false (got: {data.get('overall_valid')})"
            except (json.JSONDecodeError, ValueError):
                return "File is not valid JSON"

        # "must show overall_valid=true, no internal contradiction"
        if "overall_valid=true" in semantic.lower() and "contradiction" in semantic.lower():
            try:
                data = json.loads(text)
                if data.get("overall_valid", False) is not True:
                    return f"overall_valid is not true (got: {data.get('overall_valid')})"
                # Check for internal contradiction: failed=0 but a FAILURE rule is passed=false
                failed_count = data.get("failed", 0)
                rules = data.get("rules", [])
                actually_failed = [
                    r for r in rules
                    if not r.get("passed", True) and r.get("severity", "") == "FAILURE"
                ]
                if failed_count == 0 and actually_failed:
                    rule_ids = [r.get("rule_id", "?") for r in actually_failed]
                    return (
                        f"Internal contradiction: failed=0 but {len(actually_failed)} "
                        f"FAILURE rules have passed=false: {rule_ids}"
                    )
            except (json.JSONDecodeError, ValueError):
                return "File is not valid JSON"

        # "must have 42 entries with ..."
        if "42 entries" in semantic.lower() or "42/42" in semantic.lower():
            try:
                data = json.loads(text)
                records = data.get("records", data.get("entries", data.get("examples", [])))
                if len(records) < 42:
                    return f"Only {len(records)} entries (expected 42)"
                # Check for required fields
                if "output_format" in semantic.lower():
                    missing_fields = [
                        r.get("scenario_id", "?") for r in records
                        if not r.get("output_format")
                    ]
                    if missing_fields:
                        return f"{len(missing_fields)} records missing output_format"
                if "api_type" in semantic.lower():
                    missing_fields = [
                        r.get("scenario_id", "?") for r in records
                        if not r.get("api_type")
                    ]
                    if missing_fields:
                        return f"{len(missing_fields)} records missing api_type"
                if "readme_status" in semantic.lower():
                    missing_fields = [
                        r.get("scenario_id", "?") for r in records
                        if "readme_input_status" not in r and "readme_output_status" not in r
                    ]
                    if missing_fields:
                        return f"{len(missing_fields)} records missing readme status fields"
            except (json.JSONDecodeError, ValueError):
                return "File is not valid JSON"

        # "must list 6 families with file counts"
        if "6 families" in semantic.lower():
            try:
                data = json.loads(text)
                families = data.get("families", [])
                if len(families) < 6:
                    return f"Only {len(families)} families listed (expected 6)"
            except (json.JSONDecodeError, ValueError):
                return "File is not valid JSON"

        # "must show 0 PENDING blocking categories"
        if "0 pending" in semantic.lower() or "pending blocking" in semantic.lower():
            try:
                data = json.loads(text)
                categories = data.get("categories", [])
                pending = [c for c in categories if c.get("blocking") and c.get("status") == "PENDING"]
                if pending:
                    return f"{len(pending)} blocking categories still PENDING"
                bf = data.get("blocking_failures", -1)
                if bf > 0:
                    return f"{bf} blocking failures remain"
            except (json.JSONDecodeError, ValueError):
                return "File is not valid JSON"

        # "nonzero, git header present, captured AFTER final commit"
        if "git header" in semantic.lower():
            has_header = any(p in text for p in _GIT_HEADER_PATTERNS)
            if not has_header:
                return "File does not contain expected git status header"

        return ""  # semantic validation passed
