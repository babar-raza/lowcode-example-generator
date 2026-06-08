"""Drift detection for website catalog pages."""

from __future__ import annotations

import hashlib


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
