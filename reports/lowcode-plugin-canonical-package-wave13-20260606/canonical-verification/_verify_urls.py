"""
Wave 13 Lane C: HTTP verification of 22 MISSING_CANONICAL_URL entries.
Run: C:/Python313/python.exe -X utf8 reports/lowcode-plugin-canonical-package-wave13-20260606/canonical-verification/_verify_urls.py
"""
import json
import pathlib
import urllib.request
import urllib.error
import time

SPRINT = "lowcode-plugin-canonical-package-wave13-20260606"
ROOT = pathlib.Path(__file__).parents[3]
OUT = pathlib.Path(__file__).parent / "url-verification-results.json"

# Product page markers that indicate a genuine Aspose products page
PRODUCT_MARKERS = [
    "products.aspose",
    "Aspose",
    "aspose.net",
]

CANDIDATES = [
    {"family": "barcode", "slug": "read-barcode", "candidate_url": "https://products.aspose.net/barcode/read-barcode/"},
    {"family": "cad", "slug": "convert-cad-to-pdf", "candidate_url": "https://products.aspose.net/cad/convert-cad-to-pdf/"},
    {"family": "cad", "slug": "convert-dwg-to-pdf", "candidate_url": "https://products.aspose.net/cad/convert-dwg-to-pdf/"},
    {"family": "cad", "slug": "convert-dxf-to-pdf", "candidate_url": "https://products.aspose.net/cad/convert-dxf-to-pdf/"},
    {"family": "cad", "slug": "convert-cad-to-image", "candidate_url": "https://products.aspose.net/cad/convert-cad-to-image/"},
    {"family": "cad", "slug": "convert-dwg-to-jpg", "candidate_url": "https://products.aspose.net/cad/convert-dwg-to-jpg/"},
    {"family": "finance", "slug": "parse-xbrl", "candidate_url": "https://products.aspose.net/finance/parse-xbrl/"},
    {"family": "font", "slug": "convert-font", "candidate_url": "https://products.aspose.net/font/convert-font/"},
    {"family": "font", "slug": "render-text-with-font", "candidate_url": "https://products.aspose.net/font/render-text-with-font/"},
    {"family": "gis", "slug": "convert-gis-data", "candidate_url": "https://products.aspose.net/gis/convert-gis-data/"},
    {"family": "gis", "slug": "read-gis-data", "candidate_url": "https://products.aspose.net/gis/read-gis-data/"},
    {"family": "html", "slug": "convert-html-to-xps", "candidate_url": "https://products.aspose.net/html/convert-html-to-xps/"},
    {"family": "html", "slug": "convert-html-to-markdown", "candidate_url": "https://products.aspose.net/html/convert-html-to-markdown/"},
    {"family": "html", "slug": "merge-html", "candidate_url": "https://products.aspose.net/html/merge-html/"},
    {"family": "omr", "slug": "recognize-omr", "candidate_url": "https://products.aspose.net/omr/recognize-omr/"},
    {"family": "omr", "slug": "generate-omr-template", "candidate_url": "https://products.aspose.net/omr/generate-omr-template/"},
    {"family": "psd", "slug": "convert-psd-to-png", "candidate_url": "https://products.aspose.net/psd/convert-psd-to-png/"},
    {"family": "svg", "slug": "merge-svg", "candidate_url": "https://products.aspose.net/svg/merge-svg/"},
    {"family": "tasks", "slug": "read-project-data", "candidate_url": "https://products.aspose.net/tasks/read-project-data/"},
    {"family": "tex", "slug": "convert-latex-to-pdf", "candidate_url": "https://products.aspose.net/tex/convert-latex-to-pdf/"},
    {"family": "threed", "slug": "convert-3d-model", "candidate_url": "https://products.aspose.net/3d/convert-3d-model/"},
    {"family": "threed", "slug": "compress-3d-scene", "candidate_url": "https://products.aspose.net/3d/compress-3d-scene/"},
]


def verify_url(url: str) -> dict:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Aspose-LowCode-Verifier/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            final_url = resp.url
            content = resp.read(4096).decode("utf-8", errors="replace")
            has_marker = any(m in content for m in PRODUCT_MARKERS)
            return {
                "http_status": status,
                "final_url": final_url,
                "redirected": final_url.rstrip("/") != url.rstrip("/"),
                "product_markers_found": has_marker,
                "verified": status == 200 and has_marker,
            }
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "final_url": url, "redirected": False, "product_markers_found": False, "verified": False, "error": str(e)}
    except Exception as e:
        return {"http_status": None, "final_url": url, "redirected": False, "product_markers_found": False, "verified": False, "error": str(e)}


results = []
verified_count = 0

for entry in CANDIDATES:
    url = entry["candidate_url"]
    print(f"Checking {entry['family']}/{entry['slug']}... ", end="", flush=True)
    result = verify_url(url)
    status_str = "VERIFIED" if result["verified"] else f"FAIL({result.get('http_status', 'ERR')})"
    print(status_str)
    if result["verified"]:
        verified_count += 1
    results.append({
        "family": entry["family"],
        "slug": entry["slug"],
        "candidate_url": url,
        **result,
        "verification_status": "CANONICAL_IDENTITY_VERIFIED" if result["verified"] else "MISSING_CANONICAL_URL",
    })
    time.sleep(0.3)  # polite delay

output = {
    "sprint": SPRINT,
    "lane": "C",
    "date": "2026-06-06",
    "method": "HTTP_GET_VERIFICATION",
    "total_checked": len(CANDIDATES),
    "verified_count": verified_count,
    "unverified_count": len(CANDIDATES) - verified_count,
    "hit_rate": f"{verified_count}/{len(CANDIDATES)}",
    "entries": results,
    "verdict": "URL_VERIFICATION_COMPLETE",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
print(f"\nVerified: {verified_count}/{len(CANDIDATES)}")
print(f"Results written to: {OUT}")
