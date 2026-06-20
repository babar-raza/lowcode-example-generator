"""Quality scorer for generated C# examples (TC-SRHP-03).

Evaluates generated C# code against 5 criteria without requiring the external
example-reviewer. Results are written to the workspace manifest as quality_score.

Criteria
--------
1. SYMBOL_USAGE      — code references at least one Aspose API symbol (namespace check)
2. NO_TODO_STUBS     — code does not contain TODO or NotImplementedException
3. CONSOLE_OUTPUT    — code contains Console.Write* or meaningful output call
4. EXCEPTION_HANDLING — code contains a try/catch or using block
5. PATH_SAFETY       — code uses AppContext.BaseDirectory, not hardcoded absolute paths

Each criterion is PASS or FAIL. The quality_score is (passed_count / total_criteria).
A score < 0.6 (fewer than 3/5) is considered LOW.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Regex patterns for each criterion
_RE_ASPOSE_NS = re.compile(r"\bAspose\b", re.IGNORECASE)
_RE_TODO = re.compile(r"\bTODO\b|NotImplementedException", re.IGNORECASE)
_RE_CONSOLE = re.compile(r"\bConsole\.(Write|WriteLine|Error)\b")
_RE_TRY_CATCH = re.compile(r"\btry\s*\{|\busing\s*\(")
_RE_HARDCODED_PATH = re.compile(r'["\'](?:[A-Za-z]:\\\\|/home/|/root/|/Users/)[^"\']*["\']')
_RE_BASE_DIR = re.compile(r"AppContext\.BaseDirectory|Path\.GetDirectoryName|Directory\.GetCurrentDirectory")

TOTAL_CRITERIA = 5
PASSING_THRESHOLD = 0.6


@dataclass
class CriterionResult:
    """Result for a single scoring criterion."""

    name: str
    passed: bool
    detail: str = ""


@dataclass
class ExampleScoreResult:
    """Quality score for a single generated example."""

    example_id: str
    criteria: list[CriterionResult] = field(default_factory=list)
    quality_score: float = 0.0
    quality_label: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "quality_score": self.quality_score,
            "quality_label": self.quality_label,
            "criteria": [
                {"name": c.name, "passed": c.passed, "detail": c.detail}
                for c in self.criteria
            ],
        }


def score_example(example_id: str, code: str) -> ExampleScoreResult:
    """Score a single C# example against the 5 quality criteria.

    Args:
        example_id: Unique identifier for the example (e.g., slug or scenario_id).
        code: Full C# source code as a string.

    Returns:
        ExampleScoreResult with per-criterion pass/fail and overall quality_score.
    """
    criteria: list[CriterionResult] = []

    # Criterion 1: SYMBOL_USAGE — Aspose namespace referenced
    uses_aspose = bool(_RE_ASPOSE_NS.search(code))
    criteria.append(CriterionResult(
        name="SYMBOL_USAGE",
        passed=uses_aspose,
        detail="Aspose namespace found" if uses_aspose else "No Aspose namespace reference",
    ))

    # Criterion 2: NO_TODO_STUBS — no TODO or NotImplementedException
    has_stub = bool(_RE_TODO.search(code))
    criteria.append(CriterionResult(
        name="NO_TODO_STUBS",
        passed=not has_stub,
        detail="No stubs found" if not has_stub else "Contains TODO or NotImplementedException",
    ))

    # Criterion 3: CONSOLE_OUTPUT — has Console.Write* or similar
    has_output = bool(_RE_CONSOLE.search(code))
    criteria.append(CriterionResult(
        name="CONSOLE_OUTPUT",
        passed=has_output,
        detail="Console output found" if has_output else "No Console.Write* call found",
    ))

    # Criterion 4: EXCEPTION_HANDLING — has try/catch or using block
    has_handling = bool(_RE_TRY_CATCH.search(code))
    criteria.append(CriterionResult(
        name="EXCEPTION_HANDLING",
        passed=has_handling,
        detail="try/catch or using block found" if has_handling else "No try/catch or using block",
    ))

    # Criterion 5: PATH_SAFETY — uses AppContext.BaseDirectory, not hardcoded paths
    has_hardcoded = bool(_RE_HARDCODED_PATH.search(code))
    has_safe_path = bool(_RE_BASE_DIR.search(code))
    path_safe = has_safe_path and not has_hardcoded
    criteria.append(CriterionResult(
        name="PATH_SAFETY",
        passed=path_safe,
        detail=(
            "Uses AppContext.BaseDirectory" if path_safe
            else ("Hardcoded absolute path detected" if has_hardcoded else "No AppContext.BaseDirectory found")
        ),
    ))

    passed_count = sum(1 for c in criteria if c.passed)
    score = passed_count / TOTAL_CRITERIA

    if score >= 0.8:
        label = "HIGH"
    elif score >= PASSING_THRESHOLD:
        label = "MEDIUM"
    else:
        label = "LOW"

    return ExampleScoreResult(
        example_id=example_id,
        criteria=criteria,
        quality_score=round(score, 2),
        quality_label=label,
    )


def score_example_file(example_id: str, cs_path: Path) -> ExampleScoreResult:
    """Score a C# example from a file path."""
    if not cs_path.exists():
        result = ExampleScoreResult(example_id=example_id)
        result.quality_score = 0.0
        result.quality_label = "FILE_NOT_FOUND"
        return result
    code = cs_path.read_text(encoding="utf-8", errors="replace")
    return score_example(example_id, code)


def score_project_directory(example_id: str, project_dir: Path) -> ExampleScoreResult:
    """Score all .cs files in a project directory (combined code string)."""
    cs_files = sorted(project_dir.rglob("*.cs"))
    if not cs_files:
        result = ExampleScoreResult(example_id=example_id)
        result.quality_score = 0.0
        result.quality_label = "NO_CS_FILES"
        return result
    combined = "\n".join(
        f.read_text(encoding="utf-8", errors="replace") for f in cs_files
    )
    return score_example(example_id, combined)


def build_quality_manifest(scores: list[ExampleScoreResult]) -> dict[str, Any]:
    """Build a quality manifest dict suitable for writing to workspace."""
    passing = [s for s in scores if s.quality_score >= PASSING_THRESHOLD]
    return {
        "schema": "quality_manifest_v1",
        "total_examples": len(scores),
        "passing_examples": len(passing),
        "failing_examples": len(scores) - len(passing),
        "passing_threshold": PASSING_THRESHOLD,
        "average_quality_score": (
            round(sum(s.quality_score for s in scores) / len(scores), 3)
            if scores else 0.0
        ),
        "examples": [s.to_dict() for s in scores],
    }
