"""Tests for README staleness detection (audit_readme_staleness)."""

import pytest

from plugin_examples.publisher.readme_auditor import (
    audit_readme_staleness,
    ReadmeStalenessResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_readme_with_examples(example_names: list[str]) -> str:
    """Build a minimal README with an Included Examples table."""
    rows = "\n".join(f"| `{name}` | `SomeApi.Process` | `xlsx` | `pdf` | `dotnet run` |" for name in example_names)
    return (
        "# Test README\n\n"
        "Some intro.\n\n"
        "## Included Examples\n\n"
        "| Example | Demonstrated API | Input | Output | Run |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{rows}\n\n"
        "## How to Run\n\nInstructions here.\n"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestReadmeStaleness:
    def test_all_present_not_stale(self):
        content = _build_readme_with_examples(["converter", "merger", "splitter"])
        result = audit_readme_staleness(content, ["converter", "merger", "splitter"])
        assert not result.is_stale
        assert result.missing_from_readme == []
        assert result.extra_in_readme == []
        assert result.inventory_count == 3
        assert result.readme_count == 3

    def test_missing_examples_is_stale(self):
        content = _build_readme_with_examples(["converter"])
        result = audit_readme_staleness(content, ["converter", "merger", "splitter"])
        assert result.is_stale
        assert "merger" in result.missing_from_readme
        assert "splitter" in result.missing_from_readme
        assert result.inventory_count == 3
        assert result.readme_count == 1

    def test_extra_examples_is_stale(self):
        content = _build_readme_with_examples(["converter", "merger", "unexpected"])
        result = audit_readme_staleness(content, ["converter", "merger"])
        assert result.is_stale
        assert result.extra_in_readme == ["unexpected"]

    def test_pending_examples_not_failure(self):
        content = _build_readme_with_examples(["converter", "merger"])
        result = audit_readme_staleness(
            content,
            expected_examples=["converter", "merger"],
            pending_examples=["splitter", "optimizer"],
        )
        assert not result.is_stale
        assert result.missing_from_readme == []
        assert result.extra_in_readme == []
        assert sorted(result.pending_not_in_branch) == ["optimizer", "splitter"]

    def test_empty_readme_is_stale_if_expected(self):
        content = "# Empty README\n\nNo examples here.\n"
        result = audit_readme_staleness(content, ["converter"])
        assert result.is_stale
        assert result.missing_from_readme == ["converter"]
        assert result.readme_count == 0

    def test_empty_expected_not_stale(self):
        content = "# Empty README\n\nNo examples.\n"
        result = audit_readme_staleness(content, [])
        assert not result.is_stale

    def test_exact_match_order_independent(self):
        content = _build_readme_with_examples(["splitter", "converter", "merger"])
        result = audit_readme_staleness(content, ["merger", "converter", "splitter"])
        assert not result.is_stale

    def test_pending_in_readme_treated_as_extra(self):
        """If a pending example appears in the README, it's not extra — it's just pending."""
        content = _build_readme_with_examples(["converter", "pending-one"])
        result = audit_readme_staleness(
            content,
            expected_examples=["converter"],
            pending_examples=["pending-one"],
        )
        # pending-one is in the README but in the pending set, so NOT extra
        assert not result.is_stale
        assert result.extra_in_readme == []
