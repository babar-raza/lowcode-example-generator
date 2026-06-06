"""Build Wave 14 evidence bundle ZIP."""
import zipfile, pathlib, hashlib

ROOT = pathlib.Path(__file__).parents[3]
SPRINT = "lowcode-plugin-canonical-package-wave14-20260606"
REPORT = ROOT / "reports" / SPRINT
BUNDLE_PATH = ROOT / ".local/evidence-bundles" / f"{SPRINT}.zip"

INCLUDE_DIRS = [
    "adversarial-review",
    "canonical-verification",
    "coordinator",
    "final",
    "iv",
    "package-proofs",
    "preflight",
    "publication-staging",
    "state-docs",
    "taskcards",
    "validators",
    "wave13-closure-repair",
]
EXCLUDE_PATTERNS = ["/bin/", "/obj/", ".dll", ".exe", ".pdb", ".nupkg", ".pfx", "build_bundle.py"]

entries = []
BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(BUNDLE_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for d in INCLUDE_DIRS:
        dpath = REPORT / d
        if not dpath.exists():
            continue
        for f in sorted(dpath.rglob("*")):
            if not f.is_file():
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            skip = any(pat in rel for pat in EXCLUDE_PATTERNS)
            if skip:
                continue
            zf.write(f, rel)
            entries.append(rel)
    # wave14-dryrun examples (source + output only, no bin/obj)
    wave_dir = REPORT / "wave14-dryrun"
    for f in sorted(wave_dir.rglob("*")):
        if not f.is_file():
            continue
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        skip = any(pat in rel for pat in EXCLUDE_PATTERNS)
        if skip:
            continue
        zf.write(f, rel)
        entries.append(rel)

sha256 = hashlib.sha256(BUNDLE_PATH.read_bytes()).hexdigest()
print(f"Bundle: {BUNDLE_PATH}")
print(f"Entries: {len(entries)}")
print(f"Size: {BUNDLE_PATH.stat().st_size} bytes")
print(f"SHA-256: {sha256}")
