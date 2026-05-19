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
    wrong_format_claims: list[str] = field(default_factory=list)
    missing_source_snippets: list[str] = field(default_factory=list)
    xlsx_cross_family_violation: bool = False
    warnings: list[str] = field(default_factory=list)
    expected_version: str | None = None
    found_version: str | None = None
    expected_example_count: int = 0
    found_example_count: int = 0
    # Method-level symbol check: examples whose api_class lacks a method qualifier (advisory)
    unqualified_api_classes: list[str] = field(default_factory=list)
    # Semantic checks (V8 format lifecycle, advisory only)
    same_format_converter_warnings: list[str] = field(default_factory=list)
    splitter_cardinality_warnings: list[str] = field(default_factory=list)
    merger_cardinality_warnings: list[str] = field(default_factory=list)
    extractor_output_warnings: list[str] = field(default_factory=list)


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


def _find_api_class_for_example(examples_section: str, example_name: str) -> str | None:
    """Return the api_class column value for a specific example row.

    Scans the table for the row whose first column contains ``example_name``
    and returns the backtick-quoted second column (the Demonstrated API field).
    Returns None if the row or column is not found.
    """
    for line in examples_section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and f"`{example_name}`" in stripped:
            cols = stripped.split("|")
            # cols: ['', ' `name` ', ' `api_class` ', ...]
            if len(cols) >= 3:
                m = re.search(r"`([^`]+)`", cols[2])
                if m:
                    return m.group(1)
    return None


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
    # Strip fenced code blocks and <details> sections before checking —
    # source code snippets legitimately contain fully-qualified namespace calls.
    _prose_content = re.sub(r"```[\s\S]*?```", "", readme_content)
    _prose_content = re.sub(r"<details>[\s\S]*?</details>", "", _prose_content)
    for pattern in _CATALOG_NOISE_PATTERNS:
        if re.search(pattern, _prose_content):
            result.catalog_symbol_noise_found = True
            failures.append(f"Catalog symbol noise detected (pattern: {pattern!r})")
            break

    # --- 7. Method-qualifier check (advisory, non-fatal) ---
    # Warn when any example's api_class in the table lacks a dot separator —
    # this indicates the directory-name inference fallback was used instead of
    # the manifest-backed method symbol (e.g. "HtmlConverter" vs "HtmlConverter.Process").
    for ex in examples:
        name = ex.get("name", "") if isinstance(ex, dict) else ex
        if not name:
            continue
        api_cls = _find_api_class_for_example(examples_section, name)
        if api_cls is not None and "." not in api_cls:
            result.unqualified_api_classes.append(name)
            result.warnings.append(
                f"Example '{name}' api_class '{api_cls}' lacks method qualifier "
                "(expected format: 'ClassName.MethodName', e.g. 'HtmlConverter.Process'). "
                "Check that example.manifest.json is present and package_path was passed to build_readme_context()."
            )

    # --- 8. Blocked scenario reference check ---
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

    # --- 13. Format-claim validation (table columns vs context) ---
    for ex in examples:
        name = ex.get("name", "") if isinstance(ex, dict) else ex
        if not name:
            continue
        expected_input = ex.get("input_format", "") if isinstance(ex, dict) else ""
        expected_output = ex.get("output_format", "") if isinstance(ex, dict) else ""
        if not expected_input and not expected_output:
            continue
        # Find the row in the table for this example
        for line in examples_section.splitlines():
            stripped = line.strip()
            if stripped.startswith("|") and f"`{name}`" in stripped:
                cols = stripped.split("|")
                if len(cols) >= 5:
                    table_input = cols[3].strip().strip("`").strip()
                    table_output = cols[4].strip().strip("`").strip()
                    if expected_input and table_input != expected_input:
                        result.wrong_format_claims.append(
                            f"{name}: input expected '{expected_input}', found '{table_input}'"
                        )
                        failures.append(
                            f"Format mismatch for '{name}': input expected '{expected_input}', found '{table_input}'"
                        )
                    if expected_output and table_output != expected_output:
                        result.wrong_format_claims.append(
                            f"{name}: output expected '{expected_output}', found '{table_output}'"
                        )
                        failures.append(
                            f"Format mismatch for '{name}': output expected '{expected_output}', found '{table_output}'"
                        )
                break

    # --- 14. Snippet presence check ---
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        name = ex.get("name", "")
        snippet = ex.get("source_snippet", "")
        if snippet and name:
            # Check that some distinctive content from the snippet appears in the README
            # Use the first non-empty non-comment line from the snippet
            for sline in snippet.splitlines():
                sline_stripped = sline.strip()
                if sline_stripped and not sline_stripped.startswith("//") and len(sline_stripped) > 15:
                    if sline_stripped not in readme_content:
                        result.missing_source_snippets.append(name)
                        failures.append(f"Source snippet for '{name}' not found in README")
                    break

    # --- 15. XLSX cross-family guard ---
    if family and family != "cells":
        # Check that xlsx does not appear as INPUT format in the examples table.
        # Output xlsx is allowed for converters that produce Excel output (e.g. PDF xls-converter).
        for line in examples_section.splitlines():
            stripped = line.strip()
            if stripped.startswith("|") and not stripped.startswith("|---") and "Example" not in stripped:
                cols = stripped.split("|")
                if len(cols) >= 5:
                    table_input = cols[3].strip().strip("`").strip().lower()
                    if "xlsx" in table_input:
                        result.xlsx_cross_family_violation = True
                        failures.append(
                            f"XLSX input format found in {family} README table (xlsx input is cells-specific)"
                        )
                        break

    # --- 16. Same-format converter warning (advisory, non-fatal) ---
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        op_kind = ex.get("operation_kind", "")
        in_fmt = ex.get("input_format", "")
        out_fmt = ex.get("output_format", "")
        name = ex.get("name", "")
        if op_kind == "converter" and in_fmt and out_fmt and in_fmt == out_fmt:
            result.same_format_converter_warnings.append(
                f"{name}: converter with same input/output format '{in_fmt}'"
            )

    # --- 17. Splitter cardinality warning (advisory, non-fatal) ---
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        op_kind = ex.get("operation_kind", "")
        name = ex.get("name", "")
        out_display = ex.get("output_format_display", "")
        if op_kind == "splitter" and out_display and "1" not in out_display and "N" not in out_display.upper():
            result.splitter_cardinality_warnings.append(
                f"{name}: splitter output display '{out_display}' missing 1->N indicator"
            )

    # --- 18. Merger cardinality warning (advisory, non-fatal) ---
    _MERGER_INDICATORS = re.compile(r"\d+\s*[×x]|[Nn]\s*[×x]|×", re.IGNORECASE)
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        op_kind = ex.get("operation_kind", "")
        name = ex.get("name", "")
        in_display = ex.get("input_format_display", "")
        if op_kind == "merger" and in_display and not _MERGER_INDICATORS.search(in_display):
            result.merger_cardinality_warnings.append(
                f"{name}: merger input display '{in_display}' missing N× indicator"
            )

    # --- 19. Extractor output kind validation (advisory, non-fatal) ---
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        op_kind = ex.get("operation_kind", "")
        name = ex.get("name", "")
        out_display = ex.get("output_format_display", "")
        if op_kind in ("extractor", "text_extractor") and out_display:
            if "stdout" not in out_display.lower() and "text" not in out_display.lower():
                result.extractor_output_warnings.append(
                    f"{name}: extractor output display '{out_display}' missing stdout/text indicator"
                )
        elif op_kind == "image_extractor" and out_display:
            if not re.search(r"\bN\b|\d+\s+files?|\bfiles?\b", out_display, re.IGNORECASE):
                result.extractor_output_warnings.append(
                    f"{name}: image extractor output display '{out_display}' missing N-files indicator"
                )
        elif op_kind == "directory_output" and out_display:
            if "dir" not in out_display.lower():
                result.extractor_output_warnings.append(
                    f"{name}: directory output display '{out_display}' missing directory indicator"
                )

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


# ---------------------------------------------------------------------------
# Staleness detection for cumulative README inventory
# ---------------------------------------------------------------------------

@dataclass
class ReadmeStalenessResult:
    """Result of comparing README example table against expected inventory."""
    is_stale: bool
    missing_from_readme: list[str] = field(default_factory=list)
    extra_in_readme: list[str] = field(default_factory=list)
    inventory_count: int = 0
    readme_count: int = 0
    pending_not_in_branch: list[str] = field(default_factory=list)


def audit_readme_staleness(
    readme_content: str,
    expected_examples: list[str],
    pending_examples: list[str] | None = None,
) -> ReadmeStalenessResult:
    """Compare README example table against the expected inventory.

    Args:
        readme_content: Full text of the README.md.
        expected_examples: Names of examples that MUST be in the README.
        pending_examples: Names of examples that are package-ready but not
            in the target branch. These are NOT failures — they are classified
            as ``pending_not_in_branch``.

    Returns:
        ReadmeStalenessResult with is_stale=True if any expected examples
        are missing from the README, or if the README contains extra examples
        not in the expected set.
    """
    section = _extract_examples_section(readme_content)
    readme_names = set(_find_example_names_in_table(section))
    expected_set = set(expected_examples)
    pending_set = set(pending_examples or [])

    missing = sorted(expected_set - readme_names)
    extra = sorted(readme_names - expected_set - pending_set)
    pending_classified = sorted(pending_set - readme_names)

    return ReadmeStalenessResult(
        is_stale=bool(missing) or bool(extra),
        missing_from_readme=missing,
        extra_in_readme=extra,
        inventory_count=len(expected_set),
        readme_count=len(readme_names),
        pending_not_in_branch=pending_classified,
    )
