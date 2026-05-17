"""
Strict Evidence Contract for LowCode Sprint Bundles.

Defines required artifacts for a valid sprint evidence bundle and validates
that a given bundle (directory or ZIP) meets the contract. Thin bundles with
fewer than the required artifacts fail validation.

Usage:
    from plugin_examples.evidence_contract import StrictEvidenceContract, ContractResult
    result = StrictEvidenceContract().validate_zip(path_to_zip)
    if not result.passed:
        raise RuntimeError(f"Bundle contract failed: {result.failures}")
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


# ---------------------------------------------------------------------------
# Required artifact categories (filename patterns, matched against ZIP entries)
# ---------------------------------------------------------------------------

#: Required artifact categories and at least one matching filename pattern per category.
#: A category passes if ANY file in the ZIP matches its pattern list (basename match).
REQUIRED_CATEGORIES: dict[str, list[str]] = {
    "git_status_initial": ["git-status-initial.txt"],
    "git_status_final": ["git-status-final.txt"],
    "git_diff_initial": ["git-diff-initial.patch"],
    "git_diff_final": ["git-diff-final.patch"],
    "git_log_proof": ["git-log-proof.txt"],
    "changed_files": ["changed-files.txt"],
    "source_state_classification": ["source-state-classification.json"],
    "test_summary": ["test-summary.json"],
    "test_full_log": ["test-full.log", "test-full-not-run.md"],
    "final_verdict": ["final-verdict.md"],
    "final_state_summary": ["final-state-summary.yaml"],
    "bundle_contract_definition": ["bundle-contract-definition.json"],
    "bundle_contract_validation": ["bundle-contract-validation-report.json"],
    "publication_mode_decision": ["publication-mode-decision.json"],
    "github_token_readiness": ["github-token-readiness-report.json"],
    "pr3_audit_or_result": [
        "pdf-pr3-final-package-audit.json",
        "pdf-pr3-publication-result.json",
        "pdf-pr3-approval-blocked.md",
    ],
    "pr5_audit_or_result": [
        "pdf-pr5-final-package-audit.json",
        "pdf-pr5-publication-result.json",
        "pdf-pr5-approval-blocked.md",
    ],
    "pr6_audit_or_result": [
        "pdf-pr6-final-package-audit.json",
        "pdf-pr6-publication-result.json",
        "pdf-pr6-approval-blocked.md",
    ],
    "pr7_audit_or_result": [
        "pdf-pr7-final-package-audit.json",
        "pdf-pr7-publication-result.json",
        "pdf-pr7-approval-blocked.md",
    ],
    "pr8_audit_or_result": [
        "pdf-pr8-final-package-audit.json",
        "pdf-pr8-publication-result.json",
        "pdf-pr8-approval-blocked.md",
    ],
    "pr9_audit_or_result": [
        "pdf-pr9-final-package-audit.json",
        "pdf-pr9-publication-result.json",
        "pdf-pr9-approval-blocked.md",
    ],
    "post_publication": [
        "post-publication-pr-verification-report.json",
        "post-publication-not-run-approval-blocked.md",
    ],
    "formimporter_defect": [
        "pdf-formimporter-defect-package-final-report.json",
        "pdf-formimporter-upstream-issue-final.md",
    ],
    "pdf_closeout_matrix": ["pdf-final-denominator-closeout-matrix.json"],
    "pdf_max_coverage": ["pdf-maximum-achievable-coverage-report.md"],
    "email_runtime": ["email-final-runtime-status.json"],
    "slides_runtime": ["slides-final-runtime-status.json"],
    "words_guard": ["words-final-guard-report.json"],
    "cells_guard": ["cells-final-guard-report.json"],
    "diagram_guard": ["diagram-final-guard-report.json"],
    "all_family_scoreboard_json": ["all-family-launch-scoreboard.json"],
    "all_family_scoreboard_md": ["all-family-launch-scoreboard.md"],
    "families_needing_work": ["families-needing-launch-work.json"],
    "release_state": ["release-state-reconciliation-report.json"],
    "taskcard_reconciliation": ["taskcard-reconciliation-report.json"],
    "taskcard_state": ["taskcard-state-after-sprint28.json"],
}

#: Patterns indicating raw secrets present in a file (lines matching these must not appear).
SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ghp_[A-Za-z0-9]{36}", re.IGNORECASE),  # GitHub classic PAT
    re.compile(r"github_pat_[A-Za-z0-9_]{82}", re.IGNORECASE),  # GitHub fine-grained PAT
    re.compile(r"sk-[A-Za-z0-9]{48}", re.IGNORECASE),  # OpenAI key
    re.compile(r"Bearer [A-Za-z0-9\-_\.]{20,}", re.IGNORECASE),  # Generic Bearer token
]

#: Minimum number of unique categories that must pass (all of REQUIRED_CATEGORIES).
MIN_CATEGORIES_REQUIRED = len(REQUIRED_CATEGORIES)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ContractResult:
    passed: bool
    categories_found: list[str] = field(default_factory=list)
    categories_missing: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    secret_violations: list[str] = field(default_factory=list)
    file_count: int = 0
    verdict: str = ""

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"ContractResult[{status}] files={self.file_count} "
            f"categories={len(self.categories_found)}/{MIN_CATEGORIES_REQUIRED} "
            f"failures={len(self.failures)}"
        )


# ---------------------------------------------------------------------------
# Contract validator
# ---------------------------------------------------------------------------

class StrictEvidenceContract:
    """
    Validates that a sprint evidence ZIP meets the strict evidence contract.

    The contract requires every category in REQUIRED_CATEGORIES to be satisfied
    by at least one file in the ZIP. It also scans text files for raw secrets.
    """

    def validate_zip(self, zip_path: str | Path) -> ContractResult:
        """
        Validate a ZIP file against the strict evidence contract.

        Parameters
        ----------
        zip_path:
            Absolute or relative path to the ZIP file.

        Returns
        -------
        ContractResult
            Result object with passed/failed status and details.
        """
        zip_path = Path(zip_path)
        result = ContractResult(passed=False)

        if not zip_path.exists():
            result.failures.append(f"ZIP file not found: {zip_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        if not zip_path.is_absolute():
            result.warnings.append(
                "ZIP path is relative; contract requires absolute path in final response."
            )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                result.file_count = len(names)
                basenames = {Path(n).name for n in names}

                # Check categories
                for category, patterns in REQUIRED_CATEGORIES.items():
                    if any(p in basenames for p in patterns):
                        result.categories_found.append(category)
                    else:
                        result.categories_missing.append(category)
                        result.failures.append(
                            f"Missing category '{category}' — "
                            f"expected one of: {patterns}"
                        )

                # Scan text files for secrets
                for name in names:
                    if name.endswith((".json", ".md", ".txt", ".yaml", ".yml", ".patch", ".log")):
                        try:
                            content = zf.read(name).decode("utf-8", errors="replace")
                            for pattern in SECRET_PATTERNS:
                                if pattern.search(content):
                                    violation = f"Possible secret in {name}: pattern {pattern.pattern}"
                                    result.secret_violations.append(violation)
                                    result.failures.append(violation)
                        except Exception:
                            pass  # Binary file — skip

        except zipfile.BadZipFile as e:
            result.failures.append(f"ZIP is invalid/corrupt: {e}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        # Final pass/fail
        if result.failures:
            result.passed = False
            result.verdict = "BUNDLE_CONTRACT_FAILED"
        else:
            result.passed = True
            result.verdict = "BUNDLE_CONTRACT_PASSED"

        return result

    def validate_directory(self, dir_path: str | Path) -> ContractResult:
        """
        Validate an unpacked directory of evidence artifacts against the contract.

        Parameters
        ----------
        dir_path:
            Path to a directory containing evidence files (searched recursively).
        """
        dir_path = Path(dir_path)
        result = ContractResult(passed=False)

        if not dir_path.exists() or not dir_path.is_dir():
            result.failures.append(f"Directory not found: {dir_path}")
            result.verdict = "BUNDLE_CONTRACT_FAILED"
            return result

        all_files = list(dir_path.rglob("*"))
        basenames = {f.name for f in all_files if f.is_file()}
        result.file_count = len(basenames)

        for category, patterns in REQUIRED_CATEGORIES.items():
            if any(p in basenames for p in patterns):
                result.categories_found.append(category)
            else:
                result.categories_missing.append(category)
                result.failures.append(
                    f"Missing category '{category}' — expected one of: {patterns}"
                )

        result.passed = not result.failures
        result.verdict = "BUNDLE_CONTRACT_PASSED" if result.passed else "BUNDLE_CONTRACT_FAILED"
        return result


def contract_definition() -> dict:
    """Return the bundle contract definition as a serialisable dict."""
    return {
        "contract_version": "1.0.0",
        "sprint": "sprint28+",
        "description": "Strict evidence contract for LowCode sprint bundles. Every category must be satisfied.",
        "required_categories": {
            cat: patterns for cat, patterns in REQUIRED_CATEGORIES.items()
        },
        "min_categories_required": MIN_CATEGORIES_REQUIRED,
        "secret_scanning_enabled": True,
        "secret_patterns": [p.pattern for p in SECRET_PATTERNS],
        "failure_verdict": "BUNDLE_CONTRACT_FAILED",
        "pass_verdict": "BUNDLE_CONTRACT_PASSED",
    }
