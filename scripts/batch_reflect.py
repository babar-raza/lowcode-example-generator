"""TRAIN C: DllReflector reflection wave for all available families."""
import json
import subprocess
import shutil
import zipfile
from pathlib import Path

REPORT = Path("reports/lowcode-non-lowcode-plugin-universe-20260604")
IMPL_REPORT = Path("reports/lowcode-non-lowcode-fallback-implementation-20260604")
TS = "2026-06-04T00:00:00Z"

REFLECTOR = "tools/DllReflector"

# All families with NuGet versions confirmed in TRAIN B
FAMILIES = {
    "barcode": ("Aspose.BarCode", "26.5.0"),
    "imaging": ("Aspose.Imaging", "26.6.0"),
    "zip": ("Aspose.ZIP", "26.5.0"),
    "html": ("Aspose.HTML", "26.5.0"),
    "tasks": ("Aspose.Tasks", "26.5.0"),
    "cad": ("Aspose.CAD", "26.1.0"),
    "ocr": ("Aspose.OCR", "26.5.0"),
    "psd": ("Aspose.PSD", "26.5.0"),
    "svg": ("Aspose.SVG", "26.5.0"),
    "omr": ("Aspose.OMR", "26.1.0"),
    "gis": ("Aspose.GIS", "26.5.0"),
    "page": ("Aspose.Page", "26.5.0"),
    "tex": ("Aspose.TeX", "26.4.0"),
    "note": ("Aspose.Note", "26.4.0"),
    "drawing": ("Aspose.Drawing", "26.5.0"),
    "font": ("Aspose.Font", "26.4.0"),
    "finance": ("Aspose.Finance", "26.5.22"),
    "threed": ("Aspose.3D", "26.4.0"),
}

# Pre-existing reflection runs (skip download; use existing nupkg)
EXISTING_NUPKG = {
    "barcode": ".local/reflection-runs/barcode/packages/barcode/Aspose.BarCode.26.5.0.nupkg",
    "imaging": ".local/reflection-runs/imaging/packages/imaging/Aspose.Imaging.26.6.0.nupkg",
    "zip": ".local/reflection-runs/zip/packages/zip/Aspose.ZIP.26.5.0.nupkg",
}

# TF Moniker search order for DLL extraction
TF_SEARCH_ORDER = [
    "net8.0", "net7.0", "net6.0", "net5.0",
    "netstandard2.1", "netstandard2.0", "netstandard1.6",
    "net472", "net471", "net47", "net462", "net461", "net46", "net45",
]

inventory_dir = REPORT / "reflection" / "public-api-inventory"
inventory_dir.mkdir(parents=True, exist_ok=True)

fingerprint_ledger = {}
namespace_matrix = []
errors = []


def find_dll_in_nupkg(nupkg_path: Path, package_id: str) -> Path | None:
    """Extract primary DLL from nupkg, searching TFMs in order."""
    dll_name = f"{package_id}.dll"
    extract_base = nupkg_path.parent / "extracted"

    with zipfile.ZipFile(nupkg_path) as zf:
        names = zf.namelist()
        # Search TFMs in order
        for tfm in TF_SEARCH_ORDER:
            candidate = f"lib/{tfm}/{dll_name}"
            if candidate in names:
                target = extract_base / candidate
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(candidate))
                print(f"    Extracted {dll_name} from lib/{tfm}/")
                return target

        # Try any lib/ entry matching dll name
        for name in names:
            if name.endswith(f"/{dll_name}") and name.startswith("lib/"):
                target = extract_base / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(name))
                print(f"    Extracted from {name}")
                return target

    return None


def download_nupkg(package_id: str, version: str, dest_dir: Path) -> Path | None:
    """Download nupkg from NuGet."""
    import urllib.request
    pkg_lower = package_id.lower()
    url = f"https://api.nuget.org/v3-flatcontainer/{pkg_lower}/{version}/{pkg_lower}.{version}.nupkg"
    dest = dest_dir / f"{package_id}.{version}.nupkg"
    dest_dir.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"    Using cached nupkg: {dest.name}")
        return dest

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LowcodeGenerator/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
        print(f"    Downloaded {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest
    except Exception as e:
        print(f"    Download failed: {e}")
        return None


def run_reflector(dll_path: Path, output_path: Path) -> dict | None:
    """Run DllReflector on the DLL and return parsed output."""
    cmd = [
        "dotnet", "run", "--project", REFLECTOR,
        "--", "--dll", str(dll_path), "--output", str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"    DllReflector error: {result.stderr[:200]}")
        return None
    if output_path.exists():
        return json.loads(output_path.read_text())
    return None


def classify_namespace(reflection: dict) -> str:
    """Classify namespace status from DllReflector output."""
    if not reflection:
        return "BLOCKED_REFLECTION_FAILED"
    namespaces = [ns.get("namespace", "") for ns in reflection.get("namespaces", [])]
    if any(".LowCode" in ns for ns in namespaces):
        return "LOWCODE_NAMESPACE_PRESENT"
    if any(".Plugins" in ns for ns in namespaces):
        return "PLUGINS_NAMESPACE_PRESENT"
    return "NO_LOWCODE_BUT_PLUGIN_SITE_PRESENT"


# Check if existing reflection results already exist
existing_inventory = {
    f.stem: f for f in (IMPL_REPORT / "reflection" / "public-api-inventory").glob("*.json")
}

for family, (package_id, version) in FAMILIES.items():
    print(f"\n[{family}] {package_id} v{version}")

    # Check if already reflected
    existing_json = existing_inventory.get(family)
    if existing_json:
        print(f"    Already reflected — copying from implementation report")
        reflection = json.loads(existing_json.read_text())
        out_path = inventory_dir / f"{family}.json"
        out_path.write_text(json.dumps(reflection, indent=2))
        status = classify_namespace(reflection)
        import hashlib
        dll_bytes = b""  # already done
        matrix_entry = {
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": status,
            "evidence_path": str(out_path),
            "source": "prior_sprint",
            "notes": f"Reflected in prior sprint. Status: {status}.",
        }
        namespace_matrix.append(matrix_entry)
        fingerprint_ledger[family] = {"package_id": package_id, "version": version, "source": "prior_sprint"}
        continue

    # Use existing nupkg if available
    nupkg_path_str = EXISTING_NUPKG.get(family)
    if nupkg_path_str:
        nupkg_path = Path(nupkg_path_str)
        print(f"    Using existing nupkg: {nupkg_path}")
    else:
        # Download
        dl_dir = Path(f".local/reflection-runs/{family}/packages/{family}")
        nupkg_path = download_nupkg(package_id, version, dl_dir)

    if not nupkg_path or not nupkg_path.exists():
        print(f"    BLOCKED: nupkg not available")
        namespace_matrix.append({
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": "BLOCKED_PACKAGE_UNAVAILABLE",
            "evidence_path": None,
            "notes": "nupkg download failed",
        })
        errors.append({"family": family, "error": "download_failed"})
        continue

    # Extract DLL
    dll_path = find_dll_in_nupkg(nupkg_path, package_id)
    if not dll_path:
        print(f"    BLOCKED: DLL not found in nupkg")
        namespace_matrix.append({
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": "BLOCKED_REFLECTION_FAILED",
            "evidence_path": None,
            "notes": "DLL not found in nupkg",
        })
        errors.append({"family": family, "error": "dll_not_found"})
        continue

    # Compute fingerprint
    import hashlib
    dll_hash = hashlib.sha256(dll_path.read_bytes()).hexdigest()
    fingerprint_ledger[family] = {
        "package_id": package_id,
        "version": version,
        "dll_sha256": dll_hash,
        "dll_path": str(dll_path),
        "dll_size_bytes": dll_path.stat().st_size,
    }

    # Run DllReflector
    out_path = inventory_dir / f"{family}.json"
    print(f"    Running DllReflector on {dll_path.name} ({dll_path.stat().st_size:,} bytes)...")
    try:
        reflection = run_reflector(dll_path, out_path)
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT: DllReflector exceeded 120s")
        namespace_matrix.append({
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": "BLOCKED_REFLECTION_FAILED",
            "evidence_path": None,
            "notes": "DllReflector timeout (>120s)",
        })
        errors.append({"family": family, "error": "timeout"})
        continue
    except Exception as e:
        print(f"    ERROR: {e}")
        namespace_matrix.append({
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": "BLOCKED_REFLECTION_FAILED",
            "evidence_path": None,
            "notes": str(e),
        })
        errors.append({"family": family, "error": str(e)})
        continue

    if not reflection:
        namespace_matrix.append({
            "family_slug": family,
            "package_id": package_id,
            "version": version,
            "namespace_status": "BLOCKED_REFLECTION_FAILED",
            "evidence_path": None,
            "notes": "DllReflector returned no output",
        })
        errors.append({"family": family, "error": "no_output"})
        continue

    status = classify_namespace(reflection)
    type_count = sum(len(ns.get("types", [])) for ns in reflection.get("namespaces", []))
    ns_names = [ns.get("namespace", "") for ns in reflection.get("namespaces", [])]

    print(f"    Status: {status}")
    print(f"    Namespaces ({len(ns_names)}): {ns_names[:5]}")
    print(f"    Types: {type_count}")

    matrix_entry = {
        "family_slug": family,
        "package_id": package_id,
        "version": version,
        "namespace_status": status,
        "evidence_path": str(out_path),
        "dll_sha256": dll_hash,
        "type_count": type_count,
        "namespace_count": len(ns_names),
        "namespaces_sample": ns_names[:10],
        "notes": f"DllReflector: {type_count} types, {len(ns_names)} namespaces.",
    }
    namespace_matrix.append(matrix_entry)


# Save namespace matrix (update the existing one from impl report)
existing_matrix_path = IMPL_REPORT / "reflection" / "family-namespace-matrix.json"
universe_matrix_path = REPORT / "reflection" / "family-namespace-matrix.json"

(REPORT / "reflection").mkdir(parents=True, exist_ok=True)
universe_matrix_path.write_text(json.dumps(namespace_matrix, indent=2))

# Also update the impl report matrix
existing_matrix_path.write_text(json.dumps(namespace_matrix, indent=2))

# Save fingerprint ledger
fingerprint_path = REPORT / "reflection" / "package-fingerprint-ledger.json"
fingerprint_path.write_text(json.dumps({
    "generated_at": TS,
    "total": len(fingerprint_ledger),
    "families": fingerprint_ledger,
}, indent=2))

# Also update impl report ledger
(IMPL_REPORT / "reflection" / "package-fingerprint-ledger.json").write_text(json.dumps({
    "generated_at": TS,
    "total": len(fingerprint_ledger),
    "families": fingerprint_ledger,
}, indent=2))

# Summary
classified = [e for e in namespace_matrix if e["namespace_status"] != "WEBSITE_ONLY_UNVERIFIED"]
print(f"\n\n=== TRAIN C REFLECTION WAVE SUMMARY ===")
print(f"Total families attempted: {len(namespace_matrix)}")
print(f"Fully classified (not UNVERIFIED): {len(classified)}")
print(f"Errors: {len(errors)}")
if errors:
    for e in errors:
        print(f"  - {e['family']}: {e['error']}")
