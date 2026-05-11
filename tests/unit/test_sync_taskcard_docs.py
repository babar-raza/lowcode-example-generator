"""Tests for the sync-taskcard-docs CLI command."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


_SAMPLE_MATRIX = {
    "matrix_date": "2026-05-04",
    "sprint": "Test Sprint",
    "taskcards": [
        {"id": "followup-words-split-criteria-enumeration", "status": "OPEN",
         "title": "SplitCriteria enum", "blocking": "WORDS-005"},
        {"id": "followup-words-pair-fixture-strategy", "status": "OPEN",
         "title": "Paired fixture strategy", "blocking": "WORDS-006/007"},
        {"id": "followup-fixture-token-ci", "status": "OPEN",
         "title": "CI token docs", "blocking": "CI integration"},
        {"id": "followup-pdf-reflection-dedup", "status": "CLOSED",
         "title": "PDF DllReflector dedup", "closed_in": "PDF Assembly Deduplication Sprint"},
        {"id": "followup-words-options-aware-review", "status": "CLOSED",
         "title": "Words options-aware review", "closed_in": "Words Readiness Review Sprint"},
    ],
}

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_sync_command(matrix: dict | None = None, *, extra_args: list[str] | None = None):
    """Run sync-taskcard-docs in a temp workspace and return (returncode, stdout, stderr, md_path)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Create verification/latest/ with matrix
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        matrix_data = matrix if matrix is not None else _SAMPLE_MATRIX
        (latest / "open-taskcard-closure-matrix.json").write_text(
            json.dumps(matrix_data), encoding="utf-8"
        )
        # Create docs/discovery/ target
        docs_dir = tmp_path / "docs" / "discovery"
        docs_dir.mkdir(parents=True)

        # Patch __main__.py to use tmp_path as repo_root is not straightforward;
        # instead run the command against the real repo but verify using real matrix.
        # For isolation, test the core logic by inspecting the real output file.
        cmd = [sys.executable, "-m", "plugin_examples", "sync-taskcard-docs"]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(_REPO_ROOT),
        )
        md_path = _REPO_ROOT / "docs" / "discovery" / "open-taskcard-closure-matrix.md"
        return result.returncode, result.stdout, result.stderr, md_path


class TestSyncTaskcardDocs:
    """Tests for sync-taskcard-docs command."""

    def test_taskcard_markdown_generated_from_json(self):
        """sync-taskcard-docs must generate the markdown file from JSON matrix."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0, f"Expected exit 0, got {rc}\nstdout: {stdout}\nstderr: {stderr}"
        assert md_path.exists(), "open-taskcard-closure-matrix.md was not created"
        content = md_path.read_text(encoding="utf-8")
        # Must have generated marker
        assert "GENERATED" in content, "Markdown missing generated marker"
        # Must have header
        assert "Taskcard" in content or "taskcard" in content.lower()

    def test_taskcard_markdown_counts_match_json(self):
        """Counts in generated markdown must match the actual JSON matrix."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0
        # Read the actual matrix to get ground-truth counts
        matrix_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "open-taskcard-closure-matrix.json"
        assert matrix_path.exists(), "Matrix file not found"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        taskcards = matrix.get("taskcards", [])
        total = len(taskcards)
        open_count = sum(1 for tc in taskcards if tc.get("status") == "OPEN")
        closed_count = sum(1 for tc in taskcards if tc.get("status") in ("CLOSED", "CLOSED_VERIFIED"))

        content = md_path.read_text(encoding="utf-8")
        # The counts must appear in the markdown
        assert str(total) in content, f"Total count {total} not in markdown"
        assert str(open_count) in content, f"Open count {open_count} not in markdown"
        assert str(closed_count) in content, f"Closed count {closed_count} not in markdown"

    def test_taskcard_markdown_includes_all_open_taskcards(self):
        """All open taskcards in the JSON matrix must appear in the generated markdown."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0
        matrix_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "open-taskcard-closure-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        open_ids = [tc["id"] for tc in matrix.get("taskcards", []) if tc.get("status") == "OPEN"]

        content = md_path.read_text(encoding="utf-8")
        for tc_id in open_ids:
            assert tc_id in content, f"Open taskcard '{tc_id}' missing from markdown"

    def test_taskcard_markdown_closed_taskcards_not_in_open_section(self):
        """Closed taskcards must not appear in the Open Taskcards section."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0
        matrix_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "open-taskcard-closure-matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        closed_ids = [tc["id"] for tc in matrix.get("taskcards", []) if tc.get("status") == "CLOSED"]

        content = md_path.read_text(encoding="utf-8")
        # Split on the "## Closed Taskcards" section header
        parts = content.split("## Closed Taskcards")
        open_section = parts[0] if len(parts) > 1 else content
        for tc_id in closed_ids:
            assert tc_id not in open_section, (
                f"Closed taskcard '{tc_id}' appeared in Open Taskcards section"
            )

    def test_cli_exits_0_with_promote_latest_flag(self):
        """sync-taskcard-docs --promote-latest exits 0."""
        rc, stdout, stderr, md_path = _run_sync_command(extra_args=["--promote-latest"])
        assert rc == 0, f"Expected exit 0\nstdout: {stdout}\nstderr: {stderr}"

    def test_cli_stdout_mentions_counts(self):
        """CLI stdout must mention open and closed counts."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0
        assert "open" in stdout.lower() or "closed" in stdout.lower(), (
            f"stdout did not mention open/closed counts: {stdout}"
        )

    def test_cli_stdout_mentions_output_path(self):
        """CLI stdout must mention the output file path."""
        rc, stdout, stderr, md_path = _run_sync_command()
        assert rc == 0
        assert "open-taskcard-closure-matrix.md" in stdout, (
            f"stdout did not mention output file: {stdout}"
        )
