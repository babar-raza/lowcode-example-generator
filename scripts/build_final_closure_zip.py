"""Build the final-closure evidence ZIP — lowcode-final-closure-20260531.

Sprint 1F+ artifact-staging convention:
- All tracked files committed BEFORE this script runs
- ZIP includes: reports/ + source files + artifact-metadata/
- artifact-metadata/ written POST-COMMIT to .local/ (gitignored)
- Sidecar SHA/size/count OUTSIDE ZIP
- No commit after ZIP build
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPRINT_ID = "lowcode-final-closure-20260531"
LOCAL_DIR = REPO_ROOT / ".local" / "evidence-bundles"
ZIP_PATH = LOCAL_DIR / f"{SPRINT_ID}-evidence.zip"
META_DIR = LOCAL_DIR / "artifact-metadata" / SPRINT_ID
LOCAL_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=REPO_ROOT).stdout.strip()


def git_status_clean() -> tuple[bool, int]:
    status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True,
                             cwd=REPO_ROOT).stdout.strip()
    tracked = [l for l in status.splitlines() if l and not l.startswith("??")]
    return len(tracked) == 0, len(tracked)


def collect_files() -> list[tuple[Path, str]]:
    """Return (absolute_path, archive_name) pairs for ZIP."""
    files = []

    # 1. Evidence reports
    reports_dir = REPO_ROOT / "reports" / SPRINT_ID
    for f in sorted(reports_dir.rglob("*")):
        if f.is_file():
            arc = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
            files.append((f, arc))

    # 2. Key source files
    key_sources = [
        "src/plugin_examples/gates/evaluator.py",
        "src/plugin_examples/gates/models.py",
        "tests/unit/test_gates.py",
        "tests/unit/test_false_success_contracts.py",
        "tests/unit/test_agent_metrics_payload.py",
        "tests/unit/test_agent_metrics_config.py",
        "pipeline/configs/metrics.yml",
        "scripts/run_final_closure_evidence.py",
        "scripts/build_final_closure_zip.py",
        "pipeline/configs/denominators/words.json",
        "pipeline/configs/denominators/pdf.json",
    ]
    for src in key_sources:
        p = REPO_ROOT / src
        if p.exists():
            files.append((p, src))

    return files


def build_zip(files: list[tuple[Path, str]], meta_dir: Path) -> None:
    meta_files = sorted(meta_dir.rglob("*"))
    print(f"Building ZIP: {ZIP_PATH}")
    print(f"  Tracked files: {len(files)}")
    print(f"  Metadata files: {len([f for f in meta_files if f.is_file()])}")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fpath, arc_name in files:
            zf.write(fpath, arc_name)
        for meta_f in sorted(meta_files):
            if meta_f.is_file():
                arc = "artifact-metadata/" + meta_f.name
                zf.write(meta_f, arc)


def main():
    print(f"=== Build Evidence ZIP: {SPRINT_ID} ===")
    print(f"Time: {now_ts()}")

    is_clean, dirty_count = git_status_clean()
    head = git_head()
    print(f"HEAD: {head}")
    print(f"Tracked dirty files: {dirty_count} ({'CLEAN' if is_clean else 'DIRTY — ABORT'})")
    if not is_clean:
        print("ERROR: Commit tracked changes before building ZIP.")
        sys.exit(1)

    files = collect_files()
    print(f"Total files to include: {len(files)}")

    # Write artifact-metadata Pass 1 (without ZIP SHA)
    bundle_manifest = {
        "sprint_id": SPRINT_ID,
        "generated_at": now_ts(),
        "head_sha": head,
        "tracked_dirty_at_build": dirty_count,
        "source_files_count": len(files),
        "zip_path": str(ZIP_PATH),
        "note": "zip_sha256 written to sidecar .sha256 file post-build",
    }
    (META_DIR / "bundle-manifest.json").write_text(
        json.dumps(bundle_manifest, indent=2), encoding="utf-8")

    # Copy final-clean-proof.json
    src_proof = REPO_ROOT / "reports" / SPRINT_ID / "artifact" / "final-clean-proof.json"
    if src_proof.exists():
        import shutil
        shutil.copy2(src_proof, META_DIR / "final-clean-proof.json")

    # Build ZIP pass 1
    build_zip(files, META_DIR)

    # Compute SHA-256 pass 1
    zip_sha256 = sha256_file(ZIP_PATH)
    zip_size = ZIP_PATH.stat().st_size
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zip_entry_count = len(zf.namelist())

    print(f"\nZIP pass 1:")
    print(f"  SHA-256: {zip_sha256}")
    print(f"  Size:    {zip_size:,} bytes")
    print(f"  Entries: {zip_entry_count}")

    # Write sidecar files (outside ZIP)
    sidecar_sha = LOCAL_DIR / f"{SPRINT_ID}-evidence.zip.sha256"
    sidecar_sha.write_text(zip_sha256, encoding="utf-8")

    sidecar_sc = LOCAL_DIR / f"{SPRINT_ID}-evidence.zip.size-count.json"
    sidecar_sc.write_text(json.dumps({
        "sprint_id": SPRINT_ID,
        "zip_sha256": zip_sha256,
        "zip_size_bytes": zip_size,
        "zip_size_kb": round(zip_size / 1024, 1),
        "entry_count": zip_entry_count,
        "generated_at": now_ts(),
        "head_sha": head,
    }, indent=2), encoding="utf-8")

    # Write artifact-verification.json (with SHA from pass 1)
    (META_DIR / "artifact-verification.json").write_text(json.dumps({
        "sprint_id": SPRINT_ID,
        "zip_sha256": zip_sha256,
        "zip_size_bytes": zip_size,
        "entry_count": zip_entry_count,
        "head_sha": head,
        "tracked_dirty_at_build": dirty_count,
        "generated_at": now_ts(),
    }, indent=2), encoding="utf-8")

    # Write zip-file-list (from pass 1)
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        entries = sorted(zf.namelist())
    (META_DIR / "zip-file-list.txt").write_text("\n".join(entries), encoding="utf-8")

    # Build ZIP pass 2 — include artifact-verification + zip-file-list
    build_zip(files, META_DIR)

    # Final SHA after pass 2
    zip_sha256_final = sha256_file(ZIP_PATH)
    zip_size_final = ZIP_PATH.stat().st_size
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zip_entry_count_final = len(zf.namelist())

    # Update sidecar with final values
    sidecar_sha.write_text(zip_sha256_final, encoding="utf-8")
    sidecar_sc.write_text(json.dumps({
        "sprint_id": SPRINT_ID,
        "zip_sha256": zip_sha256_final,
        "zip_size_bytes": zip_size_final,
        "zip_size_kb": round(zip_size_final / 1024, 1),
        "entry_count": zip_entry_count_final,
        "generated_at": now_ts(),
        "head_sha": head,
    }, indent=2), encoding="utf-8")

    print(f"\n=== Final ZIP (pass 2) ===")
    print(f"  SHA-256: {zip_sha256_final}")
    print(f"  Size:    {zip_size_final:,} bytes ({zip_size_final / 1024:.1f} KB)")
    print(f"  Entries: {zip_entry_count_final}")
    print(f"\nSidecar SHA:        {sidecar_sha}")
    print(f"Sidecar size-count: {sidecar_sc}")
    print(f"\nVERDICT: LOWCODE_REPEATABLE_SYSTEM_PUBLICATION_READY_APPROVAL_BLOCKED")


if __name__ == "__main__":
    main()
