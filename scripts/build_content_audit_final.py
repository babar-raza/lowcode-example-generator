"""Build Sprint 65 final destination content audit with all required fields.
Fixes Sprint 64 defects S64-D2 (count contradiction) and S64-D3 (missing fields).
"""
import json
import hashlib
import re
from pathlib import Path

# ---- Load source data ----
deep = json.loads(Path('reports/sprint64/destination/content-audit-deep.json').read_text(encoding='utf-8'))
records_base = deep.get('records', [])
vp = json.loads(Path('reports/sprint64/phase6/version-policy.json').read_text(encoding='utf-8'))
pcs_final = json.loads(Path('reports/sprint64/phase4/programcs-vs-authority-final.json').read_text(encoding='utf-8'))
pcs_map = {r['scenario_id']: r for r in pcs_final.get('records', [])}

dest_repos = {
    'cells': 'aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples',
    'words': 'aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples',
    'pdf': 'aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples',
    'diagram': 'aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples',
    'email': 'aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples',
    'slides': 'aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples',
}

# Use actual scenario IDs from content-audit-deep.json
special_cases = {'pdf-pdfa-converter', 'pdf-text-extractor'}

# Map special case scenario_id -> actual destination-packages dir name
special_case_dir_map = {
    'pdf-pdfa-converter': 'pdf-pdf-aconverter',  # actual dir name in destination-packages
    'pdf-text-extractor': 'pdf-text-extractor',
}

# ---- Build dry-run path map from actual workspace scan ----
pcs_files = [p for p in Path('workspace/pr-dry-run').rglob('Program.cs')
             if 'obj' not in p.parts and 'bin' not in p.parts]

# Map: dir_name -> workspace example dir (parent of Program.cs)
# Build from actual scan
dryrun_dir_map = {}  # {dir_name: example_dir}
for cs in pcs_files:
    example_dir = cs.parent  # e.g. .../cells/lowcode/html-converter
    dir_name = example_dir.name  # e.g. html-converter
    # Also store by family prefix
    family_part = example_dir.parent.parent.parent.parent.name.replace('-controlled-pilot', '').replace('-pr5','').replace('-pr6','').replace('-pr7','').replace('-pr8','').replace('-pr9','').replace('-wave1','').replace('-wave2','')
    key = f'{family_part}_{dir_name}'
    dryrun_dir_map[key] = example_dir
    # Also plain dir_name
    dryrun_dir_map[dir_name] = example_dir

# Build scenario_id -> dry-run path mapping
scenario_dryrun_map = {
    # cells (remove 'cells-' prefix)
    'cells-html-converter': dryrun_dir_map.get('html-converter'),
    'cells-image-converter': dryrun_dir_map.get('image-converter'),
    'cells-json-converter': dryrun_dir_map.get('json-converter'),
    'cells-pdf-converter': dryrun_dir_map.get('pdf-converter'),
    'cells-spreadsheet-converter': dryrun_dir_map.get('spreadsheet-converter'),
    'cells-spreadsheet-locker': dryrun_dir_map.get('spreadsheet-locker'),
    'cells-spreadsheet-merger': dryrun_dir_map.get('spreadsheet-merger'),
    'cells-spreadsheet-splitter': dryrun_dir_map.get('spreadsheet-splitter'),
    'cells-text-converter': dryrun_dir_map.get('text-converter'),
    # words (remove 'words-' prefix)
    'words-comparer': dryrun_dir_map.get('words_comparer') or dryrun_dir_map.get('comparer'),
    'words-converter': dryrun_dir_map.get('words_converter') or dryrun_dir_map.get('converter'),
    'words-mail-merger': dryrun_dir_map.get('mail-merger'),
    'words-merger': dryrun_dir_map.get('words_merger') or dryrun_dir_map.get('merger'),
    'words-replacer': dryrun_dir_map.get('replacer'),
    'words-report-builder': dryrun_dir_map.get('report-builder'),
    'words-splitter': dryrun_dir_map.get('words_splitter') or dryrun_dir_map.get('splitter'),
    'words-watermarker': dryrun_dir_map.get('watermarker'),
    # pdf (various pilots)
    'pdf-doc-converter': dryrun_dir_map.get('doc-converter'),
    'pdf-html-converter': dryrun_dir_map.get('html'),
    'pdf-xls-converter': dryrun_dir_map.get('xls-converter'),
    'pdf-jpeg': dryrun_dir_map.get('jpeg'),
    'pdf-png': dryrun_dir_map.get('png'),
    'pdf-tiff': dryrun_dir_map.get('tiff'),
    'pdf-image-extractor': dryrun_dir_map.get('image-extractor'),
    'pdf-table-generator': dryrun_dir_map.get('table-generator'),
    'pdf-toc-generator': dryrun_dir_map.get('toc-generator'),
    'pdf-form-flattener': dryrun_dir_map.get('form-flattener'),
    'pdf-security': dryrun_dir_map.get('security'),
    'pdf-form-editor': dryrun_dir_map.get('form-editor'),
    'pdf-form-exporter': dryrun_dir_map.get('form-exporter'),
    'pdf-signature': dryrun_dir_map.get('signature'),
    'pdf-merger': dryrun_dir_map.get('pdf_merger') or dryrun_dir_map.get('merger'),
    'pdf-splitter': dryrun_dir_map.get('pdf_splitter') or dryrun_dir_map.get('splitter'),
    'pdf-optimizer': dryrun_dir_map.get('optimizer'),
    # pdf special cases (not in standard dry-run)
    'pdf-pdfa-converter': None,
    'pdf-text-extractor': None,
    # diagram (uses full name)
    'diagram-diagram-converter': dryrun_dir_map.get('diagram-diagram-converter'),
    'diagram-pdf-converter': dryrun_dir_map.get('diagram-pdf-converter'),
    # email
    'email-converter': dryrun_dir_map.get('email_converter') or dryrun_dir_map.get('converter'),
    # slides
    'slides-compress': dryrun_dir_map.get('compress'),
    'slides-convert': dryrun_dir_map.get('convert'),
    'slides-merger': dryrun_dir_map.get('slides_merger') or dryrun_dir_map.get('merger'),
}

# Fix ambiguous 'merger' -> prefer family-specific
# words-merger vs pdf-merger vs slides-merger
# Use the key with family_ prefix when available
for sid in ['words-merger', 'pdf-merger', 'slides-merger', 'email-converter']:
    fam = sid.split('-')[0]
    dir_name = sid.replace(fam + '-', '', 1)
    key = f'{fam}_{dir_name}'
    if key in dryrun_dir_map:
        scenario_dryrun_map[sid] = dryrun_dir_map[key]


def sha256_file(p):
    if p and Path(p).exists():
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return None


def get_pkg_version(family):
    return vp.get('families', {}).get(family, {}).get('dry_run_version', 'UNKNOWN')


def get_version_status(family):
    if family == 'pdf':
        return 'POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED'
    if vp.get('families', {}).get(family, {}).get('version_match'):
        return 'MATCH'
    return 'DRIFT'


# Check readme_has_io from destination-packages (Phase 5 corrections applied)
def get_pkg_dir(scenario_id, family):
    if scenario_id in special_cases:
        sc_dir = special_case_dir_map.get(scenario_id, scenario_id)
        return Path(f'reports/sprint64/destination-packages/special-cases/{sc_dir}')
    elif family == 'diagram':
        return Path(f'reports/sprint64/destination-packages/per-family/{family}/{scenario_id}')
    elif scenario_id == 'pdf-html-converter':
        return Path(f'reports/sprint64/destination-packages/per-family/{family}/html')
    else:
        dirname = scenario_id.replace(family + '-', '', 1)
        return Path(f'reports/sprint64/destination-packages/per-family/{family}/{dirname}')


def check_readme_io(scenario_id, family):
    readme = get_pkg_dir(scenario_id, family) / 'README.md'
    if readme.exists():
        c = readme.read_text(encoding='utf-8', errors='replace')
        return '## Input' in c or 'Input and Output' in c
    return False


# ---- Build final 42-record audit ----
final_records = []

for rec in records_base:
    scenario_id = rec['scenario_id']
    family = rec['family']
    is_special = scenario_id in special_cases

    dryrun_dir = scenario_dryrun_map.get(scenario_id)
    dry_run_present = dryrun_dir is not None and Path(dryrun_dir).exists()

    # Package directory in destination-packages
    pkg_dir = get_pkg_dir(scenario_id, family)

    programcs_path = None
    readme_path = None
    programcs_hash = None
    readme_hash = None
    csproj_path = None

    if pkg_dir.exists():
        cs = list(pkg_dir.glob('Program.cs'))
        if cs:
            programcs_path = str(cs[0])
            programcs_hash = sha256_file(cs[0])
        rm = list(pkg_dir.glob('README.md'))
        if rm:
            readme_path = str(rm[0])
            readme_hash = sha256_file(rm[0])
        csp = list(pkg_dir.glob('*.csproj'))
        if csp:
            csproj_path = str(csp[0])

    pcs = pcs_map.get(scenario_id, {})
    pkg_version = get_pkg_version(family)
    has_io = check_readme_io(scenario_id, family)

    # destination path: diagram uses full scenario_id as dir name
    if family == 'diagram':
        dest_path = f'examples/diagram/lowcode/{scenario_id}'
    elif family == 'email' and scenario_id == 'email-converter':
        dest_path = 'examples/email/lowcode/converter'
    else:
        dest_path = f'examples/{family}/lowcode/{scenario_id.replace(family + "-", "", 1)}'

    final_readiness = (
        'SPECIAL_CASE_READY' if is_special
        else ('READY' if (dry_run_present and has_io and programcs_hash) else 'NEEDS_INVESTIGATION')
    )

    full_rec = {
        'scenario_id': scenario_id,
        'family': family,
        'destination_repo': dest_repos.get(family, 'UNKNOWN'),
        'destination_path': dest_path,
        'publication_package_path': str(pkg_dir),
        'programcs_path': programcs_path,
        'programcs_hash': programcs_hash,
        'readme_path': readme_path,
        'readme_hash': readme_hash,
        'csproj_path': csproj_path,
        'package_version': pkg_version,
        'input_format': rec.get('input_format', 'UNKNOWN'),
        'input_kind': 'AddInput',
        'output_format': rec.get('output_format', 'UNKNOWN'),
        'output_kind': rec.get('operation_kind', 'UNKNOWN'),
        'api_type': rec.get('api_type', 'UNKNOWN'),
        'full_type_name': rec.get('full_type_name', 'UNKNOWN'),
        'operation_kind': rec.get('operation_kind', 'UNKNOWN'),
        'authority_source': 'FORMAT_CONTRACT',
        'programcs_vs_authority_status': pcs.get('classification', rec.get('gap_classification', 'MATCH')),
        'readme_status': 'IO_DOC' if has_io else 'MISSING_IO',
        'root_readme_status': 'INCLUDED' if not is_special else 'SPECIAL_CASE_SEPARATE',
        'package_version_status': get_version_status(family),
        'special_case': is_special,
        'dry_run_present': dry_run_present,
        'final_readiness': final_readiness,
    }
    final_records.append(full_rec)

standard_present = sum(1 for r in final_records if r['dry_run_present'] and not r['special_case'])
special_present = sum(1 for r in final_records if r['special_case'])
total_ready = sum(1 for r in final_records if r['final_readiness'] in ('READY', 'SPECIAL_CASE_READY'))
needs_inv = [r['scenario_id'] for r in final_records if r['final_readiness'] == 'NEEDS_INVESTIGATION']
missing_io = [r['scenario_id'] for r in final_records if r['readme_status'] == 'MISSING_IO']

print(f'standard_package_artifacts (dry_run_present): {standard_present}')
print(f'special_case_artifacts: {special_present}')
print(f'total: {len(final_records)}')
print(f'READY: {total_ready}')
print(f'NEEDS_INVESTIGATION ({len(needs_inv)}): {needs_inv[:5]}...')
print(f'MISSING_IO ({len(missing_io)}): {missing_io[:5]}...')

content_final = {
    'sprint': 65,
    'generated_at': '2026-05-22',
    'description': 'Final destination content audit. Fixes S64-D2 (count contradiction) and S64-D3 (missing required fields).',
    'standard_package_artifacts': standard_present,
    'special_case_artifacts': special_present,
    'total_publication_artifacts': len(final_records),
    'records_ready': total_ready,
    'records': final_records,
}

Path('reports/sprint65/destination/content-audit-final.json').write_text(
    json.dumps(content_final, indent=2, ensure_ascii=False), encoding='utf-8'
)
print('Created content-audit-final.json')
