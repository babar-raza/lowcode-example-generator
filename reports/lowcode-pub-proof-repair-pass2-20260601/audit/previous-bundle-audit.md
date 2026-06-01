# Previous Bundle Audit

Sprint: lowcode-pub-proof-repair-20260601
Classification: LOWCODE_FINAL_PUBLICATION_PROOF_NEAR_COMPLETE_ARTIFACT_COMMAND_AND_PACKAGE_COMPLETENESS_REPAIR_REQUIRED

## Accepted
- ZIP SHA-256: c9c97cdf52db40b131034d6bda07dbfd7227d5b6fcb5eab0310976f8c6c25f22
- ZIP size: 196,948 bytes
- ZIP entries: 260
- 56/56 decision-board items decided
- Zero human-deferred items
- Decision model: 42 main + 1 companion + 1 env-dep = 44 pub, 12 excluded
- E2E: 44/44 pub, 5/5 diag, 49/49 combined, FormImporter excluded
- per-example-output-proof.json exists
- 44 package artifact directories exist
- No static .pfx
- pytest: 3222/18/0
- Publication matrix: 44 candidates

## Rejected
1. Sidecar/final-clean-proof mismatch: claims f3b6c307..., 150,057 bytes, 230 entries vs actual c9c97cdf..., 196,948 bytes, 260 entries
2. V03 validator FAIL: command ledger found 0 stdout/stderr files
3. IV/acceptance matrix claim validators pass despite V03 failure
4. Command stdout/stderr files are snippets, not full raw output
5. Package artifacts minimal: no README.md or expected-output.json
6. Artifact may have been changed after sidecar computation
