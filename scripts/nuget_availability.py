"""TRAIN B: NuGet availability matrix for all 20 families."""
import urllib.request
import json
from pathlib import Path

REPORT = Path("reports/lowcode-non-lowcode-plugin-universe-20260604")
TS = "2026-06-04T00:00:00Z"

PACKAGE_ALIASES = {
    "barcode": "Aspose.BarCode",
    "imaging": "Aspose.Imaging",
    "zip": "Aspose.ZIP",
    "html": "Aspose.HTML",
    "cad": "Aspose.CAD",
    "ocr": "Aspose.OCR",
    "psd": "Aspose.PSD",
    "svg": "Aspose.SVG",
    "omr": "Aspose.OMR",
    "gis": "Aspose.GIS",
    "page": "Aspose.Page",
    "tex": "Aspose.TeX",
    "tasks": "Aspose.Tasks",
    "note": "Aspose.Note",
    "drawing": "Aspose.Drawing",
    "font": "Aspose.Font",
    "finance": "Aspose.Finance",
    "threed": "Aspose.3D",
    "epub": "Aspose.HTML",
    "medical": "Aspose.Medical",
}

NUGET_BASE = "https://api.nuget.org/v3-flatcontainer/{}/index.json"

results = {}
for family, package_id in PACKAGE_ALIASES.items():
    url = NUGET_BASE.format(package_id.lower())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LowcodeGenerator/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            versions = data.get("versions", [])
            # Filter to stable versions (no pre-release)
            stable = [v for v in versions if "-" not in v]
            latest_stable = stable[-1] if stable else (versions[-1] if versions else None)
            results[family] = {
                "package_id": package_id,
                "available": True,
                "latest_stable_version": latest_stable,
                "total_versions": len(versions),
                "http_status": 200,
                "nuget_url": url,
                "namespace_status": "AVAILABLE",
                "blocker_status": None,
            }
            print(f"  OK  {family:12} {package_id:20} v{latest_stable}")
    except urllib.error.HTTPError as e:
        status = e.code
        results[family] = {
            "package_id": package_id,
            "available": False,
            "latest_stable_version": None,
            "total_versions": 0,
            "http_status": status,
            "nuget_url": url,
            "namespace_status": "BLOCKED_PACKAGE_UNAVAILABLE" if status == 404 else "BLOCKED_HTTP_ERROR",
            "blocker_status": "BLOCKED_PACKAGE_UNAVAILABLE" if status == 404 else f"HTTP_{status}",
        }
        print(f"  {status}  {family:12} {package_id:20} — BLOCKED")
    except Exception as e:
        results[family] = {
            "package_id": package_id,
            "available": False,
            "latest_stable_version": None,
            "total_versions": 0,
            "http_status": None,
            "nuget_url": url,
            "namespace_status": "BLOCKED_NETWORK_ERROR",
            "blocker_status": f"NETWORK_ERROR: {e}",
        }
        print(f"  ERR {family:12} {package_id:20} — {e}")

available = [f for f, r in results.items() if r["available"]]
blocked = [f for f, r in results.items() if not r["available"]]

output = {
    "generated_at": TS,
    "total_families": len(results),
    "available_count": len(available),
    "blocked_count": len(blocked),
    "available_families": sorted(available),
    "blocked_families": sorted(blocked),
    "families": results,
}

(REPORT / "universe/nuget-availability-matrix.json").write_text(json.dumps(output, indent=2))
print(f"\nAvailable: {len(available)}/{len(results)} families")
print(f"Blocked: {blocked}")
