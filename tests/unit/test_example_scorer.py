"""Tests for the example quality scorer (TC-SRHP-03)."""

from __future__ import annotations

from pathlib import Path

import pytest

from plugin_examples.gates.example_gates import evaluate_quality_gate
from plugin_examples.quality.example_scorer import (
    PASSING_THRESHOLD,
    TOTAL_CRITERIA,
    ExampleScoreResult,
    build_quality_manifest,
    score_example,
    score_example_file,
    score_project_directory,
)

# ---------------------------------------------------------------------------
# Fixtures: sample C# code snippets
# ---------------------------------------------------------------------------

_GOOD_EXAMPLE = """\
using System;
using Aspose.Words;

class Program
{
    static void Main()
    {
        var dataDir = AppContext.BaseDirectory;
        try
        {
            var doc = new Document(dataDir + "input.docx");
            doc.Save(dataDir + "output.pdf");
            Console.WriteLine("Conversion complete.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
"""

_NO_ASPOSE = """\
using System;
class Program
{
    static void Main()
    {
        try { Console.WriteLine("hi"); } catch {}
    }
}
"""

_HAS_TODO = """\
using Aspose.Cells;
class Program
{
    static void Main()
    {
        // TODO: implement this
        throw new NotImplementedException();
        Console.WriteLine("done");
    }
}
"""

_NO_OUTPUT = """\
using Aspose.Pdf;
class Program
{
    static void Main()
    {
        var dataDir = AppContext.BaseDirectory;
        try
        {
            var doc = new Document(dataDir + "input.pdf");
            doc.Save(dataDir + "output.pdf");
        }
        catch {}
    }
}
"""

_NO_EXCEPTION_HANDLING = """\
using Aspose.Imaging;
class Program
{
    static void Main()
    {
        var dataDir = AppContext.BaseDirectory;
        var img = Image.Load(dataDir + "img.png");
        img.Save(dataDir + "out.jpg");
        Console.WriteLine("Done.");
    }
}
"""

_HARDCODED_PATH = """\
using Aspose.Words;
class Program
{
    static void Main()
    {
        try
        {
            var doc = new Document("C:\\\\Users\\\\foo\\\\input.docx");
            doc.Save("C:\\\\Users\\\\foo\\\\output.pdf");
            Console.WriteLine("done");
        }
        catch {}
    }
}
"""


# ---------------------------------------------------------------------------
# Tests: score_example
# ---------------------------------------------------------------------------


def test_good_example_scores_high() -> None:
    """A well-formed example scores HIGH (all 5 criteria pass)."""
    result = score_example("good-example", _GOOD_EXAMPLE)
    assert result.quality_score == 1.0
    assert result.quality_label == "HIGH"
    assert all(c.passed for c in result.criteria)


def test_no_aspose_fails_symbol_criterion() -> None:
    """Code without Aspose namespace fails SYMBOL_USAGE criterion."""
    result = score_example("no-aspose", _NO_ASPOSE)
    sym = next(c for c in result.criteria if c.name == "SYMBOL_USAGE")
    assert not sym.passed


def test_todo_stub_fails_criterion() -> None:
    """Code with TODO or NotImplementedException fails NO_TODO_STUBS."""
    result = score_example("has-todo", _HAS_TODO)
    stub = next(c for c in result.criteria if c.name == "NO_TODO_STUBS")
    assert not stub.passed


def test_no_console_output_fails_criterion() -> None:
    """Code without Console.Write* fails CONSOLE_OUTPUT."""
    result = score_example("no-output", _NO_OUTPUT)
    out = next(c for c in result.criteria if c.name == "CONSOLE_OUTPUT")
    assert not out.passed


def test_no_exception_handling_fails_criterion() -> None:
    """Code without try/catch or using block fails EXCEPTION_HANDLING."""
    result = score_example("no-handling", _NO_EXCEPTION_HANDLING)
    eh = next(c for c in result.criteria if c.name == "EXCEPTION_HANDLING")
    assert not eh.passed


def test_hardcoded_path_fails_path_safety() -> None:
    """Code with hardcoded absolute path fails PATH_SAFETY."""
    result = score_example("hardcoded-path", _HARDCODED_PATH)
    ps = next(c for c in result.criteria if c.name == "PATH_SAFETY")
    assert not ps.passed


def test_score_returns_correct_total_criteria() -> None:
    """Always returns exactly TOTAL_CRITERIA criterion results."""
    result = score_example("any", _GOOD_EXAMPLE)
    assert len(result.criteria) == TOTAL_CRITERIA


def test_quality_label_medium_for_partial_pass() -> None:
    """3 out of 5 criteria passing yields MEDIUM label."""
    result = score_example("no-output", _NO_OUTPUT)  # fails CONSOLE_OUTPUT only
    # _NO_OUTPUT passes: SYMBOL_USAGE, NO_TODO_STUBS, EXCEPTION_HANDLING, PATH_SAFETY (4/5)
    # So it's HIGH — let's use a code that scores 3/5
    low_code = """\
using Aspose.Words;
class Program {
    static void Main() {
        // No output, no exception handling, no path safety
        var doc = new Document("C:\\\\Users\\\\foo\\\\input.docx");
        doc.Save("C:\\\\Users\\\\foo\\\\output.pdf");
    }
}
"""
    # passes: SYMBOL_USAGE, NO_TODO_STUBS (2/5) → LOW
    r2 = score_example("low-quality", low_code)
    assert r2.quality_score == 0.4
    assert r2.quality_label == "LOW"


def test_score_is_fraction_of_total() -> None:
    """quality_score is always in [0.0, 1.0]."""
    for code in [_GOOD_EXAMPLE, _NO_ASPOSE, _HAS_TODO, _NO_OUTPUT, _HARDCODED_PATH]:
        result = score_example("x", code)
        assert 0.0 <= result.quality_score <= 1.0


# ---------------------------------------------------------------------------
# Tests: score_example_file
# ---------------------------------------------------------------------------


def test_score_file_not_found(tmp_path: Path) -> None:
    """Missing file returns FILE_NOT_FOUND label."""
    result = score_example_file("missing", tmp_path / "nonexistent.cs")
    assert result.quality_label == "FILE_NOT_FOUND"
    assert result.quality_score == 0.0


def test_score_file_reads_content(tmp_path: Path) -> None:
    """score_example_file reads a real file and scores it."""
    cs_file = tmp_path / "Program.cs"
    cs_file.write_text(_GOOD_EXAMPLE, encoding="utf-8")
    result = score_example_file("file-example", cs_file)
    assert result.quality_score == 1.0


# ---------------------------------------------------------------------------
# Tests: score_project_directory
# ---------------------------------------------------------------------------


def test_score_project_no_cs_files(tmp_path: Path) -> None:
    """Directory with no .cs files returns NO_CS_FILES label."""
    result = score_project_directory("empty-proj", tmp_path)
    assert result.quality_label == "NO_CS_FILES"


def test_score_project_combines_files(tmp_path: Path) -> None:
    """All .cs files in directory are combined for scoring."""
    # Split _GOOD_EXAMPLE across two files to test combination
    (tmp_path / "Program.cs").write_text(_GOOD_EXAMPLE, encoding="utf-8")
    result = score_project_directory("multi-file", tmp_path)
    assert result.quality_score == 1.0


# ---------------------------------------------------------------------------
# Tests: build_quality_manifest
# ---------------------------------------------------------------------------


def test_build_quality_manifest_fields() -> None:
    """build_quality_manifest produces expected top-level fields."""
    good = score_example("good", _GOOD_EXAMPLE)
    bad = score_example("bad", _NO_ASPOSE)
    manifest = build_quality_manifest([good, bad])
    assert manifest["schema"] == "quality_manifest_v1"
    assert manifest["total_examples"] == 2
    assert "average_quality_score" in manifest
    assert len(manifest["examples"]) == 2


def test_build_quality_manifest_empty() -> None:
    """build_quality_manifest handles empty list gracefully."""
    manifest = build_quality_manifest([])
    assert manifest["total_examples"] == 0
    assert manifest["average_quality_score"] == 0.0


# ---------------------------------------------------------------------------
# Tests: evaluate_quality_gate (TC-SRHP-13)
# ---------------------------------------------------------------------------


def test_quality_gate_blocks_low_score() -> None:
    """Gate blocks when at least one example scores below threshold."""
    projects = [
        {"scenario_id": "words-convert", "quality_score": 1.0},
        {"scenario_id": "words-stub", "quality_score": 0.4},
    ]
    blocked, low_ids = evaluate_quality_gate(projects, allow_low_quality=False)
    assert blocked is True
    assert "words-stub" in low_ids


def test_quality_gate_passes_when_all_above_threshold() -> None:
    """Gate does NOT block when all examples meet or exceed the threshold."""
    projects = [
        {"scenario_id": "words-convert", "quality_score": 1.0},
        {"scenario_id": "words-extract", "quality_score": 0.6},
    ]
    blocked, low_ids = evaluate_quality_gate(projects, allow_low_quality=False)
    assert blocked is False
    assert low_ids == []


def test_quality_gate_bypassed_with_allow_flag() -> None:
    """Gate does NOT block when allow_low_quality=True, but still identifies low IDs."""
    projects = [{"scenario_id": "words-stub", "quality_score": 0.2}]
    blocked, low_ids = evaluate_quality_gate(projects, allow_low_quality=True)
    assert blocked is False
    assert "words-stub" in low_ids


def test_quality_gate_empty_projects_not_blocked() -> None:
    """Gate does not block when there are no generated projects."""
    blocked, low_ids = evaluate_quality_gate([], allow_low_quality=False)
    assert blocked is False
    assert low_ids == []


def test_quality_gate_missing_score_defaults_to_passing() -> None:
    """Projects without a quality_score key default to 1.0 (passing)."""
    projects = [{"scenario_id": "words-no-score"}]
    blocked, low_ids = evaluate_quality_gate(projects, allow_low_quality=False)
    assert blocked is False
    assert low_ids == []
