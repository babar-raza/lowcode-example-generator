"""README auditor for LowCode family example repositories.

Audits a rendered or existing README.md against the expected ReadmeContext to
detect stale versions, missing sections, missing/extra examples, and invalid content.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Required section headings that must appear in every README
REQUIRED_SECTIONS: list[str] = [
    "## Overview",
    "## Included Examples",
    "## Requirements",
    "## How to Run",
    "## Package Installation",
    "## Validation Status",
    "## Useful Links",
]

# Strings that indicate a central (non-family-specific) repo was referenced
_CENTRAL_REPO_PATTERNS: list[str] = [
    "aspose-plugins-examples-dotnet",
    "aspose/Aspose",
    "central repo",
    "combined repo",
]

# Patterns that signal catalog symbol noise — long symbol names that are not
# actual LowCode class names (e.g. full namespace-qualified method names)
_CATALOG_NOISE_PATTERNS: list[str] = [
    # Fully-qualified namespace patterns like Aspose.Cells.LowCode.HtmlConverter.Process
    r"Aspose\.\w+\.LowCode\.\w+\.\w+\(",
    # DocFX token noise: M:Namespace.Class.Method(params)
    r"M:[A-Z][A-Za-z\.]+\(",
    # Raw XML doc comment tokens
    r"<member name=",
    r"<see cref=",
]


@dataclass
class ReadmeAuditResult:
    """Result of auditing a README against expected context."""
    passed: bool
    missing_sections: list[str] = field(default_factory=list)
    stale_version: bool = False          # package_version not found in README
    stale_examples: bool = False         # number of example rows doesn't match
    missing_examples: list[str] = field(default_factory=list)
    extra_examples: list[str] = field(default_factory=list)
    central_repo_reference_found: bool = False
    blocked_scenario_reference_found: bool = False
    catalog_symbol_noise_found: bool = False
    # URL domain validation results (added for aspose.net link standardization)
    forbidden_aspose_com_links: list[str] = field(default_factory=list)
    platform_path_errors: list[str] = field(default_factory=list)
    wrong_blog_links: list[str] = field(default_factory=list)
    wrong_contact_links: list[str] = field(default_factory=list)
    missing_required_links: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    expected_version: str | None = None
    found_version: str | None = None
    expected_example_count: int = 0
    found_example_count: int = 0


def _extract_examples_section(content: str) -> str:
    """Extract the text between '## Included Examples' and the next '## ' heading."""
    match = re.search(r"## Included Examples\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def _count_example_rows(examples_section: str) -> int:
    """Count the number of data rows in the Included Examples markdown table."""
    count = 0
    for line in examples_section.splitlines():
        stripped = line.strip()
        # Data rows start with | but are not the header row (contains 'Example') or separator row
        if stripped.startswith("|") and not stripped.startswith("|---") and "Example" not in stripped:
            count += 1
    return count


def _find_example_names_in_table(examples_section: str) -> list[str]:
    """Extract example names from the backtick-quoted first column of the table."""
    names = []
    for line in examples_section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and not stripped.startswith("|---") and "Example" not in stripped:
            # First column: | `name` | ...
            m = re.search(r"\|\s*`([^`]+)`", stripped)
            if m:
                names.append(m.group(1))
    return names


def audit_readme(readme_content: str, context) -> ReadmeAuditResult:
    """Audit README content against the expected ReadmeContext.

    Args:
        readme_content: Full text of the rendered or existing README.md.
        context: ReadmeContext with the expected values (package version, examples, etc.).
            Also accepts a plain dict with equivalent keys for testing.

    Returns:
        ReadmeAuditResult with passed=True if all checks pass.
    """
    # Support dict context for testing convenience
    if isinstance(context, dict):
        package_version = context.get("package_version", "")
        examples = context.get("examples", [])
        family = context.get("family", "")
    else:
        package_version = getattr(context, "package_version", "")
        examples_raw = getattr(context, "examples", [])
        # ExampleEntry objects or dicts
        examples = [
            ex if isinstance(ex, dict) else {"name": ex.name}
            for ex in examples_raw
        ]
        family = getattr(context, "family", "")

    result = ReadmeAuditResult(
        passed=True,
        expected_version=package_version,
        expected_example_count=len(examples),
    )
    failures: list[str] = []

    # --- 1. Required sections ---
    for section in REQUIRED_SECTIONS:
        if section not in readme_content:
            result.missing_sections.append(section)
            failures.append(f"Missing section: {section!r}")

    # --- 2. Package version appears ---
    if package_version and package_version not in readme_content:
        result.stale_version = True
        failures.append(f"Package version '{package_version}' not found in README")
    else:
        result.found_version = package_version

    # --- 3. Example table row count ---
    examples_section = _extract_examples_section(readme_content)
    found_count = _count_example_rows(examples_section)
    result.found_example_count = found_count
    expected_count = len(examples)

    if found_count != expected_count:
        result.stale_examples = True
        failures.append(
            f"Example row count mismatch: expected {expected_count}, found {found_count}"
        )

    # --- 4. Each expected example name appears in the table ---
    table_names = _find_example_names_in_table(examples_section)
    for ex in examples:
        name = ex.get("name", "") if isinstance(ex, dict) else ex
        if name and name not in table_names:
            result.missing_examples.append(name)
            failures.append(f"Example '{name}' missing from README table")

    # Extra examples in table that are not in context
    context_names = {
        (ex.get("name", "") if isinstance(ex, dict) else ex)
        for ex in examples
    }
    for tname in table_names:
        if tname and tname not in context_names:
            result.extra_examples.append(tname)
            failures.append(f"Extra example '{tname}' in README not in context")

    # --- 5. Central repo reference check ---
    for pattern in _CENTRAL_REPO_PATTERNS:
        if pattern.lower() in readme_content.lower():
            result.central_repo_reference_found = True
            failures.append(f"Central repo reference found: '{pattern}'")
            break

    # --- 6. Catalog symbol noise check ---
    for pattern in _CATALOG_NOISE_PATTERNS:
        if re.search(pattern, readme_content):
            result.catalog_symbol_noise_found = True
            failures.append(f"Catalog symbol noise detected (pattern: {pattern!r})")
            break

    # --- 7. Blocked scenario reference check ---
    # Check that no scenario marked as "blocked" in the context appears in the README
    # (Only applicable if context provides a blocked list; otherwise skip)
    blocked: list[str] = []
    if isinstance(context, dict):
        blocked = context.get("blocked_scenarios", [])
    else:
        blocked = getattr(context, "blocked_scenarios", [])
    for scenario in blocked:
        if scenario and scenario in readme_content:
            result.blocked_scenario_reference_found = True
            failures.append(f"Blocked scenario '{scenario}' referenced in README")

    # --- Cross-family contamination check ---
    # If family is known, verify the opposite family's specific markers are absent
    if family == "cells":
        if "Aspose.Words" in readme_content or "aspose-words-net" in readme_content:
            result.warnings.append(
                "Words-specific content detected in Cells README"
            )
            failures.append("Words content found in Cells README")
    elif family == "words":
        if "Aspose.Cells" in readme_content or "aspose-cells-net" in readme_content:
            result.warnings.append(
                "Cells-specific content detected in Words README"
            )
            failures.append("Cells content found in Words README")

    # --- URL domain validation (aspose.net link policy) ---
    from plugin_examples.publisher.aspose_links import (
        find_forbidden_aspose_com_links,
        find_platform_path_errors,
        find_wrong_blog_links,
        find_wrong_contact_links,
        find_missing_required_links,
    )

    # Check 8: Forbidden aspose.com product/docs/ref/blog/forum/purchase/about links
    _forbidden = find_forbidden_aspose_com_links(readme_content)
    if _forbidden:
        result.forbidden_aspose_com_links = _forbidden
        failures.append(
            f"Forbidden aspose.com links found (must use aspose.net): {_forbidden}"
        )

    # Check 9: aspose.net URLs with /net platform suffix (wrong)
    _family_slug = family if family else ""
    if _family_slug:
        _path_errors = find_platform_path_errors(readme_content, _family_slug)
        if _path_errors:
            result.platform_path_errors = _path_errors
            failures.append(
                f"aspose.net URLs with incorrect /net platform suffix: {_path_errors}"
            )

    # Check 10: Wrong blog URL (aspose.com/category/ instead of aspose.net/categories/.../)
    _wrong_blog = find_wrong_blog_links(readme_content)
    if _wrong_blog:
        result.wrong_blog_links = _wrong_blog
        failures.append(
            f"Wrong blog URL pattern (use blog.aspose.net/categories/aspose.{{slug}}-plugin-family/): {_wrong_blog}"
        )

    # Check 11: Wrong contact URL (aspose.com/contact-us/ instead of aspose.net/contact/)
    _wrong_contact = find_wrong_contact_links(readme_content)
    if _wrong_contact:
        result.wrong_contact_links = _wrong_contact
        failures.append(
            f"Wrong contact URL (use about.aspose.net/contact/): {_wrong_contact}"
        )

    # Check 12: Missing required KB link
    _missing = find_missing_required_links(readme_content, _family_slug or None)
    if _missing:
        result.missing_required_links = _missing
        failures.append(f"Missing required links: {_missing}")

    if failures:
        result.passed = False
        result.warnings.extend(failures)
        logger.warning("README audit FAILED for %s: %s", family or "unknown", "; ".join(failures))
    else:
        logger.info("README audit PASSED for %s", family or "unknown")

    return result


def audit_readme_file(readme_path: Path, context) -> ReadmeAuditResult:
    """Read a README.md file and audit it.

    Args:
        readme_path: Path to the README.md file.
        context: ReadmeContext or dict.

    Returns:
        ReadmeAuditResult.
    """
    readme_path = Path(readme_path)
    if not readme_path.exists():
        result = ReadmeAuditResult(passed=False)
        result.warnings.append(f"README.md does not exist: {readme_path}")
        return result
    content = readme_path.read_text(encoding="utf-8")
    return audit_readme(content, context)
