"""Write example index and generation manifests."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def write_example_index(
    examples: list[dict],
    manifests_dir: Path,
) -> Path:
    """Write example index to manifests directory.

    Args:
        examples: List of generated example metadata dicts.
        manifests_dir: Path to manifests directory.

    Returns:
        Path to written index file.
    """
    manifests_dir.mkdir(parents=True, exist_ok=True)
    path = manifests_dir / "example-index.json"

    data = {
        "total_examples": len(examples),
        "generated": len([e for e in examples if e.get("status") == "generated"]),
        "repaired": len([e for e in examples if e.get("status") == "repaired"]),
        "failed": len([e for e in examples if e.get("status") == "failed"]),
        "examples": examples,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Example index written: %s (%d examples)", path, len(examples))
    return path
