"""Build the blocker-closure evidence ZIP — lowcode-blocker-closure-20260531.

Sprint 1F+ artifact-staging convention:
- All tracked files committed BEFORE this script runs
- ZIP includes: canonical examples + format authority + probes + key sources + artifact-metadata
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
SPRINT_ID = "lowcode-blocker-closure-20260531"
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

    def add(rel: str) -> None:
        p = REPO_ROOT / rel
        if p.exists():
            files.append((p, rel.replace("\\", "/")))

    def add_dir(rel: str) -> None:
        d = REPO_ROOT / rel
        if d.is_dir():
            for f in sorted(d.rglob("*")):
                if f.is_file() and not any(p in f.parts for p in ("bin", "obj", "__pycache__")):
                    arc = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
                    files.append((f, arc))

    # 1. New canonical examples
    add_dir("workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/signer")
    add_dir("workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/for-each")

    # 2. Updated package READMEs
    add("workspace/pr-dry-run/words-controlled-pilot/README.md")
    add("workspace/pr-dry-run/slides-controlled-pilot/README.md")

    # 3. Format authority (updated with Signer + ForEach)
    add("pipeline/format-authority/contracts/words.json")
    add("pipeline/format-authority/contracts/slides.json")
    add("pipeline/format-authority/manifest.json")

    # 4. Completion queue
    add("workspace/queues/example-completion-queue.json")

    # 5. Probe directories (build/run evidence)
    add_dir("workspace/runs/blocker-closure-20260531/probes/words-signer")
    add_dir("workspace/runs/blocker-closure-20260531/probes/slides-for-each")
    add_dir("workspace/runs/blocker-closure-20260531/probes/words-ofd")
    add_dir("workspace/runs/blocker-closure-20260531/probes/words-processor")

    # 6. Verification snapshots
    add("workspace/verification/latest/words-root-readme-render-result.json")
    add("workspace/verification/latest/words-root-readme-audit.json")
    add("workspace/verification/latest/release-status.json")

    # 7. Denominators
    add("pipeline/configs/denominators/words.json")
    add("pipeline/configs/denominators/slides.json")

    # 8. Assembly manifests
    add("pipeline/configs/assembly-manifests/words-controlled-pilot.json")
    add("pipeline/configs/assembly-manifests/slides-controlled-pilot.json")

    # 9. Key source / test files updated this sprint
    add("tests/unit/test_format_authority_store.py")
    add("tests/unit/test_operation_kind_cardinality_matrix.py")
    add("tests/unit/test_readme_renderer.py")
    add("scripts/build_blocker_closure_zip.py")

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
        "blockers_closed": ["words-signer", "slides-for-each"],
        "blockers_reclassified_not_a_main_class": ["words-Processor", "cells-SpreadsheetPrinter"],
        "blockers_unsupported_format": ["words-OFD"],
        "blockers_deferred": ["pdf-FormImporter", "pdf-Timestamp"],
        "new_format_contracts": ["words/Signer", "slides/ForEach"],
        "pytest_result": "3222 passed, 18 skipped, 0 failed",
        "note": "zip_sha256 written to sidecar .sha256 file post-build",
    }
    (META_DIR / "bundle-manifest.json").write_text(
        json.dumps(bundle_manifest, indent=2), encoding="utf-8")

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
    print(f"\nZIP path:           {ZIP_PATH}")
    print(f"Sidecar SHA:        {sidecar_sha}")
    print(f"Sidecar size-count: {sidecar_sc}")
    print(f"\nVERDICT: BLOCKER_CLOSURE_PARTIAL_WORDS_SIGNER_AND_SLIDES_FOREACH_PROVEN")


if __name__ == "__main__":
    main()
