"""Cumulative README example inventory for LowCode family repositories.

Discovers all examples across multiple PR packages and post-merge evidence
for a given family, supporting repo-scoped README rendering instead of
per-package rendering.

Inventory modes:
  - repo_actual:              examples present in the target repo's main branch
  - current_package_overlay:  repo_actual UNION single package being prepared
  - batch_overlay:            repo_actual UNION multiple packages
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class InventoryEntry:
    """A single example discovered from any source."""

    name: str
    source_package: str  # e.g. "pdf-controlled-pilot-pr5"
    source_type: str  # "pr_package" | "post_merge" | "repo_actual"
    output_format: str = ""
    has_program_cs: bool = False
    package_path: str = ""  # absolute path string to the containing package


@dataclass
class InventoryAuditTrail:
    """Records what was scanned and how conflicts were resolved."""

    family: str
    inventory_mode: str
    sources_scanned: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    dedup_log: list[str] = field(default_factory=list)


def _scan_package_examples(
    family: str,
    package_path: Path,
) -> list[InventoryEntry]:
    """Scan a single PR dry-run package for example directories."""
    entries: list[InventoryEntry] = []
    examples_root = package_path / "examples" / family / "lowcode"
    if not examples_root.exists():
        return entries
    for d in sorted(examples_root.iterdir()):
        if d.is_dir():
            has_cs = (d / "Program.cs").exists()
            entries.append(
                InventoryEntry(
                    name=d.name,
                    source_package=package_path.name,
                    source_type="pr_package",
                    has_program_cs=has_cs,
                    package_path=str(package_path),
                )
            )
    return entries


def _load_post_merge_examples(
    family: str,
    verification_dir: Path,
) -> list[InventoryEntry]:
    """Load examples from post-merge validation JSON (published to remote)."""
    entries: list[InventoryEntry] = []
    pm_path = verification_dir / "latest" / f"{family}-post-merge-clean-checkout-validation.json"
    if not pm_path.exists():
        return entries
    try:
        data = json.loads(pm_path.read_text(encoding="utf-8"))
        for ex in data.get("examples", []):
            name = ex.get("name", "")
            if name:
                entries.append(
                    InventoryEntry(
                        name=name,
                        source_package="post-merge",
                        source_type="post_merge",
                        output_format=ex.get("output_format", ""),
                    )
                )
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to read post-merge JSON for %s: %s", family, e)
    return entries


def discover_family_inventory(
    family: str,
    repo_root: Path,
    inventory_mode: str = "repo_actual",
    current_package_path: Path | None = None,
    batch_package_paths: list[Path] | None = None,
    repo_actual_examples: list[str] | None = None,
) -> tuple[list[InventoryEntry], InventoryAuditTrail]:
    """Discover all examples for a family using the specified inventory mode.

    Args:
        family: Family name (e.g. "pdf").
        repo_root: Path to the pipeline repository root.
        inventory_mode: One of "repo_actual", "current_package_overlay",
            "batch_overlay".
        current_package_path: For current_package_overlay mode — the single
            package being prepared for a PR.
        batch_package_paths: For batch_overlay mode — all packages to include.
        repo_actual_examples: Example names known to be on the target repo's
            main branch (from GitHub API or post-merge evidence). If None,
            post-merge JSON is used as fallback.

    Returns:
        (entries, audit_trail) — deduplicated inventory and audit trail.
    """
    valid_modes = ("repo_actual", "current_package_overlay", "batch_overlay")
    if inventory_mode not in valid_modes:
        raise ValueError(f"Invalid inventory_mode '{inventory_mode}'. Must be one of {valid_modes}")

    trail = InventoryAuditTrail(family=family, inventory_mode=inventory_mode)
    verification_dir = repo_root / "workspace" / "verification"

    # --- 1. Establish repo_actual base ---
    base_entries: dict[str, InventoryEntry] = {}

    if repo_actual_examples is not None:
        # Explicit list from GitHub API or caller
        for name in repo_actual_examples:
            base_entries[name] = InventoryEntry(
                name=name,
                source_package="repo_actual",
                source_type="repo_actual",
            )
        trail.sources_scanned.append(
            {
                "source_type": "repo_actual_explicit",
                "entry_count": len(repo_actual_examples),
            }
        )
    else:
        # Fallback to post-merge evidence
        pm_entries = _load_post_merge_examples(family, verification_dir)
        for e in pm_entries:
            base_entries[e.name] = e
        trail.sources_scanned.append(
            {
                "source_type": "post_merge_json",
                "path": str(verification_dir / "latest" / f"{family}-post-merge-clean-checkout-validation.json"),
                "entry_count": len(pm_entries),
            }
        )

    # --- 2. Overlay based on mode ---
    if inventory_mode == "repo_actual":
        # Also scan ALL pr-dry-run packages for this family to find any
        # packages that might have been merged but not reflected in post-merge
        pr_dir = repo_root / "workspace" / "pr-dry-run"
        if pr_dir.exists():
            for pkg_dir in sorted(pr_dir.iterdir()):
                if pkg_dir.is_dir() and pkg_dir.name.startswith(f"{family}-"):
                    pkg_entries = _scan_package_examples(family, pkg_dir)
                    trail.sources_scanned.append(
                        {
                            "source_type": "pr_package",
                            "path": str(pkg_dir),
                            "entry_count": len(pkg_entries),
                        }
                    )
                    # Only add to base if not already present (post-merge wins)
                    for e in pkg_entries:
                        if e.name not in base_entries:
                            base_entries[e.name] = e
                            trail.dedup_log.append(f"{e.name}: added from {pkg_dir.name} (not in repo_actual base)")
                        else:
                            # Preserve package_path for fact extraction
                            existing = base_entries[e.name]
                            if not existing.package_path and e.package_path:
                                existing.package_path = e.package_path
                                existing.has_program_cs = e.has_program_cs
                                trail.dedup_log.append(f"{e.name}: package_path enriched from {pkg_dir.name}")

    elif inventory_mode == "current_package_overlay":
        if current_package_path is None:
            raise ValueError("current_package_path required for current_package_overlay mode")
        pkg_entries = _scan_package_examples(family, current_package_path)
        trail.sources_scanned.append(
            {
                "source_type": "current_package",
                "path": str(current_package_path),
                "entry_count": len(pkg_entries),
            }
        )
        for e in pkg_entries:
            if e.name in base_entries:
                trail.conflicts.append(
                    {
                        "example": e.name,
                        "existing_source": base_entries[e.name].source_type,
                        "new_source": "current_package",
                        "resolution": "current_package wins (fresher)",
                    }
                )
            base_entries[e.name] = e

    elif inventory_mode == "batch_overlay":
        paths = batch_package_paths or []
        for pkg_path in paths:
            pkg_entries = _scan_package_examples(family, pkg_path)
            trail.sources_scanned.append(
                {
                    "source_type": "batch_package",
                    "path": str(pkg_path),
                    "entry_count": len(pkg_entries),
                }
            )
            for e in pkg_entries:
                if e.name in base_entries and base_entries[e.name].source_type != "pr_package":
                    trail.conflicts.append(
                        {
                            "example": e.name,
                            "existing_source": base_entries[e.name].source_type,
                            "new_source": f"batch:{pkg_path.name}",
                            "resolution": "batch package wins",
                        }
                    )
                base_entries[e.name] = e

    result = sorted(base_entries.values(), key=lambda e: e.name)
    return result, trail


def build_cumulative_examples_meta(
    entries: list[InventoryEntry],
) -> list[dict]:
    """Convert inventory entries to the format expected by build_readme_context()."""
    return [{"name": e.name, "output_format": e.output_format} for e in entries]


def build_package_path_map(
    entries: list[InventoryEntry],
) -> dict[str, Path]:
    """Build a map of example_name -> package_path for multi-package fact extraction."""
    result: dict[str, Path] = {}
    for e in entries:
        if e.package_path:
            result[e.name] = Path(e.package_path)
    return result


def inventory_to_json(
    entries: list[InventoryEntry],
    trail: InventoryAuditTrail,
) -> str:
    """Serialize inventory and audit trail to JSON."""
    return json.dumps(
        {
            "inventory": [asdict(e) for e in entries],
            "audit_trail": asdict(trail),
        },
        indent=2,
    )
