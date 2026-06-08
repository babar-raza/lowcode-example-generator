"""Generate plugin-code-registry YAML files from harvested code and manual analysis."""
import json
from pathlib import Path

REPORT_DIR = Path('reports/lowcode-plugin-code-registry-20260604')
REGISTRY_DIR = Path('pipeline/plugin-code-registry/family')
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

# Load prior sprint page hashes
with open('reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/plugin-page-hashes.json') as f:
    page_hashes = json.load(f).get('hashes', {})

# Load code harvest results
with open(REPORT_DIR / 'code-harvest/raw-code-cache-manifest.json') as f:
    harvest = json.load(f)

harvest_by_key = {}
for entry in harvest.get('entries', []):
    key = f"{entry['family']}/{entry['plugin_slug']}"
    harvest_by_key[key] = entry

# Load symbol inventory
with open(REPORT_DIR / 'code-harvest/code-symbol-inventory.json') as f:
    symbols_data = json.load(f)

symbols_by_key = {}
for entry in symbols_data.get('entries', []):
    key = f"{entry['family']}/{entry['plugin_slug']}"
    symbols_by_key[key] = entry

# Load package aliases
with open('pipeline/plugin-capability-registry/package-aliases.json') as f:
    pkg_aliases = json.load(f).get('families', {})

# Load manual analysis summary
with open(REPORT_DIR / 'manual-analysis/manual-family-summary-matrix.json') as f:
    family_matrix = json.load(f).get('families', {})

# Plugin page list from hash ledger
PLUGIN_PAGES = list(page_hashes.keys())

# Map family to plugins
family_plugins = {}
for url in PLUGIN_PAGES:
    parts = url.replace('https://products.aspose.net/', '').split('/')
    if len(parts) >= 3:
        family, _, plugin = parts[0], parts[1], parts[2]
        if family not in family_plugins:
            family_plugins[family] = []
        family_plugins[family].append({'url': url, 'plugin': plugin})

def yaml_str(value):
    """Format value for YAML."""
    if value is None:
        return 'null'
    if isinstance(value, list):
        if not value:
            return '[]'
        return '\n  - ' + '\n  - '.join(str(v) for v in value)
    s = str(value)
    if ':' in s or '"' in s or "'" in s or '\n' in s:
        return f'"{s.replace(chr(34), chr(92) + chr(34))}"'
    return s

def determine_status(family, plugin, harvest_entry, family_info):
    """Determine registry status for a plugin."""
    if not harvest_entry or harvest_entry.get('fetch_status') == 'NO_MATCH':
        return 'NEEDS_MANUAL_MAPPING', 'NEEDS_MANUAL_MAPPING'
    if harvest_entry.get('fetch_status') == 'CODE_FETCH_FAILED':
        return 'CODE_FETCH_FAILED', 'CODE_FETCH_FAILED'

    if family_info:
        blocked_types = family_info.get('blocker_type')
        if blocked_types == 'BLOCKED_LICENSE':
            return 'BLOCKED_LICENSE', 'BLOCKED_LICENSE'

    # Has code — determine readiness
    if harvest_entry.get('fetch_status') == 'OK':
        # Check if it's a caveat file (mismatched)
        caveat_patterns = ['App.xaml', 'RunExamples', 'SceneHierarchyTree', 'ExPdfDigitalSignature']
        filename = harvest_entry.get('filename', '')
        if any(p in filename for p in caveat_patterns):
            return 'NEEDS_MANUAL_MAPPING', None
        return 'CODE_HARVESTED', None

    return 'PAGE_DISCOVERED', None

for family, plugins in sorted(family_plugins.items()):
    family_info = family_matrix.get(family, {})
    impl_model = family_info.get('implementation_model', 'LOAD_SAVE_OPTIONS')
    pkg_id = pkg_aliases.get(family, f'Aspose.{family.capitalize()}')

    yaml_lines = [f'# Plugin-Code Registry: {family}', f'# Generated: 2026-06-04', f'# Sprint: lowcode-plugin-code-registry-20260604', '']
    yaml_lines.append(f'family: {family}')
    yaml_lines.append(f'package_id: {pkg_id}')
    yaml_lines.append(f'github_repo: https://github.com/aspose-{family}/Aspose.{family.capitalize()}-for-.NET')
    yaml_lines.append(f'implementation_model: {impl_model}')
    yaml_lines.append('')
    yaml_lines.append('plugins:')

    for p in plugins:
        plugin = p['plugin']
        url = p['url']
        page_hash = page_hashes.get(url, '')
        key = f'{family}/{plugin}'
        harvest_entry = harvest_by_key.get(key, {})
        symbols = symbols_by_key.get(key, {})

        status, blocker = determine_status(family, plugin, harvest_entry, family_info)

        code_hashes = []
        code_file = harvest_entry.get('filename', '')
        code_hash = harvest_entry.get('code_hash', '')
        raw_url = harvest_entry.get('raw_url', '')
        if code_hash and status not in ['NEEDS_MANUAL_MAPPING', 'CODE_FETCH_FAILED', 'BLOCKED_LICENSE']:
            code_hashes = [code_hash[:32]]

        namespaces = symbols.get('namespaces', [])
        classes = symbols.get('classes', [])
        methods = symbols.get('methods', [])

        # Determine next_action
        if status == 'READY_FOR_TRANSFORMATION':
            next_action = 'Generate example in next transformation sprint'
        elif status == 'CODE_HARVESTED':
            next_action = f'Extract symbols from {code_file} and validate against DllReflector; then advance to READY_FOR_TRANSFORMATION'
        elif status == 'NEEDS_MANUAL_MAPPING':
            next_action = f'Manually write code mapping based on family pattern ({impl_model}); fetch better example from GitHub'
        elif status == 'BLOCKED_LICENSE':
            next_action = 'Set up licensed environment or use full Aspose license; re-probe'
        elif status == 'CODE_FETCH_FAILED':
            next_action = f'Retry fetch from {raw_url}; check GitHub repo structure'
        else:
            next_action = 'Harvest code from GitHub repo; update status'

        evidence = [
            f'reports/lowcode-plugin-code-registry-20260604/crawl/plugin-page-inventory.json',
            f'reports/lowcode-plugin-code-registry-20260604/code-harvest/raw-code-cache-manifest.json',
            f'reports/lowcode-plugin-code-registry-20260604/manual-analysis/family/{family}.md',
        ]
        if raw_url:
            evidence.append(raw_url)

        yaml_lines.append(f'  - plugin_slug: {plugin}')
        yaml_lines.append(f'    plugin_url: {url}')
        yaml_lines.append(f'    page_hash: {page_hash}')
        yaml_lines.append(f'    registry_status: {status}')
        if blocker:
            yaml_lines.append(f'    blocker_type: {blocker}')
        else:
            yaml_lines.append(f'    blocker_type: null')
        yaml_lines.append(f'    implementation_model: {impl_model}')
        if code_hashes:
            yaml_lines.append(f'    code_hashes: [{", ".join(code_hashes)}]')
        else:
            yaml_lines.append(f'    code_hashes: []')
        if namespaces:
            yaml_lines.append(f'    namespaces_used:')
            for ns in namespaces[:4]:
                yaml_lines.append(f'      - "{ns}"')
        if classes:
            yaml_lines.append(f'    classes_used:')
            for cls in classes[:8]:
                yaml_lines.append(f'      - "{cls}"')
        if raw_url and status not in ['NEEDS_MANUAL_MAPPING', 'CODE_FETCH_FAILED']:
            yaml_lines.append(f'    github_links:')
            yaml_lines.append(f'      - {raw_url}')
        yaml_lines.append(f'    next_action: "{next_action}"')
        yaml_lines.append(f'    evidence_paths:')
        for ev in evidence:
            yaml_lines.append(f'      - "{ev}"')
        yaml_lines.append(f'    history:')
        yaml_lines.append(f'      - date: "2026-06-04"')
        yaml_lines.append(f'        status: {status}')
        hist_note = f'Sprint lowcode-plugin-code-registry-20260604. Code from {code_file}' if code_file else 'Sprint lowcode-plugin-code-registry-20260604. Direction correction sprint.'
        yaml_lines.append(f'        analyst_notes: "{hist_note}"')
        yaml_lines.append('')

    yaml_content = '\n'.join(yaml_lines)
    out_file = REGISTRY_DIR / f'{family}.yaml'
    out_file.write_text(yaml_content, encoding='utf-8')
    print(f'Written: {out_file} ({len(plugins)} plugins)')

# Also copy to reports/registry/
report_registry = REPORT_DIR / 'registry' / 'family'
report_registry.mkdir(parents=True, exist_ok=True)

import shutil
for yaml_file in REGISTRY_DIR.glob('*.yaml'):
    shutil.copy(yaml_file, report_registry / yaml_file.name)
    print(f'Copied to reports: {yaml_file.name}')

print('\nRegistry generation complete.')
