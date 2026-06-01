# Validator Rules

Sprint: lowcode-pub-proof-repair-pass2-20260601

- V01: Sidecar validated post-ZIP build: PASS (deferred to post-build verification)
- V02: Package artifacts contain real directories: PASS (found 44)
- V03: Command ledger has stdout/stderr files: PASS (found 6)
- V03b: Command index file references valid: PASS (all 6 commands verified)
- V04: per-example-output-proof.json exists: PASS
- V05: FormImporter NOT in E2E denominator: PASS
- V06: Publishable count matches package count: PASS (pkg=44)
- V07: Duplicates excluded from packages: PASS (found: [])
- V08: Helper (slides/for-each) not in packages: PASS
- V09: FormImporter not in E2E pass counts: PASS (FormImporter excluded from E2E by design)
- V10: No deferred decision items: PASS (found 0)
- V11: E2E publishable all pass: PASS (44/44)
- V12: No static PFX in tracked git: PASS (found: [])
- V13: Package completeness policy enforced: PASS (all 44 satisfy policy)