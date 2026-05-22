# Companion Proof & Manifest Repair — Sprint 50

## Root Cause
Sprint 49 manually built ZIP, manifest, and companion proof instead of using `build_evidence_bundle()`.

## Fix
- Use `build_evidence_bundle()` which correctly:
  - Uses `sha256-manifest.txt` with `SELF` marker (no circular hash)
  - Writes `evidence-contract-validation.json` **outside** the ZIP
  - Validates the actual final ZIP and records its exact SHA256
  - Excludes `.zip` and `.validation.json` files from evidence input
- Added 3 new tests (10 total, all pass)

## Tests Added
1. `test_companion_sha_matches_final_zip` — companion SHA == actual ZIP SHA
2. `test_companion_not_inside_zip` — validation file not in ZIP entries
3. `test_manifest_self_hash_not_circular` — manifest uses SELF, not a hash
