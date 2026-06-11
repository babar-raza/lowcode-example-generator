"""Engineering hygiene validators — EHV-01..05.

Detects recurring code quality regressions that lower the Recruitize Engineering
Practices (P) score. These validators run as part of the doctor health check and
can be invoked standalone for CI pre-commit gating.

Validators:
    EHV-01: Silent bare except handlers (except Exception: pass / bare except:)
    EHV-02: Bare except without type (except:) — catches BaseException silently
    EHV-03: Integration test count below minimum threshold
    EHV-04: Bandit security config present in pyproject.toml
    EHV-05: CODEOWNERS present at project root
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EHVResult:
    """Result of a single engineering hygiene validator."""

    validator_id: str
    passed: bool
    message: str
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "validator_id": self.validator_id,
            "passed": self.passed,
            "message": self.message,
            "detail": self.detail,
        }


# ---------------------------------------------------------------------------
# EHV-01: Detect silent bare except handlers (except Exception: pass)
# ---------------------------------------------------------------------------


def _find_silent_bare_excepts(source_dir: Path) -> list[str]:
    """Find `except Exception: pass` / `except Exception as e: pass` patterns via AST."""
    violations: list[str] = []
    for py_file in source_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            # Check if body is a single Pass statement
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                # EHV-01 fires only when exception type is `Exception` or subclass
                if node.type is not None:
                    type_name = ""
                    if isinstance(node.type, ast.Name):
                        type_name = node.type.id
                    elif isinstance(node.type, ast.Attribute):
                        type_name = node.type.attr
                    if type_name == "Exception":
                        violations.append(f"{py_file}:{node.lineno}: except Exception: pass")
    return violations


def check_silent_bare_excepts(repo_root: Path | None = None) -> EHVResult:
    """EHV-01: Detect `except Exception: pass` patterns that silently swallow errors."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    src_dir = repo_root / "src"
    if not src_dir.is_dir():
        return EHVResult(
            "EHV-01",
            passed=True,
            message="EHV-01: SKIP — src/ directory not found",
        )

    violations = _find_silent_bare_excepts(src_dir)
    if violations:
        return EHVResult(
            "EHV-01",
            passed=False,
            message=f"EHV-01: FAIL — {len(violations)} silent bare except(Exception) handler(s) found",
            detail="; ".join(violations[:5]) + (" ..." if len(violations) > 5 else ""),
        )
    return EHVResult(
        "EHV-01",
        passed=True,
        message="EHV-01: PASS — No silent bare except(Exception) handlers in src/",
    )


# ---------------------------------------------------------------------------
# EHV-02: Detect bare except: (catches BaseException silently)
# ---------------------------------------------------------------------------


def _find_bare_excepts(source_dir: Path) -> list[str]:
    """Find `except:` without any type (catches BaseException silently)."""
    violations: list[str] = []
    for py_file in source_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                violations.append(f"{py_file}:{node.lineno}: bare except:")
    return violations


def check_bare_excepts(repo_root: Path | None = None) -> EHVResult:
    """EHV-02: Detect bare `except:` (no exception type) which catches BaseException."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    src_dir = repo_root / "src"
    if not src_dir.is_dir():
        return EHVResult(
            "EHV-02",
            passed=True,
            message="EHV-02: SKIP — src/ directory not found",
        )

    violations = _find_bare_excepts(src_dir)
    if violations:
        return EHVResult(
            "EHV-02",
            passed=False,
            message=f"EHV-02: FAIL — {len(violations)} bare except: handler(s) found (catches BaseException)",
            detail="; ".join(violations[:5]) + (" ..." if len(violations) > 5 else ""),
        )
    return EHVResult(
        "EHV-02",
        passed=True,
        message="EHV-02: PASS — No bare except: handlers in src/",
    )


# ---------------------------------------------------------------------------
# EHV-03: Integration test count >= minimum
# ---------------------------------------------------------------------------

_MIN_INTEGRATION_TESTS = 5


def _count_integration_test_functions(tests_dir: Path) -> int:
    """Count test functions in tests/integration/ via AST."""
    integration_dir = tests_dir / "integration"
    if not integration_dir.is_dir():
        return 0
    count = 0
    for py_file in integration_dir.glob("test_*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    count += 1
    return count


def check_integration_test_count(repo_root: Path | None = None) -> EHVResult:
    """EHV-03: Assert integration test count >= minimum threshold."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return EHVResult(
            "EHV-03",
            passed=False,
            message="EHV-03: FAIL — tests/ directory not found",
        )

    count = _count_integration_test_functions(tests_dir)
    if count < _MIN_INTEGRATION_TESTS:
        return EHVResult(
            "EHV-03",
            passed=False,
            message=(
                f"EHV-03: FAIL — Only {count} integration test function(s) found "
                f"(minimum: {_MIN_INTEGRATION_TESTS})"
            ),
        )
    return EHVResult(
        "EHV-03",
        passed=True,
        message=f"EHV-03: PASS — {count} integration test functions found (minimum: {_MIN_INTEGRATION_TESTS})",
    )


# ---------------------------------------------------------------------------
# EHV-04: Bandit security config present in pyproject.toml
# ---------------------------------------------------------------------------


def check_bandit_config(repo_root: Path | None = None) -> EHVResult:
    """EHV-04: Assert [tool.bandit] section exists in pyproject.toml."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return EHVResult(
            "EHV-04",
            passed=False,
            message="EHV-04: FAIL — pyproject.toml not found",
        )

    content = pyproject.read_text(encoding="utf-8")
    if "[tool.bandit]" in content:
        return EHVResult(
            "EHV-04",
            passed=True,
            message="EHV-04: PASS — [tool.bandit] section present in pyproject.toml",
        )
    return EHVResult(
        "EHV-04",
        passed=False,
        message="EHV-04: FAIL — [tool.bandit] section missing from pyproject.toml (add SAST config)",
    )


# ---------------------------------------------------------------------------
# EHV-05: CODEOWNERS present at project root
# ---------------------------------------------------------------------------


def check_codeowners(repo_root: Path | None = None) -> EHVResult:
    """EHV-05: Assert CODEOWNERS file exists at the project root."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    codeowners = repo_root / "CODEOWNERS"
    if codeowners.exists() and codeowners.stat().st_size > 0:
        first_line = codeowners.read_text(encoding="utf-8").strip().splitlines()[0] if codeowners.stat().st_size else ""
        return EHVResult(
            "EHV-05",
            passed=True,
            message=f"EHV-05: PASS — CODEOWNERS present ({codeowners.stat().st_size} bytes)",
            detail=first_line[:80],
        )
    return EHVResult(
        "EHV-05",
        passed=False,
        message="EHV-05: FAIL — CODEOWNERS file missing or empty at project root",
    )


# ---------------------------------------------------------------------------
# Run all EHV validators
# ---------------------------------------------------------------------------


def run_all_ehv_validators(repo_root: Path | None = None) -> list[EHVResult]:
    """Run all engineering hygiene validators and return results."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    return [
        check_silent_bare_excepts(repo_root),
        check_bare_excepts(repo_root),
        check_integration_test_count(repo_root),
        check_bandit_config(repo_root),
        check_codeowners(repo_root),
    ]
