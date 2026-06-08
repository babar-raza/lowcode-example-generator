# Previous Bundle Audit — lowcode-final-publication-20260601-evidence.zip

## Identity
- SHA-256: 27fe17fc7525b476bc416b8f2fdc5e36fe859f668ae318b8e3fb9e806c56810f
- Size: 202,894 bytes | Entries: 338

## Classification
LOWCODE_PUBLICATION_DECISION_ACCEPTED_ARTIFACT_AND_PACKAGE_PROOF_REPAIR_REQUIRED

## Accepted
- 56/56 final decisions made, zero human-deferred
- Publishable model: 42 main + 1 companion + 1 env-dep = 44
- Exclusion model: 4 dup + 3 not-main + 2 unsup-fmt + 1 helper + 1 no-catalog + 1 upstream-bug = 12
- pytest 3222 passed, 18 skipped, 0 failed
- Static PFX absent from ZIP
- FormImporter upstream bug classification plausible
- Words Signer companion classification plausible
- Slides ForEach non-runnable helper exclusion plausible
- Timestamp environment-dependent publish plausible

## Rejected / Still Not Final
1. Artifact metadata inside ZIP does not match actual uploaded ZIP (internal has pass-1/pass-2 values)
2. package-artifacts contains only manifest, not actual package directories or archives
3. Central command ledger is summary-style, lacks stdout/stderr files
4. E2E denominator says 49 = 44 + 4 dup + 1 upstream-bug, but actual E2E = 44 + 4 dup + slides/for-each. FormImporter NOT in E2E.
5. output-validation proof embedded in e2e-aggregate but no separate per-example-output-proof.json
6. Publication readiness not final until package + sidecar protocol self-consistent
