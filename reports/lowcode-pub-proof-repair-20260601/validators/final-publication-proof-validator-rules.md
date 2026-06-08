# Validator Rules

- V01: Sidecar file will be validated post-ZIP: PASS (deferred to post-build)
- V02: Package artifacts contain real directories: PASS (found 44)
- V03: Command ledger has stdout/stderr files: FAIL (found 0)
- V04: per-example-output-proof.json exists: PASS
- V05: E2E denominator does not claim FormImporter in 49: PASS
- V06: Publishable count matches package count: PASS (pkg=44)
- V07: Duplicates excluded from packages: PASS (found: [])
- V08: Helper (slides/for-each) not in packages: PASS
- V09: FormImporter not in E2E pass counts: PASS (FormImporter excluded from E2E by design)
- V10: No deferred decision items: PASS (found 0)
- V11: E2E publishable all pass: PASS (44/44)
- V12: No static PFX in tracked git: PASS (found: [])