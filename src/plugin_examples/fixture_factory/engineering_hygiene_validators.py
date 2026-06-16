"""Engineering hygiene validators — EHV-01..11.

Detects recurring code quality regressions that lower the Recruitize Engineering
Practices (P) and Readiness (R) scores. These validators run as part of the
doctor health check and can be invoked standalone for CI pre-commit gating.

Validators:
    EHV-01: Silent bare except handlers (except Exception: pass / bare except:)
    EHV-02: Bare except without type (except:) — catches BaseException silently
    EHV-03: Integration test count below minimum threshold
    EHV-04: Bandit security config present in pyproject.toml
    EHV-05: CODEOWNERS present at project root
    EHV-06: pyproject.toml version matches CHANGELOG.md top entry
    EHV-07: pyproject.toml version follows semver pattern
    EHV-08: Dependency licenses are in the approved allowlist
    EHV-09: SECURITY.md presence
    EHV-10: CONTRIBUTING.md presence
    EHV-11: Broad except Exception: handler count ratchet
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
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass) and node.type is not None:
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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
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
# EHV-06: pyproject.toml version matches CHANGELOG.md top entry
# ---------------------------------------------------------------------------

_VERSION_RE = re.compile(r'version\s*=\s*"([^"]+)"')
_CHANGELOG_VERSION_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\]", re.MULTILINE)


def check_version_changelog_sync(repo_root: Path | None = None) -> EHVResult:
    """EHV-06: Assert pyproject.toml version matches first CHANGELOG.md version heading."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    pyproject = repo_root / "pyproject.toml"
    changelog = repo_root / "CHANGELOG.md"

    if not pyproject.exists():
        return EHVResult("EHV-06", passed=False, message="EHV-06: FAIL — pyproject.toml not found")
    if not changelog.exists():
        return EHVResult("EHV-06", passed=False, message="EHV-06: FAIL — CHANGELOG.md not found")

    pyproject_text = pyproject.read_text(encoding="utf-8")
    m = _VERSION_RE.search(pyproject_text)
    if not m:
        return EHVResult("EHV-06", passed=False, message="EHV-06: FAIL — no version found in pyproject.toml")
    pyproject_version = m.group(1)

    changelog_text = changelog.read_text(encoding="utf-8")
    cm = _CHANGELOG_VERSION_RE.search(changelog_text)
    if not cm:
        return EHVResult("EHV-06", passed=False, message="EHV-06: FAIL — no version heading found in CHANGELOG.md")
    changelog_version = cm.group(1)

    if pyproject_version != changelog_version:
        return EHVResult(
            "EHV-06",
            passed=False,
            message=f"EHV-06: FAIL — version mismatch: pyproject.toml={pyproject_version}, CHANGELOG.md={changelog_version}",
        )
    return EHVResult(
        "EHV-06",
        passed=True,
        message=f"EHV-06: PASS — version {pyproject_version} matches in pyproject.toml and CHANGELOG.md",
    )


# ---------------------------------------------------------------------------
# EHV-07: pyproject.toml version follows semver pattern
# ---------------------------------------------------------------------------

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def check_semver_version(repo_root: Path | None = None) -> EHVResult:
    """EHV-07: Assert pyproject.toml version follows semver (MAJOR.MINOR.PATCH)."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return EHVResult("EHV-07", passed=False, message="EHV-07: FAIL — pyproject.toml not found")

    content = pyproject.read_text(encoding="utf-8")
    m = _VERSION_RE.search(content)
    if not m:
        return EHVResult("EHV-07", passed=False, message="EHV-07: FAIL — no version found in pyproject.toml")

    version = m.group(1)
    if _SEMVER_RE.match(version):
        return EHVResult("EHV-07", passed=True, message=f"EHV-07: PASS — version '{version}' follows semver")
    return EHVResult("EHV-07", passed=False, message=f"EHV-07: FAIL — version '{version}' does not follow semver")


# ---------------------------------------------------------------------------
# EHV-08: Dependency licenses in approved allowlist
# ---------------------------------------------------------------------------

_ALLOWED_LICENSE_KEYWORDS = frozenset({
    "mit", "bsd", "apache", "psf", "python software foundation",
    "isc", "lgpl", "mpl", "public domain", "unlicense", "cc0",
})


def check_dependency_licenses(repo_root: Path | None = None) -> EHVResult:
    """EHV-08: Check installed dependency licenses against an approved allowlist."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    try:
        from importlib.metadata import distributions
    except ImportError:
        return EHVResult("EHV-08", passed=True, message="EHV-08: SKIP — importlib.metadata not available")

    # Read declared dependencies from pyproject.toml
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return EHVResult("EHV-08", passed=False, message="EHV-08: FAIL — pyproject.toml not found")

    content = pyproject.read_text(encoding="utf-8")
    # Extract dependency names (simple regex, good enough for top-level deps)
    dep_section = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not dep_section:
        return EHVResult("EHV-08", passed=True, message="EHV-08: SKIP — no dependencies section found")

    dep_names: set[str] = set()
    for line in dep_section.group(1).splitlines():
        line = line.strip().strip('"').strip("'").strip(",")
        if line:
            # Extract package name (before any version specifier)
            name = re.split(r"[><=!~\[]", line)[0].strip().lower().replace("-", "_")
            if name:
                dep_names.add(name)

    if not dep_names:
        return EHVResult("EHV-08", passed=True, message="EHV-08: SKIP — no dependencies declared")

    violations: list[str] = []
    for dist in distributions():
        dist_name = (dist.metadata.get("Name") or "").lower().replace("-", "_")
        if dist_name not in dep_names:
            continue
        license_str = dist.metadata.get("License") or ""
        license_expr = dist.metadata.get("License-Expression") or ""
        classifiers = dist.metadata.get_all("Classifier") or []
        license_classifiers = [c for c in classifiers if c.startswith("License")]

        # Build combined license text for matching (PEP 639 License-Expression + legacy License + classifiers)
        combined = (license_str + " " + license_expr + " " + " ".join(license_classifiers)).lower()
        if not any(kw in combined for kw in _ALLOWED_LICENSE_KEYWORDS):
            violations.append(f"{dist_name}: '{license_expr or license_str or 'UNKNOWN'}'")

    if violations:
        return EHVResult(
            "EHV-08",
            passed=False,
            message=f"EHV-08: FAIL — {len(violations)} dependency license(s) not in allowlist",
            detail="; ".join(violations[:5]),
        )
    return EHVResult(
        "EHV-08",
        passed=True,
        message=f"EHV-08: PASS — all {len(dep_names)} declared dependencies have approved licenses",
    )


# ---------------------------------------------------------------------------
# EHV-09: SECURITY.md presence (policy-as-code)
# ---------------------------------------------------------------------------


def check_security_policy(repo_root: Path | None = None) -> EHVResult:
    """EHV-09: Assert SECURITY.md exists with vulnerability disclosure process."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    security_md = repo_root / "SECURITY.md"
    if not security_md.exists():
        return EHVResult(
            "EHV-09",
            passed=False,
            message="EHV-09: FAIL — SECURITY.md not found at project root",
        )
    content = security_md.read_text(encoding="utf-8")
    if len(content) < 100:
        return EHVResult(
            "EHV-09",
            passed=False,
            message="EHV-09: FAIL — SECURITY.md is too short (< 100 chars)",
        )
    has_disclosure = "disclosure" in content.lower() or "report" in content.lower()
    if not has_disclosure:
        return EHVResult(
            "EHV-09",
            passed=False,
            message="EHV-09: FAIL — SECURITY.md lacks vulnerability disclosure section",
        )
    return EHVResult(
        "EHV-09",
        passed=True,
        message=f"EHV-09: PASS — SECURITY.md present ({security_md.stat().st_size} bytes)",
    )


# ---------------------------------------------------------------------------
# EHV-10: CONTRIBUTING.md presence (policy-as-code)
# ---------------------------------------------------------------------------


def check_contributing_guide(repo_root: Path | None = None) -> EHVResult:
    """EHV-10: Assert CONTRIBUTING.md exists at the project root."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    contributing = repo_root / "CONTRIBUTING.md"
    if not contributing.exists():
        return EHVResult(
            "EHV-10",
            passed=False,
            message="EHV-10: FAIL — CONTRIBUTING.md not found at project root",
        )
    content = contributing.read_text(encoding="utf-8")
    if len(content) < 200:
        return EHVResult(
            "EHV-10",
            passed=False,
            message="EHV-10: FAIL — CONTRIBUTING.md is too short (< 200 chars)",
        )
    return EHVResult(
        "EHV-10",
        passed=True,
        message=f"EHV-10: PASS — CONTRIBUTING.md present ({contributing.stat().st_size} bytes)",
    )


# ---------------------------------------------------------------------------
# EHV-11: Broad except Exception: handler count ratchet
# ---------------------------------------------------------------------------

_BROAD_EXCEPT_THRESHOLD = 160  # Baseline: 153 as of 2026-06-16. Ratchet down over time.


def _count_broad_except_handlers(source_dir: Path) -> int:
    """Count all `except Exception:` handlers (not just silent pass ones)."""
    count = 0
    for py_file in source_dir.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler) or node.type is None:
                continue
            type_name = ""
            if isinstance(node.type, ast.Name):
                type_name = node.type.id
            elif isinstance(node.type, ast.Attribute):
                type_name = node.type.attr
            if type_name == "Exception":
                count += 1
    return count


def check_broad_exception_handlers(repo_root: Path | None = None) -> EHVResult:
    """EHV-11: Track broad `except Exception:` handler count against ratchet baseline."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    src_dir = repo_root / "src"
    if not src_dir.is_dir():
        return EHVResult("EHV-11", passed=True, message="EHV-11: SKIP — src/ directory not found")

    count = _count_broad_except_handlers(src_dir)
    if count > _BROAD_EXCEPT_THRESHOLD:
        return EHVResult(
            "EHV-11",
            passed=False,
            message=(
                f"EHV-11: FAIL — {count} broad except Exception: handlers "
                f"exceed ratchet threshold ({_BROAD_EXCEPT_THRESHOLD})"
            ),
            detail=f"Reduce broad handlers to stay below {_BROAD_EXCEPT_THRESHOLD}",
        )
    return EHVResult(
        "EHV-11",
        passed=True,
        message=(
            f"EHV-11: PASS — {count} broad except Exception: handlers "
            f"(ratchet threshold: {_BROAD_EXCEPT_THRESHOLD})"
        ),
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
        check_version_changelog_sync(repo_root),
        check_semver_version(repo_root),
        check_dependency_licenses(repo_root),
        check_security_policy(repo_root),
        check_contributing_guide(repo_root),
        check_broad_exception_handlers(repo_root),
    ]
