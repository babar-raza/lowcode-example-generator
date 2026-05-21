#!/usr/bin/env python3
"""Sprint 57 destination repo deep content verification."""
import subprocess, json, os

repos = {
    'cells': ('aspose-cells-net', 'Aspose.Cells.LowCode-for-.NET-Examples'),
    'words': ('aspose-words-net', 'Aspose.Words.LowCode-for-.NET-Examples'),
    'pdf': ('aspose-pdf-net', 'Aspose.PDF.LowCode-for-.NET-Examples'),
    'diagram': ('aspose-diagram-net', 'Aspose.Diagram.LowCode-for-.NET-Examples'),
    'email': ('aspose-email-net', 'Aspose.Email.LowCode-for-.NET-Examples'),
    'slides': ('aspose-slides-net', 'Aspose.Slides.LowCode-for-.NET-Examples'),
}

content_proof = {}
for family, (org, repo) in repos.items():
    # Check examples/{family}/ for example subdirectories
    r = subprocess.run(
        ['gh', 'api', f'repos/{org}/{repo}/contents/examples/{family}',
         '--jq', '[.[] | {name: .name, type: .type}]'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        content_proof[family] = {'status': 'ERROR', 'error': r.stderr[:100]}
        continue
    try:
        items = json.loads(r.stdout)
        dirs = [d['name'] for d in items if d['type'] == 'dir']
        files = [d['name'] for d in items if d['type'] == 'file']
        content_proof[family] = {
            'status': 'OK',
            'path': f'examples/{family}/',
            'subdirs': dirs,
            'files': files,
            'example_count': len(dirs)
        }
        print(f'{family} examples/{family}/: {len(dirs)} subdirs: {dirs[:5]}...')
    except Exception as e:
        content_proof[family] = {'status': 'PARSE_ERROR', 'error': str(e)}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'destination-content-proof2.json')
with open(out_path, 'w') as f:
    json.dump(content_proof, f, indent=2)
print(f'Saved {out_path}')
