"""Website catalog crawler for products.aspose.net plugin pages.

Discovery only — never treats catalog as API authority.
All returned PluginEntry objects have marketing_only=True.
"""

from __future__ import annotations

import logging
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from plugin_examples.website_catalog.drift_detector import compute_page_hash
from plugin_examples.website_catalog.models import CatalogResult, PluginEntry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CACHE_BASE = Path(".local") / "catalog-cache"
_CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days
_DEFAULT_DELAY_MS = 1000  # 1 second between requests

_LOCALE_PATTERN = re.compile(
    r"/(en|de|fr|es|zh|ja|ru|pt|it)(/|$)",
    re.IGNORECASE,
)

_RETRY_STATUS_CODES = {429, 503}
_BACKOFF_SECONDS = [1, 2, 4]


# ---------------------------------------------------------------------------
# URL normalisation
# ---------------------------------------------------------------------------


def normalize_url(url: str) -> str:
    """Strip locale path segments from a URL.

    e.g. https://products.aspose.net/en/barcode → https://products.aspose.net/barcode
    """
    return _LOCALE_PATTERN.sub(r"\2", url)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _cache_path(family: str, slug: str) -> Path:
    return _CACHE_BASE / family / f"{slug}.html"


def _is_cache_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < _CACHE_TTL_SECONDS


def _read_cache(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_cache(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# HTTP fetch with retry
# ---------------------------------------------------------------------------


def _fetch_url(url: str) -> str | None:
    """Fetch URL with retry on 429/503. Returns HTML content or None on failure."""
    for attempt, backoff in enumerate([0] + _BACKOFF_SECONDS):
        if attempt > 0:
            time.sleep(backoff)
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "LowcodeGenerator-CatalogCrawler/1.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_STATUS_CODES and attempt < len(_BACKOFF_SECONDS):
                logger.warning("HTTP %d for %s — retrying (attempt %d)", e.code, url, attempt + 1)
                continue
            logger.warning("HTTP %d for %s — not retrying", e.code, url)
            return None
        except Exception as e:
            logger.warning("Fetch error for %s: %s", url, e)
            return None
    return None


# ---------------------------------------------------------------------------
# Crawler
# ---------------------------------------------------------------------------


class WebsiteCatalog:
    """Crawls plugin product pages for a given Aspose family.

    All entries are marked marketing_only=True.
    Use --replay mode to read from cache without making HTTP calls.
    """

    def __init__(self, *, replay: bool = False) -> None:
        self.replay = replay

    def crawl_family(self, family: str, urls: list[str]) -> CatalogResult:
        """Crawl product pages for a family and return PluginEntry objects.

        Args:
            family: Family slug (e.g. "barcode").
            urls: List of product page URLs to crawl.
        """
        delay_ms = int(os.environ.get("CATALOG_CRAWL_DELAY_MS", _DEFAULT_DELAY_MS))
        delay_s = delay_ms / 1000.0

        entries: list[PluginEntry] = []
        errors: list[str] = []
        from_cache = True

        for url in urls:
            normalized = normalize_url(url)
            slug = _url_to_slug(normalized)
            cache_file = _cache_path(family, slug)

            if self.replay:
                if cache_file.exists():
                    content = _read_cache(cache_file)
                else:
                    errors.append(f"Replay: no cache for {url}")
                    continue
            elif _is_cache_fresh(cache_file):
                content = _read_cache(cache_file)
            else:
                from_cache = False
                time.sleep(delay_s)
                content = _fetch_url(normalized)
                if content is None:
                    errors.append(f"Failed to fetch {url}")
                    entries.append(
                        PluginEntry(
                            family=family,
                            plugin_name=slug,
                            url=normalized,
                            slug=slug,
                            page_hash="",
                            marketing_only=True,
                        )
                    )
                    continue
                _write_cache(cache_file, content)

            page_hash = compute_page_hash(content)
            plugin_name = _extract_plugin_name(content, slug)

            entries.append(
                PluginEntry(
                    family=family,
                    plugin_name=plugin_name,
                    url=normalized,
                    slug=slug,
                    page_hash=page_hash,
                    marketing_only=True,
                )
            )

        return CatalogResult(family=family, entries=entries, from_cache=from_cache, errors=errors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug."""
    # Strip protocol and domain, take path segments
    slug = re.sub(r"https?://[^/]+", "", url)
    slug = slug.strip("/").replace("/", "_").replace(".", "_")
    return slug or "index"


def _extract_plugin_name(html: str, fallback: str) -> str:
    """Extract plugin name from page HTML (best-effort; falls back to slug)."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return fallback
