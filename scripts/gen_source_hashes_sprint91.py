"""Generate source-hashes.json for Sprint 91."""
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src_files = sorted(
    list((root / "src").rglob("*.py")) + list((root / "tests").rglob("*.py"))
)
hashes = {}
for f in src_files:
    try:
        content = f.read_bytes()
        rel = str(f.relative_to(root)).replace("\\", "/")
        hashes[rel] = hashlib.sha256(content).hexdigest()[:16]
    except Exception:
        pass

result = {
    "sprint_id": "sprint91",
    "generated_at": "2026-05-27T00:00:00Z",
    "file_count": len(hashes),
    "hashes": hashes,
}
out = root / "reports" / "sprint91" / "source-hashes.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Wrote {len(hashes)} hashes to {out}")
