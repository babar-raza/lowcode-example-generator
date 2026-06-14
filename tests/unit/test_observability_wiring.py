"""Regression test: structured logging must be wired in __main__ and critical modules."""

import ast
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src" / "plugin_examples"


def _imports_from_observability(filepath: Path) -> bool:
    """Check if a Python file imports from plugin_examples.observability."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "plugin_examples.observability":
            return True
    return False


def test_main_uses_configure_logging():
    """__main__.py must import configure_logging from observability."""
    main_file = _SRC / "__main__.py"
    assert main_file.exists(), "__main__.py not found"
    tree = ast.parse(main_file.read_text(encoding="utf-8"))
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "plugin_examples.observability":
            imported_names.extend(alias.name for alias in node.names)
    assert "configure_logging" in imported_names, (
        "__main__.py must import configure_logging from plugin_examples.observability"
    )


def test_at_least_10_modules_use_observability():
    """At least 10 source modules must import from plugin_examples.observability."""
    count = 0
    for py in _SRC.rglob("*.py"):
        if py.name == "__init__.py" or py.name == "observability.py":
            continue
        if _imports_from_observability(py):
            count += 1
    assert count >= 10, (
        f"Only {count} source modules import from observability (expected >= 10)"
    )
