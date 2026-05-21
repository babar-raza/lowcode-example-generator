#!/usr/bin/env python3
"""Sprint 57 destination repo audit script."""
import json, subprocess, os

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
    print(f'Checking {family}...')
    r = subprocess.run(
        ['gh', 'api', f'repos/{org}/{repo}/git/refs/heads/main', '--jq', '.object.sha'],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f'  ERROR: {r.stderr[:100]}')
        results[family] = {'status': 'ERROR', 'error': r.stderr.strip()}
        continue
    sha = r.stdout.strip()
    r2 = subprocess.run(
        ['gh', 'api', f'repos/{org}/{repo}/contents/', '--jq', '[.[] | {name: .name, type: .type}]'],
        capture_output=True, text=True
    )
    files = []
    if r2.returncode == 0:
        try:
            files = json.loads(r2.stdout)
        except Exception:
            pass
    results[family] = {
        'org': org,
        'repo': repo,
        'latest_sha': sha,
        'root_files': files,
        'has_readme': any(f['name'].lower() == 'readme.md' for f in files),
        'has_examples_dir': any(f['name'].lower() in ('examples', 'src', 'lowcode', 'csharp') for f in files),
    }
    print(f'  SHA: {sha[:12]}... files: {len(files)} readme: {results[family]["has_readme"]}')

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'destination-repo-audit.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f'Saved {out_path}')
