"""Unit tests for engineering hygiene validators EHV-01..05."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest

from plugin_examples.fixture_factory.engineering_hygiene_validators import (
    check_silent_bare_excepts,
    check_bare_excepts,
    check_integration_test_count,
    check_bandit_config,
    check_codeowners,
    run_all_ehv_validators,
    _find_silent_bare_excepts,
    _find_bare_excepts,
    _count_integration_test_functions,
)


class TestEHV01SilentBareExcepts:
    def test_detects_silent_except_exception_pass(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "bad.py").write_text(textwrap.dedent("""
            def foo():
                try:
                    x = int("abc")
                except Exception:
                    pass
        """), encoding="utf-8")
        violations = _find_silent_bare_excepts(src)
        assert len(violations) == 1
        assert "bad.py" in violations[0]

    def test_passes_when_no_silent_handlers(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "ok.py").write_text(textwrap.dedent("""
            import logging
            logger = logging.getLogger(__name__)

            def foo():
                try:
                    x = int("abc")
                except ValueError as exc:
                    logger.warning("parse error: %s", exc)
        """), encoding="utf-8")
        violations = _find_silent_bare_excepts(src)
        assert violations == []

    def test_ignores_exception_with_logging(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        # except Exception: with a log call is not a silent handler
        (src / "ok.py").write_text(textwrap.dedent("""
            import logging
            logger = logging.getLogger(__name__)

            def foo():
                try:
                    pass
                except Exception:
                    logger.debug("skipping")
        """), encoding="utf-8")
        violations = _find_silent_bare_excepts(src)
        assert violations == []

    def test_check_function_returns_fail_on_violation(self, tmp_path: Path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "bad.py").write_text(textwrap.dedent("""
            def f():
                try:
                    pass
                except Exception:
                    pass
        """), encoding="utf-8")
        result = check_silent_bare_excepts(repo_root=tmp_path)
        assert not result.passed
        assert "EHV-01" in result.validator_id

    def test_check_function_returns_pass_on_clean_src(self, tmp_path: Path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "clean.py").write_text("def f(): pass\n", encoding="utf-8")
        result = check_silent_bare_excepts(repo_root=tmp_path)
        assert result.passed

    def test_returns_skip_when_no_src_dir(self, tmp_path: Path) -> None:
        result = check_silent_bare_excepts(repo_root=tmp_path)
        assert result.passed  # SKIP is not a failure


class TestEHV02BareExcepts:
    def test_detects_bare_except_no_type(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "bad.py").write_text(textwrap.dedent("""
            def foo():
                try:
                    pass
                except:
                    pass
        """), encoding="utf-8")
        violations = _find_bare_excepts(src)
        assert len(violations) == 1

    def test_passes_when_all_have_types(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        src.mkdir()
        (src / "ok.py").write_text(textwrap.dedent("""
            def foo():
                try:
                    pass
                except ValueError:
                    pass
        """), encoding="utf-8")
        violations = _find_bare_excepts(src)
        assert violations == []


class TestEHV03IntegrationTestCount:
    def test_passes_when_enough_tests(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests" / "integration"
        tests_dir.mkdir(parents=True)
        # Write a file with 6 test functions
        funcs = "\n".join(f"def test_{i}(): pass" for i in range(6))
        (tests_dir / "test_example.py").write_text(funcs, encoding="utf-8")
        result = check_integration_test_count(repo_root=tmp_path)
        assert result.passed

    def test_fails_when_too_few_tests(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests" / "integration"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_example.py").write_text("def test_one(): pass\n", encoding="utf-8")
        result = check_integration_test_count(repo_root=tmp_path)
        assert not result.passed
        assert "minimum" in result.message

    def test_counts_only_test_functions(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests" / "integration"
        tests_dir.mkdir(parents=True)
        (tests_dir / "test_example.py").write_text(textwrap.dedent("""
            def helper(): pass
            def test_one(): pass
            def test_two(): pass
            class TestFoo:
                def test_three(self): pass
                def helper_method(self): pass
        """), encoding="utf-8")
        count = _count_integration_test_functions(tmp_path / "tests")
        assert count == 3  # test_one, test_two, test_three


class TestEHV04BanditConfig:
    def test_passes_when_bandit_section_present(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[tool.bandit]\nskips = ['B101']\n", encoding="utf-8")
        result = check_bandit_config(repo_root=tmp_path)
        assert result.passed

    def test_fails_when_no_bandit_section(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
        result = check_bandit_config(repo_root=tmp_path)
        assert not result.passed

    def test_fails_when_no_pyproject(self, tmp_path: Path) -> None:
        result = check_bandit_config(repo_root=tmp_path)
        assert not result.passed


class TestEHV05Codeowners:
    def test_passes_when_codeowners_present(self, tmp_path: Path) -> None:
        (tmp_path / "CODEOWNERS").write_text("* @owner/team\n", encoding="utf-8")
        result = check_codeowners(repo_root=tmp_path)
        assert result.passed

    def test_fails_when_codeowners_missing(self, tmp_path: Path) -> None:
        result = check_codeowners(repo_root=tmp_path)
        assert not result.passed

    def test_fails_when_codeowners_empty(self, tmp_path: Path) -> None:
        (tmp_path / "CODEOWNERS").write_text("", encoding="utf-8")
        result = check_codeowners(repo_root=tmp_path)
        assert not result.passed


class TestRunAllEHVValidators:
    def test_returns_5_results(self, tmp_path: Path) -> None:
        """run_all_ehv_validators always returns exactly 5 results."""
        results = run_all_ehv_validators(repo_root=tmp_path)
        assert len(results) == 5

    def test_validator_ids_are_unique(self, tmp_path: Path) -> None:
        results = run_all_ehv_validators(repo_root=tmp_path)
        ids = [r.validator_id for r in results]
        assert len(ids) == len(set(ids))

    def test_all_results_have_message(self, tmp_path: Path) -> None:
        results = run_all_ehv_validators(repo_root=tmp_path)
        for r in results:
            assert r.message, f"Result {r.validator_id} has no message"

    def test_to_dict_has_required_fields(self, tmp_path: Path) -> None:
        results = run_all_ehv_validators(repo_root=tmp_path)
        for r in results:
            d = r.to_dict()
            assert "validator_id" in d
            assert "passed" in d
            assert "message" in d
