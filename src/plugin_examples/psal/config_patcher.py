"""Config patcher — create runnable ephemeral configs for disabled families.

Never modifies original config files. Writes patched copies to
.local/psal/configs/{family}.yml with enabled=true, status=discovery_only.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_runnable_config(family: str, repo_root: Path) -> Path:
    """Return a runnable config path for the family.

    If the original config is already enabled, returns the original path.
    Otherwise, creates a patched ephemeral copy with enabled=true and
    status=discovery_only.

    Args:
        family: Family slug (e.g. "drawing").
        repo_root: Repository root path.

    Returns:
        Path to a runnable config YAML (original or patched copy).
    """
    import yaml

    original = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
    if not original.exists():
        logger.warning("No config file for family %s", family)
        return original

    with open(original, encoding="utf-8") as fh:
        data = yaml.safe_load(fh.read()) or {}

    if data.get("enabled", False):
        return original

    # Patch: enable the family for PSAL execution
    data["enabled"] = True
    if data.get("status") in ("disabled", None):
        data["status"] = "discovery_only"

    # Ensure fallback_strategy is set for non-LowCode detection
    plugin_detection = data.get("plugin_detection", {})
    if not plugin_detection.get("fallback_strategy"):
        plugin_detection["fallback_strategy"] = "capability_registry"
        data["plugin_detection"] = plugin_detection

    patched_dir = repo_root / ".local" / "psal" / "configs"
    patched_dir.mkdir(parents=True, exist_ok=True)
    patched_path = patched_dir / f"{family}.yml"

    with open(patched_path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)

    logger.info("Created patched config for %s at %s", family, patched_path)
    return patched_path
