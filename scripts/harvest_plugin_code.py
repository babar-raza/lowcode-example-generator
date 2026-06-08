"""Harvest official source code for each plugin from GitHub repos.

For each plugin page URL, finds the best matching C# example from the
official Aspose GitHub repository and fetches the raw source code.
"""
import json, re, hashlib, time, urllib.request
from pathlib import Path

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

FAMILY_REPOS = {
    'barcode': 'aspose-barcode/Aspose.BarCode-for-.NET',
    'imaging': 'aspose-imaging/Aspose.Imaging-for-.NET',
    'zip': 'aspose-zip/Aspose.ZIP-for-.NET',
    'html': 'aspose-html/Aspose.HTML-for-.NET',
    'tasks': 'aspose-tasks/Aspose.Tasks-for-.NET',
    'cad': 'aspose-cad/Aspose.CAD-for-.NET',
    'ocr': 'aspose-ocr/Aspose.OCR-for-.NET',
    'psd': 'aspose-psd/Aspose.PSD-for-.NET',
    'svg': 'aspose-svg/Aspose.SVG-for-.NET',
    'page': 'aspose-page/Aspose.Page-for-.NET',
    'tex': 'aspose-tex/Aspose.TeX-for-.NET',
    'note': 'aspose-note/Aspose.Note-for-.NET',
    'drawing': 'aspose-drawing/Aspose.Drawing-for-.NET',
    'font': 'aspose-font/Aspose.Font-for-.NET',
    'finance': 'aspose-finance/Aspose.Finance-for-.NET',
    'threed': 'aspose-3d/Aspose.3D-for-.NET',
    'gis': 'aspose-gis/Aspose.GIS-for-.NET',
    'omr': 'aspose-omr/Aspose.OMR-for-.NET',
}

code_cache = Path('.local/code-cache')
source_map_path = code_cache / 'plugin-source-map.json'

with open(source_map_path) as f:
    source_map = json.load(f)

harvest_results = []
symbol_inventory = []

def extract_symbols(code: str) -> dict:
    """Extract C# API symbols from code text."""
    namespaces = re.findall(r'^using (Aspose\.[^;]+);', code, re.MULTILINE)
    classes = re.findall(r'new (\w+)\s*[(<]', code)
    classes += re.findall(r'(\w+)\.(?:Load|Open|Create|Save|Process|Generate|Recognize|Convert|Export|Initialize)\b', code)
    methods = re.findall(r'\.(\w+)\s*\(', code)
    enums = re.findall(r'(\w+\.\w+)\b(?:\s*[,;)])', code)
    # Filter to likely Aspose types
    aspose_classes = [c for c in set(classes) if c[0].isupper() and len(c) > 3]
    return {
        'namespaces': list(set(namespaces)),
        'classes': aspose_classes[:15],
        'methods': list(set(methods))[:20],
    }

for family, plugins in sorted(source_map.items()):
    repo = FAMILY_REPOS.get(family, '')
    for plugin, paths in plugins.items():
        if not paths:
            harvest_results.append({
                'family': family,
                'plugin_slug': plugin,
                'plugin_url': f'https://products.aspose.net/{family}/net/{plugin}',
                'source_type': 'NO_CODE_FOUND',
                'fetch_status': 'NO_MATCH',
                'github_url': f'https://github.com/{repo}',
            })
            continue

        # Try to fetch the first matching file
        best_path = paths[0]
        raw_url = f'https://raw.githubusercontent.com/{repo}/master/{best_path}'

        req = urllib.request.Request(raw_url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                code_text = r.read().decode('utf-8', errors='replace')
            code_hash = hashlib.sha256(code_text.encode('utf-8')).hexdigest()

            # Save to cache
            cache_dir = code_cache / family / plugin
            cache_dir.mkdir(parents=True, exist_ok=True)
            filename = Path(best_path).name
            cache_file = cache_dir / filename
            cache_file.write_text(code_text, encoding='utf-8')

            symbols = extract_symbols(code_text)

            result = {
                'family': family,
                'plugin_slug': plugin,
                'plugin_url': f'https://products.aspose.net/{family}/net/{plugin}',
                'source_type': 'github_file',
                'github_repo': f'https://github.com/{repo}',
                'github_path': best_path,
                'raw_url': raw_url,
                'filename': filename,
                'language': 'csharp',
                'code_text_path': str(cache_file),
                'code_hash': code_hash,
                'code_length': len(code_text),
                'last_fetched': '2026-06-04',
                'fetch_status': 'OK',
                'fetch_error': None,
            }
            harvest_results.append(result)

            sym_entry = {
                'family': family,
                'plugin_slug': plugin,
                'source_type': 'github_file',
                'raw_url': raw_url,
                'code_hash': code_hash,
                **symbols
            }
            symbol_inventory.append(sym_entry)

            print(f'OK: {family}/{plugin} -> {filename} ({len(code_text)} bytes, hash={code_hash[:12]})')

        except Exception as e:
            harvest_results.append({
                'family': family,
                'plugin_slug': plugin,
                'plugin_url': f'https://products.aspose.net/{family}/net/{plugin}',
                'source_type': 'github_file',
                'github_repo': f'https://github.com/{repo}',
                'github_path': best_path,
                'raw_url': raw_url,
                'fetch_status': 'CODE_FETCH_FAILED',
                'fetch_error': str(e)[:100],
            })
            print(f'FAIL: {family}/{plugin} -> {e}')
        time.sleep(0.2)

# Build availability matrix
by_status = {}
for r in harvest_results:
    s = r.get('fetch_status', 'UNKNOWN')
    by_status[s] = by_status.get(s, 0) + 1

# Save outputs
report_dir = Path('reports/lowcode-plugin-code-registry-20260604/code-harvest')
report_dir.mkdir(parents=True, exist_ok=True)

# Source link inventory
source_links = [r for r in harvest_results if r.get('fetch_status') == 'OK']
(report_dir / 'source-link-inventory.json').write_text(json.dumps({
    'generated_at': '2026-06-04',
    'source_type': 'github_repository',
    'total': len(source_links),
    'entries': source_links
}, indent=2))

# Code symbol inventory
(report_dir / 'code-symbol-inventory.json').write_text(json.dumps({
    'generated_at': '2026-06-04',
    'total': len(symbol_inventory),
    'entries': symbol_inventory
}, indent=2))

# Full harvest results
(report_dir / 'raw-code-cache-manifest.json').write_text(json.dumps({
    'generated_at': '2026-06-04',
    'total': len(harvest_results),
    'by_status': by_status,
    'entries': harvest_results
}, indent=2))

# Availability matrix
family_status = {}
for r in harvest_results:
    fam = r['family']
    plugin = r['plugin_slug']
    status = r.get('fetch_status', 'UNKNOWN')
    if fam not in family_status:
        family_status[fam] = {}
    # Map fetch status to code availability status
    if status == 'OK':
        avail = 'CODE_FOUND_REPOSITORY'
    elif status == 'NO_MATCH':
        avail = 'NO_CODE_FOUND'
    else:
        avail = 'CODE_FETCH_FAILED'
    family_status[fam][plugin] = avail

(report_dir / 'plugin-code-availability-matrix.json').write_text(json.dumps({
    'generated_at': '2026-06-04',
    'by_family': family_status
}, indent=2))

print(f'\n=== Harvest Summary ===')
print(f'Total plugins: {len(harvest_results)}')
for s, count in sorted(by_status.items()):
    print(f'  {s}: {count}')
print(f'\nOutputs written to {report_dir}')
