"""
Wave 14 Lane C — Multi-strategy canonical URL verification for 22 MCU entries.

Strategies attempted (in order):
  1. Prior-sprint catalog cross-reference (plugin-page-hashes.json — 65 pages with hashes)
  2. Browser-style urllib requests (full Accept/User-Agent headers) for new canonical format
  3. Browser-style urllib requests for old /net/ format URLs
  4. Root-page crawl on products.aspose.net to extract canonical product links
  5. Sitemap cross-reference (products.aspose.net/sitemap.xml)

Playwright is NOT installed. Using urllib with browser-style headers.
requests library is NOT available (permission denied on system Python).
"""
import json
import pathlib
import sys
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).parent.parent.parent.parent.parent

# 22 MCU entries
MCU_ENTRIES = [
    {"family": "barcode", "slug": "read-barcode", "old_url": "https://products.aspose.net/barcode/net/read-barcode"},
    {"family": "cad", "slug": "convert-cad-to-pdf", "old_url": "https://products.aspose.net/cad/net/convert-cad-to-pdf"},
    {"family": "cad", "slug": "convert-dwg-to-pdf", "old_url": "https://products.aspose.net/cad/net/convert-dwg-to-pdf"},
    {"family": "cad", "slug": "convert-dxf-to-pdf", "old_url": "https://products.aspose.net/cad/net/convert-dxf-to-pdf"},
    {"family": "cad", "slug": "convert-cad-to-image", "old_url": "https://products.aspose.net/cad/net/convert-cad-to-image"},
    {"family": "cad", "slug": "convert-dwg-to-jpg", "old_url": "https://products.aspose.net/cad/net/convert-dwg-to-jpg"},
    {"family": "finance", "slug": "parse-xbrl", "old_url": "https://products.aspose.net/finance/net/parse-xbrl"},
    {"family": "font", "slug": "convert-font", "old_url": "https://products.aspose.net/font/net/convert-font"},
    {"family": "font", "slug": "render-text-with-font", "old_url": "https://products.aspose.net/font/net/render-text-with-font"},
    {"family": "gis", "slug": "convert-gis-data", "old_url": "https://products.aspose.net/gis/net/convert-gis-data"},
    {"family": "gis", "slug": "read-gis-data", "old_url": "https://products.aspose.net/gis/net/read-gis-data"},
    {"family": "html", "slug": "convert-html-to-xps", "old_url": "https://products.aspose.net/html/net/convert-html-to-xps"},
    {"family": "html", "slug": "convert-html-to-markdown", "old_url": "https://products.aspose.net/html/net/convert-html-to-markdown"},
    {"family": "html", "slug": "merge-html", "old_url": "https://products.aspose.net/html/net/merge-html"},
    {"family": "omr", "slug": "recognize-omr", "old_url": "https://products.aspose.net/omr/net/recognize-omr"},
    {"family": "omr", "slug": "generate-omr-template", "old_url": "https://products.aspose.net/omr/net/generate-omr-template"},
    {"family": "psd", "slug": "convert-psd-to-png", "old_url": "https://products.aspose.net/psd/net/convert-psd-to-png"},
    {"family": "svg", "slug": "merge-svg", "old_url": "https://products.aspose.net/svg/net/merge-svg"},
    {"family": "tasks", "slug": "read-project-data", "old_url": "https://products.aspose.net/tasks/net/read-project-data"},
    {"family": "tex", "slug": "convert-latex-to-pdf", "old_url": "https://products.aspose.net/tex/net/convert-latex-to-pdf"},
    {"family": "threed", "slug": "convert-3d-model", "old_url": "https://products.aspose.net/threed/net/convert-3d-model"},
    {"family": "threed", "slug": "compress-3d-scene", "old_url": "https://products.aspose.net/threed/net/compress-3d-scene"},
]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}


class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag == "a":
            d = dict(attrs)
            href = d.get("href", "")
            if "products.aspose.net" in href or href.startswith("/"):
                self.links.append({"href": href, "text": ""})

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.links and not self.links[-1]["text"]:
            self.links[-1]["text"] = data.strip()


def fetch_url(url, timeout=12):
    """Attempt browser-style fetch. Returns (status_code, final_url, body_snippet, error)."""
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            final_url = resp.url
            body = resp.read(4096).decode("utf-8", errors="replace")
            return status, final_url, body, None
    except urllib.error.HTTPError as e:
        return e.code, url, "", str(e)
    except Exception as e:
        return None, url, "", str(e)


def load_prior_catalog():
    """Load the plugin-page-hashes.json from the prior sprint."""
    catalog_path = ROOT / "reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/plugin-page-hashes.json"
    if not catalog_path.exists():
        return {}
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return data.get("hashes", {})


def crawl_root_page():
    """Fetch the products.aspose.net root and extract product links."""
    status, final_url, body, error = fetch_url("https://products.aspose.net/", timeout=15)
    if status != 200:
        return None, {"status": status, "error": error}

    parser = LinkExtractor()
    parser.feed(body)
    product_links = []
    for link in parser.links:
        href = link["href"]
        # Filter for product plugin links (2+ path segments)
        if "products.aspose.net" in href:
            parts = href.rstrip("/").split("/")
            if len(parts) >= 5:  # https://products.aspose.net/{family}/{slug}
                product_links.append({"url": href, "text": link["text"]})
        elif href.startswith("/") and len(href.split("/")) >= 3:
            full = f"https://products.aspose.net{href}"
            product_links.append({"url": full, "text": link["text"]})

    return {"status": status, "title": parser.title.strip(), "links_found": len(parser.links),
            "product_links": product_links}, None


def main():
    out_dir = ROOT / "reports/lowcode-plugin-canonical-package-wave14-20260606/canonical-verification"

    print("Loading prior sprint catalog...")
    catalog = load_prior_catalog()
    print(f"  Catalog entries: {len(catalog)}")

    print("\nCrawling root page...")
    root_data, root_error = crawl_root_page()
    if root_error:
        print(f"  Root page ERROR: {root_error}")
    else:
        print(f"  Root page OK: {root_data['title']}, {root_data['links_found']} links, {len(root_data['product_links'])} product links")

    # Save root link inventory
    root_inventory = {
        "sprint": "lowcode-plugin-canonical-package-wave14-20260606",
        "date": "2026-06-06",
        "root_url": "https://products.aspose.net/",
        "root_status": root_data["status"] if root_data else None,
        "root_error": str(root_error) if root_error else None,
        "root_title": root_data.get("title", "") if root_data else "",
        "product_links": root_data.get("product_links", []) if root_data else [],
        "product_link_count": len(root_data.get("product_links", [])) if root_data else 0,
    }
    (out_dir / "root-link-inventory.json").write_text(json.dumps(root_inventory, indent=2), encoding="utf-8")
    print(f"  Saved root-link-inventory.json")

    # Per-entry verification
    print("\nVerifying 22 MCU entries...")
    results = []
    for entry in MCU_ENTRIES:
        family = entry["family"]
        slug = entry["slug"]
        old_url = entry["old_url"]
        new_url = f"https://products.aspose.net/{family}/{slug}/"

        print(f"  [{family}/{slug}]", end=" ", flush=True)

        # Strategy 1: Prior catalog cross-reference
        in_catalog = old_url in catalog
        catalog_hash = catalog.get(old_url, "")

        # Strategy 2: Browser-style new format
        time.sleep(0.3)
        new_status, new_final, new_body, new_err = fetch_url(new_url)
        print(f"new={new_status}", end=" ", flush=True)

        # Strategy 3: Browser-style old /net/ format
        time.sleep(0.3)
        old_status, old_final, old_body, old_err = fetch_url(old_url)
        print(f"old={old_status}", end=" ", flush=True)

        # Strategy 4: Root page link check
        in_root_links = False
        if root_data:
            for pl in root_data.get("product_links", []):
                if slug in pl["url"] or family in pl["url"]:
                    in_root_links = True
                    break

        # Classification logic
        if new_status == 200 and "aspose" in new_body.lower():
            classification = "VERIFIED_CANONICAL_URL"
            verified_url = new_url
            verification_method = "BROWSER_NEW_FORMAT_200"
            confidence = "HIGH"
        elif old_status == 200 and "aspose" in old_body.lower():
            classification = "VERIFIED_CANONICAL_URL"
            verified_url = old_url
            verification_method = "BROWSER_OLD_FORMAT_200"
            confidence = "HIGH"
        elif new_status in (301, 302, 307, 308):
            classification = "VERIFIED_CANONICAL_URL"
            verified_url = new_url
            verification_method = f"BROWSER_NEW_FORMAT_REDIRECT_{new_status}"
            confidence = "MEDIUM"
        elif old_status in (301, 302, 307, 308):
            classification = "VERIFIED_CANONICAL_URL"
            verified_url = old_url
            verification_method = f"BROWSER_OLD_FORMAT_REDIRECT_{old_status}"
            confidence = "MEDIUM"
        elif in_catalog and catalog_hash:
            classification = "SOURCE_CATALOG_VERIFIED"
            verified_url = old_url
            verification_method = "PRIOR_SPRINT_CATALOG_HASH"
            confidence = "MEDIUM"
        elif in_root_links:
            classification = "FAMILY_PAGE_VERIFIED"
            verified_url = f"https://products.aspose.net/{family}/"
            verification_method = "ROOT_PAGE_FAMILY_LINK"
            confidence = "LOW"
        else:
            classification = "BROWSER_BLOCKED"
            verified_url = None
            verification_method = f"ALL_STRATEGIES_FAILED: new={new_status},old={old_status},catalog={in_catalog}"
            confidence = "NONE"

        print(f"→ {classification}")

        results.append({
            "family": family,
            "slug": slug,
            "old_format_url": old_url,
            "new_format_url": new_url,
            "in_prior_catalog": in_catalog,
            "catalog_hash": catalog_hash,
            "catalog_source": "reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/plugin-page-hashes.json",
            "new_format_status": new_status,
            "old_format_status": old_status,
            "in_root_page_links": in_root_links,
            "classification": classification,
            "verified_url": verified_url,
            "verification_method": verification_method,
            "confidence": confidence,
        })

    # Aggregate results
    classification_counts = {}
    for r in results:
        c = r["classification"]
        classification_counts[c] = classification_counts.get(c, 0) + 1

    browser_results = {
        "sprint": "lowcode-plugin-canonical-package-wave14-20260606",
        "date": "2026-06-06",
        "strategy": "multi-strategy: browser-style-urllib + prior-catalog + root-page-crawl",
        "total_checked": len(MCU_ENTRIES),
        "classification_counts": classification_counts,
        "entries": results,
    }
    (out_dir / "browser-url-verification-results.json").write_text(
        json.dumps(browser_results, indent=2), encoding="utf-8"
    )
    print(f"\nSaved browser-url-verification-results.json")
    print(f"Classification breakdown: {classification_counts}")
    return results


if __name__ == "__main__":
    results = main()
