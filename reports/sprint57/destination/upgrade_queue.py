#!/usr/bin/env python3
"""Sprint 57 Lane G: upgrade 14 MERGED -> POST_MERGE_VERIFIED after content verification."""
import json
from collections import Counter

with open('workspace/queues/example-completion-queue.json', encoding='utf-8') as f:
    q = json.load(f)

dest_content = {
    'cells': {'html-converter','image-converter','json-converter','pdf-converter',
              'spreadsheet-converter','spreadsheet-locker','spreadsheet-merger',
              'spreadsheet-splitter','text-converter'},
    'words': {'comparer','converter','mail-merger','merger','replacer',
              'report-builder','splitter','watermarker'},
    'pdf': {'doc-converter','form-editor','form-exporter','form-flattener','html',
            'image-extractor','jpeg','merger','optimizer','pdfa-converter','png',
            'security','signature','splitter','table-generator','text-extractor',
            'tiff','toc-generator','xls-converter'},
    'diagram': {'diagram-diagram-converter','diagram-pdf-converter'},
    'email': {'converter'},
    'slides': {'compress','convert','merger'},
}

def sid_to_dir(sid, family):
    prefix = family + '-'
    if sid.startswith(prefix):
        return sid[len(prefix):]
    return sid

upgraded = 0
not_found = []
for entry in q['entries']:
    if entry['state'] == 'MERGED':
        sid = entry['scenario_id']
        family = entry['family']
        dir_name = sid_to_dir(sid, family)
        family_content = dest_content.get(family, set())
        if dir_name in family_content:
            entry['state'] = 'POST_MERGE_VERIFIED'
            entry['post_merge_validation'] = 'CONTENT_VERIFIED'
            old_notes = entry.get('notes', '')
            entry['notes'] = (
                f'Sprint57-LaneG: Upgraded MERGED->POST_MERGE_VERIFIED. '
                f'Destination repo content verified 2026-05-21: '
                f'examples/{family}/lowcode/{dir_name}/ present. '
                + old_notes
            )
            upgraded += 1
            print(f'  Upgraded: {sid} -> POST_MERGE_VERIFIED')
        else:
            not_found.append(f'{sid} (looking for {dir_name} in {family})')
            print(f'  NOT FOUND: {sid}')

active_states = Counter(e['state'] for e in q['entries']
                        if e['state'] not in ('BACKLOGGED', 'PERMANENTLY_BLOCKED'))
bg = sum(1 for e in q['entries'] if e['state'] == 'BACKLOGGED')
pb = sum(1 for e in q['entries'] if e['state'] == 'PERMANENTLY_BLOCKED')
q['state_summary'] = {k: v for k, v in dict(active_states).items() if v > 0}
q['state_summary']['BACKLOGGED'] = bg
q['state_summary']['PERMANENTLY_BLOCKED'] = pb

with open('workspace/queues/example-completion-queue.json', 'w', encoding='utf-8') as f:
    json.dump(q, f, indent=2, ensure_ascii=False)

print(f'Done. {upgraded} upgraded. State: {q["state_summary"]}')
if not_found:
    print(f'Not found: {not_found}')
