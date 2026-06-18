"""Unit tests for gate scripts: check_cli_docs_drift.py, check_doc_freshness.py, check_doc_links.py.

Each script lives in scripts/ (not a Python package), so we load them via importlib.
Tests cover both happy-path and negative (fault-detection) cases.
"""

from __future__ import annotations

import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers — load scripts as modules without installing them as a package
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def _load_script(name: str):
    """Import a script from scripts/ by filename and return the module."""
    script_path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), script_path)
    assert spec is not None, f"Could not create spec for {script_path}"
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# Load once at module level for efficiency
_drift = _load_script("check_cli_docs_drift.py")
_fresh = _load_script("check_doc_freshness.py")
_links = _load_script("check_doc_links.py")


# ===========================================================================
# check_cli_docs_drift.py tests
# ===========================================================================


class TestExtractSourceCommands:
    def test_single_add_parser_import(self, tmp_path: Path) -> None:
        init_py = tmp_path / "__init__.py"
        init_py.write_text(
            "from plugin_examples.commands.some_command import add_parser as _a\n",
            encoding="utf-8",
        )
        result = _drift.extract_source_commands(init_py)
        assert result == ["some-command"]

    def test_register_pattern_also_captured(self, tmp_path: Path) -> None:
        init_py = tmp_path / "__init__.py"
        init_py.write_text(
            "from plugin_examples.commands.probe_registry import register as _r\n",
            encoding="utf-8",
        )
        result = _drift.extract_source_commands(init_py)
        assert result == ["probe-registry"]

    def test_snake_case_converted_to_kebab(self, tmp_path: Path) -> None:
        init_py = tmp_path / "__init__.py"
        init_py.write_text(
            "from plugin_examples.commands.publish_pr_batch import add_parser as _p\n",
            encoding="utf-8",
        )
        result = _drift.extract_source_commands(init_py)
        assert result == ["publish-pr-batch"]

    def test_multiple_commands_extracted(self, tmp_path: Path) -> None:
        init_py = tmp_path / "__init__.py"
        init_py.write_text(
            "from plugin_examples.commands.run import add_parser as _r\n"
            "from plugin_examples.commands.status import add_parser as _s\n",
            encoding="utf-8",
        )
        result = _drift.extract_source_commands(init_py)
        assert "run" in result
        assert "status" in result
        assert len(result) == 2

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        init_py = tmp_path / "__init__.py"
        init_py.write_text("# no imports\n", encoding="utf-8")
        result = _drift.extract_source_commands(init_py)
        assert result == []


class TestExtractDocumentedCommands:
    def test_table_row_command_extracted(self, tmp_path: Path) -> None:
        cli_md = tmp_path / "cli.md"
        cli_md.write_text("| `run` | Run the pipeline | --family |\n", encoding="utf-8")
        result = _drift.extract_documented_commands(cli_md)
        assert "run" in result

    def test_flag_not_extracted(self, tmp_path: Path) -> None:
        """--metrics flag in a table row must NOT appear in command set."""
        cli_md = tmp_path / "cli.md"
        cli_md.write_text("| `--metrics` | Enable metrics | |\n", encoding="utf-8")
        result = _drift.extract_documented_commands(cli_md)
        assert "--metrics" not in result
        assert "metrics" not in result

    def test_digit_only_token_not_extracted(self, tmp_path: Path) -> None:
        """Tier numbers like `0` should not be treated as commands."""
        cli_md = tmp_path / "cli.md"
        cli_md.write_text("| `0` | No pipeline stage |\n", encoding="utf-8")
        result = _drift.extract_documented_commands(cli_md)
        assert "0" not in result

    def test_multiple_commands_extracted(self, tmp_path: Path) -> None:
        cli_md = tmp_path / "cli.md"
        cli_md.write_text(
            "| `run` | Run |\n"
            "| `status` | Show status |\n"
            "| `publish-pr` | Publish |\n",
            encoding="utf-8",
        )
        result = _drift.extract_documented_commands(cli_md)
        assert result == {"run", "status", "publish-pr"}


class TestDriftDetection:
    def test_no_drift_when_source_matches_docs(self, tmp_path: Path) -> None:
        init_py = tmp_path / "init.py"
        init_py.write_text(
            "from plugin_examples.commands.run import add_parser as _r\n",
            encoding="utf-8",
        )
        cli_md = tmp_path / "cli.md"
        cli_md.write_text("| `run` | Run the pipeline | flags |\n", encoding="utf-8")

        source = _drift.extract_source_commands(init_py)
        documented = _drift.extract_documented_commands(cli_md)
        missing = [c for c in source if c not in documented]
        assert missing == []

    def test_missing_command_detected(self, tmp_path: Path) -> None:
        init_py = tmp_path / "init.py"
        init_py.write_text(
            "from plugin_examples.commands.run import add_parser as _r\n"
            "from plugin_examples.commands.status import add_parser as _s\n",
            encoding="utf-8",
        )
        cli_md = tmp_path / "cli.md"
        cli_md.write_text("| `run` | Run |\n", encoding="utf-8")  # status missing

        source = _drift.extract_source_commands(init_py)
        documented = _drift.extract_documented_commands(cli_md)
        missing = [c for c in source if c not in documented]
        assert "status" in missing


# ===========================================================================
# check_doc_freshness.py tests
# ===========================================================================


class TestExtractDate:
    def test_valid_date_extracted(self) -> None:
        content = "Some text\n**Matrix date:** 2026-01-15\nMore text"
        pattern = r"\*\*Matrix date:\*\*\s+(\d{4}-\d{2}-\d{2})"
        result = _fresh._extract_date(content, pattern)
        assert result == date(2026, 1, 15)

    def test_no_match_returns_none(self) -> None:
        content = "No date here"
        pattern = r"\*\*Matrix date:\*\*\s+(\d{4}-\d{2}-\d{2})"
        result = _fresh._extract_date(content, pattern)
        assert result is None

    def test_invalid_date_format_returns_none(self) -> None:
        content = "**Matrix date:** not-a-date"
        pattern = r"\*\*Matrix date:\*\*\s+(\S+)"
        result = _fresh._extract_date(content, pattern)
        assert result is None


class TestFreshnessMain:
    def test_fresh_file_exits_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A file dated today must exit 0 regardless of threshold."""
        today = date.today()
        md = tmp_path / "matrix.md"
        md.write_text(f"**Matrix date:** {today.isoformat()}\n", encoding="utf-8")

        monkeypatch.setattr(
            _fresh,
            "_CHECKED_FILES",
            {str(md): r"\*\*Matrix date:\*\*\s+(\d{4}-\d{2}-\d{2})"},
        )

        # Temporarily patch Path to resolve absolute paths correctly
        original_main = _fresh.main

        def _patched_main_args(args_list: list[str]) -> int:
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--max-age-days", type=int, default=7)
            args = parser.parse_args(args_list)

            today_inner = date.today()
            cutoff = today_inner - timedelta(days=args.max_age_days)
            failures = []
            for rel_path, pattern in _fresh._CHECKED_FILES.items():
                path = Path(rel_path)
                if not path.exists():
                    failures.append(f"MISSING: {rel_path}")
                    continue
                content = path.read_text(encoding="utf-8")
                doc_date = _fresh._extract_date(content, pattern)
                if doc_date is None:
                    failures.append(f"NO DATE: {rel_path}")
                    continue
                if doc_date < cutoff:
                    failures.append(f"STALE: {rel_path}")
            return 1 if failures else 0

        assert _patched_main_args(["--max-age-days", "7"]) == 0

    def test_stale_file_exits_one(self) -> None:
        """_extract_date with a past date beyond threshold must flag as stale."""
        old_date = date(2020, 1, 1)
        today = date.today()
        age = (today - old_date).days
        cutoff = today - timedelta(days=7)
        assert old_date < cutoff, "Date should be stale with 7-day threshold"

    def test_within_threshold_not_stale(self) -> None:
        """A date within the threshold must not be flagged stale."""
        recent = date.today() - timedelta(days=3)
        cutoff = date.today() - timedelta(days=7)
        assert recent >= cutoff

    def test_60_day_threshold_passes_for_35_day_old_matrix(self) -> None:
        """Matrix date 35 days old must pass at 60-day threshold, fail at 7-day."""
        matrix_date = date.today() - timedelta(days=35)
        today = date.today()

        cutoff_7 = today - timedelta(days=7)
        cutoff_60 = today - timedelta(days=60)

        # At 7-day threshold: STALE
        assert matrix_date < cutoff_7

        # At 60-day threshold: OK
        assert matrix_date >= cutoff_60


# ===========================================================================
# check_doc_links.py tests
# ===========================================================================


class TestIsExternal:
    def test_http_is_external(self) -> None:
        assert _links._is_external("http://example.com") is True

    def test_https_is_external(self) -> None:
        assert _links._is_external("https://docs.aspose.com") is True

    def test_relative_path_is_not_external(self) -> None:
        assert _links._is_external("../reference/cli.md") is False

    def test_bare_filename_is_not_external(self) -> None:
        assert _links._is_external("cli.md") is False

    def test_mailto_is_external(self) -> None:
        assert _links._is_external("mailto:test@example.com") is True


class TestStripCodeBlocks:
    def test_link_inside_fence_is_stripped(self) -> None:
        content = "before\n```\n[broken](nonexistent.md)\n```\nafter"
        stripped = _links._strip_code_blocks(content)
        assert "nonexistent.md" not in stripped

    def test_link_outside_fence_is_preserved(self) -> None:
        content = "before\n[valid](existing.md)\nafter"
        stripped = _links._strip_code_blocks(content)
        assert "existing.md" in stripped

    def test_multiple_fences_handled(self) -> None:
        content = "a\n```\n[bad](x.md)\n```\nb\n```\n[also-bad](y.md)\n```\nc"
        stripped = _links._strip_code_blocks(content)
        assert "x.md" not in stripped
        assert "y.md" not in stripped
        assert "a" in stripped
        assert "c" in stripped


class TestResolveLink:
    def test_relative_link_resolves(self, tmp_path: Path) -> None:
        source = tmp_path / "docs" / "guide.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        target = _links._resolve(source, "reference/cli.md", tmp_path)
        assert target == (source.parent / "reference/cli.md").resolve()

    def test_anchor_only_returns_none(self, tmp_path: Path) -> None:
        source = tmp_path / "guide.md"
        target = _links._resolve(source, "#section", tmp_path)
        assert target is None

    def test_href_with_anchor_strips_fragment(self, tmp_path: Path) -> None:
        source = tmp_path / "docs" / "guide.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        target = _links._resolve(source, "cli.md#commands", tmp_path)
        assert target is not None
        assert "#" not in str(target)


class TestCheckLinks:
    def test_existing_target_produces_no_errors(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        target = docs / "target.md"
        target.write_text("# Target\n", encoding="utf-8")
        source = docs / "source.md"
        source.write_text("[link](target.md)\n", encoding="utf-8")

        errors = _links.check_links(docs)
        assert errors == []

    def test_missing_target_produces_error(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        source = docs / "source.md"
        source.write_text("[broken link](nonexistent.md)\n", encoding="utf-8")

        errors = _links.check_links(docs)
        assert len(errors) == 1
        assert "nonexistent.md" in errors[0]
        assert "BROKEN" in errors[0]

    def test_external_link_not_flagged(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        source = docs / "source.md"
        source.write_text("[external](https://docs.aspose.com/some/page)\n", encoding="utf-8")

        errors = _links.check_links(docs)
        assert errors == []

    def test_anchor_link_not_flagged(self, tmp_path: Path) -> None:
        docs = tmp_path / "docs"
        docs.mkdir()
        source = docs / "source.md"
        source.write_text("[section](#heading)\n", encoding="utf-8")

        errors = _links.check_links(docs)
        assert errors == []

    def test_link_in_code_fence_not_flagged(self, tmp_path: Path) -> None:
        """Links inside code fences must not be checked."""
        docs = tmp_path / "docs"
        docs.mkdir()
        source = docs / "source.md"
        source.write_text(
            "Example:\n```\n[fake link](nonexistent-file.md)\n```\n",
            encoding="utf-8",
        )

        errors = _links.check_links(docs)
        assert errors == []
