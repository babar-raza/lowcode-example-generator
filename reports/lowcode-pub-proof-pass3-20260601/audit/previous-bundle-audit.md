# Previous Bundle Audit

Sprint: lowcode-pub-proof-repair-pass2-20260601
Classification: LOWCODE_FINAL_PUBLICATION_PROOF_NEAR_COMPLETE_SIDECARE_IV_AND_COMMAND_REPAIR_REQUIRED

## Accepted
- ZIP SHA-256: cd88844851f08d7865101cb0d0845ace51e1b98b8e5ce7224ee699eb772b4c4c
- ZIP size: 219,159 bytes, entries: 340
- Decision board: 44 publish, 12 exclude
- E2E: 44/44 pub, 5/5 diag, FormImporter excluded
- Package artifacts: 44 directories
- pytest: 3222/18/0
- No static .pfx

## Rejected
1. reports/artifact/final-clean-proof.json missing from ZIP
2. reports/artifact/sidecar-verification.log missing from ZIP
3. No .sha256 or .size-count.json sidecar in uploaded evidence context
4. IV report missing (iv/independent-verification-report.md, iv/final-acceptance-matrix.md)
5. CMD-004 exit_code 1 (Python quoting error) — validators still claim pass
6. Command ledger lacks artifact build, sidecar, IV, publication dry-run commands
7. zip-file-list.txt omits itself
8. per-file-sha256.json omits artifact self-reference files without convention
