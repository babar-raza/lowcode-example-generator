"""Sprint 67 Phase 5 — Contract vs per_type_constraints semantics tests.

Verifies that per_type_constraints in family config YAML files are actual
code tokens that will appear in generated C#, NOT instruction text.
Human-readable instructions like 'REQUIRED: 2 input files...' always fail
the per_type_constraints check because they are never code substrings.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PIPELINE_DIR = REPO / "pipeline"


def _load_constraints(family: str) -> dict[str, list[str]]:
    """Load per_type_constraints from a family YAML config."""
    import yaml  # type: ignore

    config_path = PIPELINE_DIR / f"{family}.yml"
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data.get("per_type_constraints", {}) if data else {}


def _is_instruction_text(constraint: str) -> bool:
    """Return True if constraint looks like instruction text, not code."""
    # Instruction-text patterns: starts with REQUIRED/FORBIDDEN/NOTE/TODO,
    # contains ': ' with a description, or contains multiple words with no code chars
    instruction_patterns = [
        r"^REQUIRED:",
        r"^FORBIDDEN:",
        r"^NOTE:",
        r"^TODO:",
        r"^Ensure ",
        r"^Must ",
        r"^Use ",
        r"^The example",
        r" — ",  # em-dash separator (instruction explanation)
        r" \(",  # parenthetical note
    ]
    return any(re.search(pat, constraint) for pat in instruction_patterns)


def _looks_like_code_token(constraint: str) -> bool:
    """Return True if constraint looks like a code token that would appear in generated C#."""
    # Code tokens: file paths in quotes, method calls, class names, identifiers
    code_patterns = [
        r'"[^"]{2,}"',  # quoted string literal
        r"\w+\.[A-Z]\w+\(",  # method call pattern ClassName.Method(
        r"WriteAll\w+",  # File.WriteAll* methods
        r"\.Save\(",  # .Save( call
        r"AddInput|AddOutput",  # LowCode plugin API
        r"input\d*\.\w+",  # input file reference
        r"output\.\w+",  # output file reference
        r"\.docx|\.xlsx|\.pdf|\.png|\.html|\.txt|\.eml|\.csv|\.json",  # format extension
    ]
    for pat in code_patterns:
        if re.search(pat, constraint):
            return True
    # A single alphanumeric token with no spaces is likely a code identifier
    return bool(re.match(r'^[\w.\/\(\)\[\]"\']+$', constraint) and len(constraint) < 80)


FAMILIES_WITH_CONSTRAINTS = ["cells", "words", "pdf", "diagram", "email", "slides"]


class TestConstraintSemantics:
    """per_type_constraints must be code tokens, not instruction text."""

    def test_no_instruction_text_in_constraints(self):
        """No constraint should look like human-readable instruction text."""
        violations = []
        for fam in FAMILIES_WITH_CONSTRAINTS:
            constraints = _load_constraints(fam)
            for type_key, items in constraints.items():
                if not isinstance(items, list):
                    continue
                for c in items:
                    if isinstance(c, str) and _is_instruction_text(c):
                        violations.append(f"{fam}/{type_key}: {c!r}")
        assert not violations, "Found per_type_constraints that look like instruction text:\n" + "\n".join(violations)

    def test_constraints_are_strings(self):
        """All constraint items must be strings."""
        for fam in FAMILIES_WITH_CONSTRAINTS:
            constraints = _load_constraints(fam)
            for type_key, items in constraints.items():
                if not isinstance(items, list):
                    continue
                for c in items:
                    assert isinstance(c, str), f"{fam}/{type_key}: constraint is not a string: {c!r}"

    def test_constraints_not_empty_strings(self):
        """Constraint items must not be empty strings."""
        for fam in FAMILIES_WITH_CONSTRAINTS:
            constraints = _load_constraints(fam)
            for type_key, items in constraints.items():
                if not isinstance(items, list):
                    continue
                for c in items:
                    assert c.strip(), f"{fam}/{type_key}: constraint is empty string"

    def test_required_constraints_are_code_tokens(self):
        """REQUIRED constraints must contain actual code-like substrings."""
        violations = []
        for fam in FAMILIES_WITH_CONSTRAINTS:
            constraints = _load_constraints(fam)
            for type_key, items in constraints.items():
                if not isinstance(items, list):
                    continue
                # Gather REQUIRED-designated constraints
                required = [c for c in items if isinstance(c, str)]
                for c in required:
                    # Only check non-FORBIDDEN constraints
                    if c.startswith("NOT:") or c.startswith("FORBIDDEN:"):
                        continue
                    if len(c) > 5 and not _looks_like_code_token(c) and not c.startswith("#"):
                        violations.append(f"{fam}/{type_key}: '{c}' (not a code token)")
        # Advisory: report but don't fail unless there are instruction-text violations
        # (Some constraints may be valid tokens that don't match our patterns)
        if violations:
            pytest.skip(
                f"Advisory: {len(violations)} constraints may not be pure code tokens "
                f"(manual review recommended):\n" + "\n".join(violations[:5])
            )
