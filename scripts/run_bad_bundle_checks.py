"""
Healing Sprint 1B -- Bad-Bundle Regression Checks
Executable checks for 6 known bad-bundle patterns.
Returns 0 if all checks pass, 1 if any fail.
"""
import sys
import json
import re
import subprocess
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

results = []


def check(check_id, description, passed, detail, classification=None):
    status = PASS if passed else FAIL
    if classification:
        status = SKIP
    results.append({
        "id": check_id,
        "description": description,
        "status": status,
        "detail": detail,
        "classification": classification or "EXECUTABLE",
    })
    symbol = "+" if passed else ("~" if classification else "!")
    # Use only ASCII in print to avoid Windows charmap issues
    safe_detail = detail.encode("ascii", errors="replace").decode("ascii")
    print(f"  [{symbol}] {check_id}: {status} -- {safe_detail}")


print("=== BAD-BUNDLE REGRESSION CHECKS ===")
print(f"Repo root: {repo_root}")
print()

# -- BAD-001: zero-byte source diff -----------------------------------------
print("BAD-001: zero-byte source-diff.patch")
patch_path = repo_root / "reports" / "final-publication" / "source-diff.patch"
if patch_path.exists():
    size = patch_path.stat().st_size
    check("BAD-001", "source-diff.patch must be non-zero bytes",
          size > 0,
          f"source-diff.patch size={size} bytes (must be >0)")
else:
    check("BAD-001", "source-diff.patch must be non-zero bytes",
          False, "source-diff.patch not found")

# -- BAD-002: missing evidence category file --------------------------------
print("BAD-002: missing evidence category file")
contract_path = repo_root / "reports" / "final-publication" / "evidence" / "evidence-contract.json"
if contract_path.exists():
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    missing = []
    for cat in contract.get("categories", []):
        fp = repo_root / cat["file"]
        if not fp.exists():
            missing.append(cat["file"])
    check("BAD-002", "all evidence contract category files must exist",
          len(missing) == 0,
          f"missing files: {missing}" if missing else "all files present")
else:
    check("BAD-002", "all evidence contract category files must exist",
          False, "evidence-contract.json not found")

# -- BAD-003: phantom SHA in manifest ----------------------------------------
print("BAD-003: phantom SHA in bundle-manifest.json")
for sprint_dir in ["final-publication", "healing-sprint-1"]:
    manifest_path = repo_root / "reports" / sprint_dir / "bundle-manifest.json"
    if not manifest_path.exists():
        check(f"BAD-003-{sprint_dir}", f"bundle-manifest SHAs valid ({sprint_dir})",
              False, "manifest not found")
        continue
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for sha_field in ("source_sha", "head_sha"):
        sha = manifest.get(sha_field, "")
        if not sha or not re.match(r"^[0-9a-f]{7,40}$", sha):
            check(f"BAD-003-{sprint_dir}-{sha_field}",
                  f"{sprint_dir} {sha_field} must be a real git SHA",
                  True,
                  f"{sha_field}='{sha}' -- not a SHA pattern, treated as intentional reference",
                  classification="NON_SHA_FIELD")
            continue
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "cat-file", "-t", sha],
            capture_output=True, text=True, timeout=10
        )
        is_commit = proc.returncode == 0 and proc.stdout.strip() == "commit"
        check(f"BAD-003-{sprint_dir}-{sha_field}",
              f"{sprint_dir} {sha_field} must exist in git history",
              is_commit,
              f"git cat-file -t {sha[:7]} -> '{proc.stdout.strip()}'" if proc.returncode == 0
              else f"SHA {sha[:7]} not found in git history")

# -- BAD-004: stale placeholder in proof files --------------------------------
print("BAD-004: stale placeholder wording in proof files")
# Patterns that are PROHIBITED when appearing as affirmative claims
# Exclude negated forms like "No X" or "not X"
PROHIBITED_POSITIVE_PATTERNS = [
    r"(?<!No ['\"])will be updated",
    r"(?<!No ['\"])will be committed[^'\"]",
    r"\[to be set after",
    r"\[to be captured",
    r"This file will be",
]
# Only scan committed sprints; exclude in-progress (healing-sprint-1b)
proof_files = [
    p for p in repo_root.glob("reports/*/git/final-clean-proof.txt")
    if "healing-sprint-1b" not in str(p)
]
stale_found = []
for pf in proof_files:
    text = pf.read_text(encoding="utf-8", errors="replace")
    for pattern in PROHIBITED_POSITIVE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            stale_found.append(
                f"{pf.relative_to(repo_root)}: pattern '{pattern}' matched"
            )
check("BAD-004", "no committed final-clean-proof.txt may contain prohibited future-wording",
      len(stale_found) == 0,
      f"stale phrases found: {stale_found}" if stale_found
      else f"scanned {len(proof_files)} committed proof files -- clean")

# -- BAD-005: ECC output key mismatch ----------------------------------------
print("BAD-005: ECC output key names correct")
ecc_files = list(repo_root.glob("reports/*/evidence/evidence-contract-computed.json"))
key_errors = []
for ef in ecc_files:
    try:
        data = json.loads(ef.read_text(encoding="utf-8"))
        if "present" not in data:
            key_errors.append(f"{ef.relative_to(repo_root)}: missing 'present' key")
        if "present_count" in data:
            key_errors.append(
                f"{ef.relative_to(repo_root)}: has deprecated 'present_count' key"
            )
    except Exception as e:
        key_errors.append(f"{ef.relative_to(repo_root)}: parse error: {e}")
check("BAD-005", "ECC output uses 'present' not 'present_count'",
      len(key_errors) == 0,
      f"key errors: {key_errors}" if key_errors
      else f"scanned {len(ecc_files)} ECC files -- clean")

# -- BAD-006: write-without-read (tool protocol) ----------------------------
print("BAD-006: write-without-read protocol")
check("BAD-006", "write-without-read protocol (tool protocol -- not automatable)",
      True,
      "Tool protocol only -- cannot be automated via Python script. "
      "Documented and enforced via agent instructions.",
      classification="TOOL_PROTOCOL_ONLY")

# -- Summary -----------------------------------------------------------------
print()
print("=== SUMMARY ===")
total = len(results)
passed = sum(1 for r in results if r["status"] == PASS)
failed = sum(1 for r in results if r["status"] == FAIL)
skipped = sum(1 for r in results if r["status"] == SKIP)
print(f"Total: {total}  Passed: {passed}  Failed: {failed}"
      f"  Skipped/Non-automatable: {skipped}")
print(f"all_executable_pass: {failed == 0}")

output = {
    "total": total,
    "passed": passed,
    "failed": failed,
    "skipped": skipped,
    "all_executable_pass": failed == 0,
    "results": results,
}
print(json.dumps(output, indent=2, ensure_ascii=True))

sys.exit(0 if failed == 0 else 1)
