"""Data models for evidence validation results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RuleResult:
    """Result of evaluating one validation rule."""
    rule_id: str
    description: str
    severity: str  # "FAILURE" | "WARNING"
    passed: bool
    evidence: str = ""
    failure_detail: str = ""


@dataclass
class ValidationReport:
    """Complete validation report for a sprint bundle."""
    bundle_dir: str
    sprint_id: str
    total_rules: int
    passed: int
    failed: int
    warnings: int
    overall_valid: bool
    rule_results: list[RuleResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "bundle_dir": self.bundle_dir,
            "sprint_id": self.sprint_id,
            "total_rules": self.total_rules,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "overall_valid": self.overall_valid,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "description": r.description,
                    "severity": r.severity,
                    "passed": r.passed,
                    "evidence": r.evidence,
                    "failure_detail": r.failure_detail,
                }
                for r in self.rule_results
            ],
        }
