"""Helper methods shared across all rule mixins."""

from __future__ import annotations

import json
import re as _re
from pathlib import Path


class ValidatorHelpers:
    """Mixin providing helper methods used by rule implementations."""

    bundle_dir: Path
    source_root: Path | None

    def _resolve_sprint_relative_path(self, src: str) -> "Path":
        """Resolve a repo-relative source path to an absolute Path.

        source_path is stored as ``reports/{sprint_id}/handoff/per-family/{family}/README.md``.
        Strip the ``reports/{sprint_id}/`` prefix and resolve relative to bundle_dir,
        which avoids dependency on the host repo layout in tests.
        """
        sprint_id = self._read_sprint_id()
        prefix = f"reports/{sprint_id}/"
        if src.startswith(prefix):
            return self.bundle_dir / src[len(prefix):]
        # Fallback: resolve relative to bundle_dir parent (reports/) then repo root
        return self.bundle_dir.parent.parent / src

    def _get_stale_paths_in_content(self, content: str) -> list[str]:
        """Return list of stale sprint path prefixes found in content.

        A path is stale if it matches reports/sprintN/ where N is not the current sprint,
        or workspace/pr-dry-run.
        """
        import re as _re
        sprint_id = self._read_sprint_id()
        current_prefix = f"reports/{sprint_id}/"
        found_prefixes = set(_re.findall(r"reports/sprint[^/\"']+/|workspace/pr-dry-run", content))
        stale = sorted(p for p in found_prefixes if p != current_prefix)
        return stale

    def _scan_source_for_import(
        self, source_root: Path, module_name: str, exclude_self: str = ""
    ) -> list[str]:
        """Scan Python source files in source_root for imports of module_name.

        Returns list of relative file paths that import the module.
        """
        found = []
        for py_file in source_root.rglob("*.py"):
            if exclude_self and py_file.name == exclude_self:
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
                if module_name in text:
                    found.append(str(py_file.relative_to(source_root)))
            except OSError:
                pass
        return found

    def _read_sprint_id(self) -> str:
        for fname in ["sprint-state.json", "evidence-contract.json"]:
            p = self.bundle_dir / fname
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    return data.get("sprint_id", str(self.bundle_dir))
                except (OSError, ValueError):
                    pass
        return str(self.bundle_dir)
