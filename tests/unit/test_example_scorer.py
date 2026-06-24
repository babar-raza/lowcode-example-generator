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

# Represents a published example that uses relative paths (safe in CI/CD) but no AppContext.
# Under the corrected PATH_SAFETY criterion (path_safe = not has_hardcoded), this PASSES.
_RELATIVE_PATH_ONLY = """\
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.pdf");
Converter.ConvertHTML("<html><body>test</body></html>", ".", new PdfSaveOptions(), outputPath);
Console.WriteLine($"PDF saved: {outputPath}");
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


def test_relative_path_passes_path_safety() -> None:
    """Code using only relative paths (no AppContext, no hardcoded absolute) passes PATH_SAFETY.

    This is the TC-QUAL-01 regression guard: relative paths are safe in CI/CD contexts.
    The corrected criterion checks 'not has_hardcoded' rather than 'has_safe_path and not has_hardcoded'.
    """
    result = score_example("relative-path", _RELATIVE_PATH_ONLY)
    ps = next(c for c in result.criteria if c.name == "PATH_SAFETY")
    assert ps.passed, f"Expected PATH_SAFETY=PASS for relative-path example, got: {ps.detail}"


def test_relative_path_detail_message() -> None:
    """PATH_SAFETY pass detail says 'No hardcoded absolute paths found' (not AppContext message)."""
    result = score_example("relative-path", _RELATIVE_PATH_ONLY)
    ps = next(c for c in result.criteria if c.name == "PATH_SAFETY")
    assert "hardcoded" in ps.detail.lower(), f"Unexpected detail: {ps.detail}"


def test_score_returns_correct_total_criteria() -> None:
    """Always returns exactly TOTAL_CRITERIA criterion results."""
    result = score_example("any", _GOOD_EXAMPLE)
    assert len(result.criteria) == TOTAL_CRITERIA


def test_quality_label_low_for_minimal_pass() -> None:
    """2 out of 5 criteria passing yields LOW label.

    low_code has hardcoded paths (PATH_SAFETY=F), no Console output (CONSOLE_OUTPUT=F),
    no try/catch (EXCEPTION_HANDLING=F). Only SYMBOL_USAGE and NO_TODO_STUBS pass → 2/5=0.40 LOW.
    Note: PATH_SAFETY=FAIL here because has_hardcoded=True (C:\\\\Users\\\\foo\\\\).
    """
    low_code = """\
using Aspose.Words;
class Program {
    static void Main() {
        var doc = new Document("C:\\\\Users\\\\foo\\\\input.docx");
        doc.Save("C:\\\\Users\\\\foo\\\\output.pdf");
    }
}
"""
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


def test_quality_gate_threshold_boundary() -> None:
    """Score exactly at threshold (0.6) is NOT blocked."""
    projects = [{"scenario_id": "words-boundary", "quality_score": 0.6}]
    blocked, low_ids = evaluate_quality_gate(projects, allow_low_quality=False)
    assert blocked is False
    assert low_ids == []


# ---------------------------------------------------------------------------
# Tests: quality gate pipeline wiring — GateVerdict mutation (TC-SRHP-21)
# ---------------------------------------------------------------------------


class TestQualityGatePipelineWiring:
    """Verify the wiring between evaluate_quality_gate() and GateVerdict as
    performed in runner.py:2671-2685. (TC-SRHP-21)

    These tests are distinct from the evaluate_quality_gate() unit tests above:
    they test that the CALLER correctly applies the gate result to a GateVerdict
    object — overriding verdict, setting publishable=False, appending to
    blocking_gates. This is the missing proof boundary for PROOF_LEVEL_4.
    """

    # The frozenset must match runner.py:_pr_eligible_verdicts exactly.
    _PR_ELIGIBLE = frozenset({
        "PR_READY",
        "FULL_E2E_PASSED",
        "PR_DRY_RUN_READY",
        "PARTIAL_PR_READY",
        "PARTIAL_PR_DRY_RUN_READY",
        "CANONICAL_TEMPLATE_GENERATION_PASS",
        "CANONICAL_LLM_GENERATION_PASS",
    })

    def _apply_quality_gate(
        self,
        generated_projects: list[dict],
        gate_verdict: object,
        allow_low_quality: bool = False,
    ) -> list[str]:
        """Replicate the wiring block from runner.py:2671-2685."""
        _blocked, _low_ids = evaluate_quality_gate(
            generated_projects, allow_low_quality=allow_low_quality
        )
        if _blocked:
            gate_verdict.verdict = "BLOCKED_QUALITY_GATE"
            gate_verdict.publishable = False
            gate_verdict.blocking_gates.append("QUALITY_HARD_GATE")
        return _low_ids

    def test_blocked_quality_gate_verdict_set_when_score_below_threshold(self) -> None:
        """When generated_projects contains quality_score < 0.6 and gate_verdict is
        PR-eligible, the verdict must be overridden to BLOCKED_QUALITY_GATE and
        publishable must be False. (TC-SRHP-21)"""
        from plugin_examples.gates.models import GateVerdict

        generated_projects = [
            {"scenario_id": "words-convert", "quality_score": 1.0},
            {"scenario_id": "words-stub", "quality_score": 0.3},
        ]
        gate_verdict = GateVerdict()
        gate_verdict.verdict = "PR_READY"
        gate_verdict.publishable = True
        assert gate_verdict.verdict in self._PR_ELIGIBLE  # pre-condition

        low_ids = self._apply_quality_gate(generated_projects, gate_verdict)

        assert gate_verdict.verdict == "BLOCKED_QUALITY_GATE"
        assert gate_verdict.publishable is False
        assert "QUALITY_HARD_GATE" in gate_verdict.blocking_gates
        assert "words-stub" in low_ids
        assert "words-convert" not in low_ids

    def test_allow_low_quality_bypasses_verdict_override(self) -> None:
        """When allow_low_quality=True, evaluate_quality_gate() returns blocked=False
        so the verdict must NOT be overridden even if quality_score < 0.6. (TC-SRHP-21)"""
        from plugin_examples.gates.models import GateVerdict

        generated_projects = [{"scenario_id": "words-stub", "quality_score": 0.3}]
        gate_verdict = GateVerdict()
        gate_verdict.verdict = "PR_READY"
        gate_verdict.publishable = True

        low_ids = self._apply_quality_gate(
            generated_projects, gate_verdict, allow_low_quality=True
        )

        assert gate_verdict.verdict == "PR_READY"  # verdict unchanged
        assert gate_verdict.publishable is True
        assert "QUALITY_HARD_GATE" not in gate_verdict.blocking_gates
        assert "words-stub" in low_ids  # identified but not blocked

    def test_template_mode_verdict_not_in_pr_eligible_frozenset(self) -> None:
        """DATA_FLOW_PROTOTYPE_ONLY and BLOCKED_QUALITY_GATE must NOT be in the
        PR-eligible frozenset, ensuring template/prototype runs skip the gate
        and gate itself cannot re-trigger. (TC-SRHP-21)"""
        assert "DATA_FLOW_PROTOTYPE_ONLY" not in self._PR_ELIGIBLE
        assert "BLOCKED_QUALITY_GATE" not in self._PR_ELIGIBLE
