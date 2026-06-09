"""Tests for new_sprint.py launcher — Wave 25 Lane H.

Verifies:
- Generates coordinator script from template
- Does NOT overwrite without --force
- With --force, overwrites existing file
- Generated script has correct sprint/date/lanes substituted
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_generates_coordinator_script(tmp_path, monkeypatch):
    """new_sprint.py creates the coordinator script at the expected path."""
    # Override scripts dir to use tmp_path so we don't pollute the real scripts/
    from scripts import new_sprint
    scripts_dir_orig = new_sprint._SCRIPTS_DIR
    monkeypatch.setattr(new_sprint, "_SCRIPTS_DIR", tmp_path)

    rc = new_sprint.main(["--sprint", "wave99", "--date", "20261231", "--lanes", "A,B,Z"])

    assert rc == 0
    output = tmp_path / "_wave99_coordinator.py"
    assert output.exists()


def test_no_overwrite_without_force(tmp_path, monkeypatch):
    """Without --force, new_sprint.py returns 1 and does not overwrite."""
    from scripts import new_sprint
    monkeypatch.setattr(new_sprint, "_SCRIPTS_DIR", tmp_path)

    # First call — create
    new_sprint.main(["--sprint", "wave99", "--date", "20261231", "--lanes", "A"])
    output = tmp_path / "_wave99_coordinator.py"
    original_mtime = output.stat().st_mtime

    # Second call without --force — must fail
    rc = new_sprint.main(["--sprint", "wave99", "--date", "20261231", "--lanes", "A"])
    assert rc == 1
    assert output.stat().st_mtime == original_mtime  # unchanged


def test_force_flag_overwrites(tmp_path, monkeypatch):
    """With --force, new_sprint.py overwrites existing file."""
    from scripts import new_sprint
    monkeypatch.setattr(new_sprint, "_SCRIPTS_DIR", tmp_path)

    new_sprint.main(["--sprint", "wave99", "--date", "20261231", "--lanes", "A"])
    output = tmp_path / "_wave99_coordinator.py"
    first_content = output.read_text()

    rc = new_sprint.main(["--sprint", "wave99", "--date", "20261231", "--lanes", "A,B", "--force"])
    assert rc == 0
    assert output.exists()


def test_substitutions_in_generated_script(tmp_path, monkeypatch):
    """Sprint, date, and lanes must be substituted in generated script."""
    from scripts import new_sprint
    monkeypatch.setattr(new_sprint, "_SCRIPTS_DIR", tmp_path)

    new_sprint.main(["--sprint", "wave42", "--date", "20270101", "--lanes", "A,B,C"])
    content = (tmp_path / "_wave42_coordinator.py").read_text()

    assert "wave42" in content
    assert "20270101" in content
    assert "A,B,C" in content
    # Template placeholders must be replaced
    assert "$SPRINT" not in content
    assert "$DATE" not in content
    assert "$LANES" not in content
