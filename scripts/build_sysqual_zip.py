"""Build final system-qualification evidence ZIP per artifact-staging convention.

Steps:
1. Verify git working tree is clean
2. Collect all tracked sprint files
3. Generate artifact-metadata/ to .local/ (outside tracked repo)
4. Build ZIP: tracked files + artifact-metadata/
5. Do NOT commit after ZIP build

ZIP path: .local/evidence-bundles/system-qualification-evidence-<timestamp>.zip
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import zipfile

REPO_ROOT = pathlib.Path(__file__).parent.parent
SPRINT_ID = 'sysqual-20260528-001'
NOW_ISO = '2026-05-28T00:00:00Z'
TIMESTAMP = '20260528'


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, **kw)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def verify_clean():
    out, _, rc = run(['git', 'status', '--short'])
    if out:
        print(f"ERROR: Working tree is not clean:\n{out}", file=sys.stderr)
        sys.exit(1)
    print("OK working tree clean")


def collect_sprint_files():
    patterns = [
        'reports/system-qualification/',
        'scripts/sysqual_discovery.py',
        'scripts/sysqual_reports.py',
        'scripts/sysqual_support_reports.py',
        'scripts/sysqual_iv_and_verdict.py',
        'scripts/build_sysqual_zip.py',
        'src/plugin_examples/family_config/models.py',
        'src/plugin_examples/family_config/loader.py',
        'src/plugin_examples/runner.py',
        'pipeline/configs/families/pdf.yml',
        'pipeline/schemas/family-config.schema.json',
        'pipeline/configs/denominators/words.json',
    ]
    files = []
    for pattern in patterns:
        out, _, _ = run(['git', 'ls-files', pattern])
        if out:
            files.extend(out.splitlines())
    seen = set()
    result = []
    for f in files:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return sorted(result)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.chdir(REPO_ROOT)

    verify_clean()

    full_sha, _, _ = run(['git', 'rev-parse', 'HEAD'])
    full_sha = full_sha.strip()
    print(f"OK HEAD SHA: {full_sha}")

    sprint_files = collect_sprint_files()
    print(f"OK collected {len(sprint_files)} tracked sprint files")

    meta_dir = REPO_ROOT / '.local' / 'artifact-metadata-sysqual'
    meta_dir.mkdir(parents=True, exist_ok=True)

    # bundle-manifest.json
    bundle_manifest = {
        'schema_version': 'bundle-manifest-v1',
        'sprint_id': SPRINT_ID,
        'bundle_type': 'system-qualification-evidence',
        'generated_at': NOW_ISO,
        'final_commit_sha': full_sha,
        'file_count': len(sprint_files),
        'files': sprint_files,
        'artifact_metadata_files': [
            'artifact-metadata/bundle-manifest.json',
            'artifact-metadata/final-clean-proof.txt',
            'artifact-metadata/artifact-verification.json',
            'artifact-metadata/zip-file-list.txt',
        ],
    }
    with open(meta_dir / 'bundle-manifest.json', 'w') as f:
        json.dump(bundle_manifest, f, indent=2)
    print("OK bundle-manifest.json")

    # final-clean-proof.txt
    git_log_out, _, _ = run(['git', 'log', '--oneline', '-5'])
    with open(meta_dir / 'final-clean-proof.txt', 'w') as f:
        f.write(f"SPRINT: {SPRINT_ID}\n")
        f.write(f"FINAL_COMMIT_SHA: {full_sha}\n")
        f.write(f"GENERATED_AT: {NOW_ISO}\n")
        f.write(f"GIT_STATUS: CLEAN\n")
        f.write(f"TRACKED_FILES: {len(sprint_files)}\n")
        f.write(f"\nRECENT GIT LOG:\n{git_log_out}\n")
        f.write(f"\nVERDICT: LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS\n")
    print("OK final-clean-proof.txt")

    # artifact-verification.json
    file_hashes = {}
    for rel_path in sprint_files:
        abs_path = REPO_ROOT / rel_path
        if abs_path.exists():
            file_hashes[rel_path] = sha256_file(abs_path)

    artifact_verification = {
        'schema_version': 'artifact-verification-v1',
        'sprint_id': SPRINT_ID,
        'final_commit_sha': full_sha,
        'generated_at': NOW_ISO,
        'git_status': 'CLEAN',
        'tracked_file_count': len(sprint_files),
        'file_sha256': file_hashes,
        'verdict': 'LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS',
        'products_classified': 25,
        'lowcode_confirmed': 6,
        'no_lowcode_confirmed': 16,
        'discovery_blocked': 3,
        'e2e_pass_count': 6,
        'machinery_defects_healed': 2,
    }
    with open(meta_dir / 'artifact-verification.json', 'w') as f:
        json.dump(artifact_verification, f, indent=2)
    print("OK artifact-verification.json")

    # Build ZIP
    zip_filename = f'system-qualification-evidence-{TIMESTAMP}.zip'
    zip_path = REPO_ROOT / '.local' / 'evidence-bundles' / zip_filename
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    all_zip_entries = []

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in sprint_files:
            abs_path = REPO_ROOT / rel_path
            if abs_path.exists():
                zf.write(abs_path, rel_path)
                all_zip_entries.append(rel_path)
            else:
                print(f"  WARN: not found: {rel_path}")

        zip_list_entries = all_zip_entries + [
            'artifact-metadata/bundle-manifest.json',
            'artifact-metadata/final-clean-proof.txt',
            'artifact-metadata/artifact-verification.json',
            'artifact-metadata/zip-file-list.txt',
        ]
        with open(meta_dir / 'zip-file-list.txt', 'w') as f:
            f.write(f"ZIP: {zip_filename}\n")
            f.write(f"SPRINT: {SPRINT_ID}\n")
            f.write(f"ENTRIES: {len(zip_list_entries)}\n\n")
            for entry in zip_list_entries:
                f.write(f"{entry}\n")

        for meta_file in ['bundle-manifest.json', 'final-clean-proof.txt', 'artifact-verification.json', 'zip-file-list.txt']:
            src = meta_dir / meta_file
            zf.write(src, f'artifact-metadata/{meta_file}')
            all_zip_entries.append(f'artifact-metadata/{meta_file}')

    total_entries = len(all_zip_entries)
    zip_size = zip_path.stat().st_size
    print(f"OK ZIP built: {zip_path}")
    print(f"   entries={total_entries}, size={zip_size:,} bytes ({zip_size/1024/1024:.2f} MB)")

    # Final clean check
    out, _, _ = run(['git', 'status', '--short'])
    if out:
        print(f"ERROR: git status dirty after ZIP build!\n{out}", file=sys.stderr)
        sys.exit(1)
    print("OK git status still clean after ZIP build")
    print("\nDONE")
    print(f"  ZIP: .local/evidence-bundles/{zip_filename}")
    print(f"  Final commit: {full_sha}")
    print("  No post-ZIP commit required or permitted.")


if __name__ == '__main__':
    main()
