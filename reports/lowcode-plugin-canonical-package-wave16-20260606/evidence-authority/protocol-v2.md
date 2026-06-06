# Evidence Authority Protocol v2

**Sprint**: lowcode-plugin-canonical-package-wave16-20260606
**Date**: 2026-06-06
**Supersedes**: sidecar_proof_protocol_v1.1

## Problem with Protocol v1.1

Protocol v1.1 attempted to fix Wave 14's ZIP-contains-own-SHA contradiction by building the bundle first, then writing the closeout. However, it still allowed:
1. Bundle freeze while taskcards were still PENDING (6 pending in Wave 15 bundle)
2. The inside-bundle closeout (if any) could still claim to be the final SHA authority
3. No formal external attestation JSON with commit SHA + timestamp

## Protocol v2 — Two-Phase Evidence Authority

### Phase 1: Pre-Bundle (inside bundle)

All of the following must be COMPLETE before bundle creation:

- [ ] All sprint taskcards COMPLETE (0 PENDING)
- [ ] IV report written (IV_PASS or explicit PARTIAL)
- [ ] Adversarial review written (PASS or explicit issues)
- [ ] Pytest raw log captured
- [ ] Pre-bundle closeout written (labeled `PRE_BUNDLE_CLOSEOUT`)
  - The pre-bundle closeout MUST NOT claim final bundle SHA (SHA is not yet known)
  - It records: sprint verdict, package counts, validator counts, pytest counts, commit SHAs (feat only)
- [ ] Content manifest written (listing all files to be bundled)
- [ ] Content manifest hash computed

The bundle includes: taskcards, IV, adversarial review, pytest log, pre-bundle closeout, content manifest, lane ledgers, all validator reports, all package proofs, all state docs.

### Phase 2: Post-Bundle (outside bundle — external authority)

After bundle is frozen (bytes cannot change):

1. **Compute bundle SHA-256** from frozen bytes
2. **Write external .sha256 sidecar**:
   - `{sprint}.sha256`
   - Format: `{sha256}  {filename}`
3. **Write external final-attestation.json**:
   - `path`: absolute bundle path
   - `sha256`: bundle SHA-256
   - `size_bytes`: exact byte count
   - `entry_count`: ZIP entry count
   - `feat_commit`: feat commit SHA
   - `chore_commit`: chore commit SHA (recorded after chore commit; initially PENDING)
   - `sidecar_path`: absolute sidecar path
   - `timestamp`: ISO 8601
   - `protocol_version`: "v2"
4. **Chore commit**: stage attestation + sidecar + final taskcard closures
5. **Update final-attestation.json** with chore commit SHA (in-place, sidecar not rebuilt)

### Invariants

- The bundle SHA in external sidecar is the ONLY authoritative SHA
- Nothing inside the bundle claims to be the final SHA authority
- Inside-bundle closeout is explicitly labeled `PRE_BUNDLE_CLOSEOUT`
- Final verdict in external attestation is the sprint close authority
- IV cannot report final PASS while any current sprint taskcard is PENDING

### Validator: EAV-01..EAV-06

| Rule | Check |
|------|-------|
| EAV-01 | IV cannot be final PASS while sprint taskcards are PENDING |
| EAV-02 | Adversarial review cannot be final PASS while sprint taskcards are PENDING |
| EAV-03 | External .sha256 sidecar must exist and match bundle bytes |
| EAV-04 | External final-attestation.json must exist with all required fields |
| EAV-05 | Inside-bundle closeout must be labeled PRE_BUNDLE_CLOSEOUT, not FINAL |
| EAV-06 | Bundle entry count in attestation must match actual ZIP entry count |
