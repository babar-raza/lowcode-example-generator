"""Build SHA256 bundle-manifest.json for Sprint 66."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
bundle_dir = root / "reports" / "sprint66"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

files = sorted(bundle_dir.rglob("*"))
entries = []
for f in files:
    if f.is_file():
        rel = f.relative_to(root).as_posix()
        entries.append({"file": rel, "sha256": sha256_file(f), "size": f.stat().st_size})

manifest = {
    "generated": "2026-05-22T00:00:00Z",
    "sprint_id": "sprint66",
    "total_files": len(entries),
    "files": entries,
}

out = bundle_dir / "bundle-manifest.json"
out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"bundle-manifest.json: {len(entries)} files")
