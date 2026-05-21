#!/usr/bin/env python3
"""Sprint 57 destination repo lowcode subdir content verification."""
import subprocess, json, os

repos = {
    'cells': ('aspose-cells-net', 'Aspose.Cells.LowCode-for-.NET-Examples'),
    'words': ('aspose-words-net', 'Aspose.Words.LowCode-for-.NET-Examples'),
    'pdf': ('aspose-pdf-net', 'Aspose.PDF.LowCode-for-.NET-Examples'),
    'diagram': ('aspose-diagram-net', 'Aspose.Diagram.LowCode-for-.NET-Examples'),
    'email': ('aspose-email-net', 'Aspose.Email.LowCode-for-.NET-Examples'),
    'slides': ('aspose-slides-net', 'Aspose.Slides.LowCode-for-.NET-Examples'),
}

results = {}
for family, (org, repo) in repos.items():
    r = subprocess.run(
        ['gh', 'api', f'repos/{org}/{repo}/contents/examples/{family}/lowcode',
         '--jq', '[.[] | {name: .name, type: .type}]'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        results[family] = {'status': 'ERROR', 'error': r.stderr[:100]}
        continue
    try:
        items = json.loads(r.stdout)
        dirs = sorted([d['name'] for d in items if d['type'] == 'dir'])
        results[family] = {
            'status': 'CONTENT_VERIFIED',
            'path': f'examples/{family}/lowcode/',
            'example_projects': dirs,
            'count': len(dirs)
        }
        print(f'{family}: {len(dirs)} examples: {dirs}')
    except Exception as e:
        results[family] = {'status': 'PARSE_ERROR', 'error': str(e)}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'destination-lowcode-content.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f'Saved {out_path}')
