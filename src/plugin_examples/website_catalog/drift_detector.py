"""Drift detection for website catalog pages — Wave 25 Lane C.

Two levels of drift detection:
1. Single-page: ``DriftDetector.detect_drift()`` (original, unchanged)
2. Full-catalog: ``detect_catalog_drift()`` compares a prior evidence JSON
   against a current plugin list, producing a ``DriftReport``.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


def compute_page_hash(content: str | bytes) -> str:
    """Compute a stable SHA-256 hash of page content for drift detection."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


class DriftDetector:
    """Detects when a cached page has changed on the live site."""

    def detect_drift(self, url: str, current_hash: str, cached_hash: str) -> bool:
        """Return True if the live page hash differs from the cached hash.

        Args:
            url: The page URL (used for logging only).
            current_hash: Hash of the freshly fetched page content.
            cached_hash: Hash stored when the page was last cached.
        """
        return current_hash != cached_hash


# ── Catalog-level drift ────────────────────────────────────────────────────────

@dataclass
class DriftReport:
    """Comparison between a prior discovery evidence run and the current catalog."""
    added: list[str]         # new plugin page URLs not in prior run
    removed: list[str]       # URLs that existed in prior run but not current
    changed: list[str]       # URLs where page_hash changed
    unchanged: list[str]     # URLs with matching page_hash
    has_drift: bool
    run_id: str
    compared_against: str    # run_id of prior evidence, or "NONE" if no prior
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "compared_against": self.compared_against,
            "has_drift": self.has_drift,
            "added_count": len(self.added),
            "removed_count": len(self.removed),
            "changed_count": len(self.changed),
            "unchanged_count": len(self.unchanged),
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
        }


def detect_catalog_drift(
    prior_evidence_path: Path | None,
    current_plugins: list[dict],
    run_id: str | None = None,
) -> DriftReport:
    """Compare current plugin list against a prior discovery evidence file.

    Args:
        prior_evidence_path: Path to a prior discovery evidence JSON.
            May be ``None`` if no prior run exists.
        current_plugins: List of dicts with at least ``{"url": str, "page_hash": str}``.
        run_id: Identifier for the current run. Auto-generated if not provided.

    Returns:
        :class:`DriftReport`.
    """
    run_id = run_id or _make_run_id()

    prior_meta_run_id = "NONE"
    prior_hashes: dict[str, str] = {}
    if prior_evidence_path is not None and prior_evidence_path.exists():
        try:
            prior_data = json.loads(prior_evidence_path.read_text(encoding="utf-8"))
            prior_meta_run_id = prior_data.get("discovery_metadata", {}).get("run_id", "NONE")
            for plugin in prior_data.get("plugins", []):
                url = plugin.get("url", "")
                page_hash = plugin.get("page_hash", "")
                if url:
                    prior_hashes[url] = page_hash
        except Exception:
            pass

    current_hashes: dict[str, str] = {
        plugin.get("url", ""): plugin.get("page_hash", "")
        for plugin in current_plugins
        if plugin.get("url")
    }

    added = [u for u in current_hashes if u not in prior_hashes]
    removed = [u for u in prior_hashes if u not in current_hashes]
    changed = [
        u for u, h in current_hashes.items()
        if u in prior_hashes and prior_hashes[u] and h and prior_hashes[u] != h
    ]
    unchanged = [
        u for u in current_hashes
        if u in prior_hashes and prior_hashes.get(u) == current_hashes[u]
    ]

    return DriftReport(
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        has_drift=bool(added or removed or changed),
        run_id=run_id,
        compared_against=prior_meta_run_id,
    )


def make_discovery_metadata(
    run_id: str | None = None,
    ttl_seconds: int = 7 * 24 * 3600,
    catalog_version: str = "1",
) -> dict:
    """Build a ``discovery_metadata`` dict to embed in discovery evidence files."""
    now = datetime.now(timezone.utc)
    run_id = run_id or _make_run_id("discovery")
    expires = now + timedelta(seconds=ttl_seconds)
    return {
        "validated_at": now.isoformat(timespec="seconds"),
        "run_id": run_id,
        "catalog_version": catalog_version,
        "ttl_seconds": ttl_seconds,
        "expires_at": expires.isoformat(timespec="seconds"),
    }


def is_discovery_stale(metadata: dict) -> bool:
    """Return True if the discovery metadata has expired."""
    expires_at = metadata.get("expires_at")
    if not expires_at:
        return True  # no expiry info = treat as stale
    try:
        expires = datetime.fromisoformat(expires_at)
        return expires < datetime.now(timezone.utc)
    except Exception:
        return True


def _make_run_id(prefix: str = "run") -> str:
    now = datetime.now(timezone.utc)
    return f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
