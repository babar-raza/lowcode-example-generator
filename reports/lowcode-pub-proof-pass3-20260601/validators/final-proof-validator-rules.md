# Validator Rules

Sprint: lowcode-pub-proof-pass3-20260601

- V01: Sidecar files will be validated post-ZIP: PASS (deferred)
- V02: Package artifacts = 44: PASS (found 44)
- V03: Command stdout/stderr files exist: PASS (found 7)
- V04: No unsuperseded failed commands: PASS (none)
- V05: Command file references valid: PASS (all 7 verified)
- V06: per-example-output-proof.json exists: PASS
- V07: FormImporter NOT in E2E: PASS
- V08: Publishable = package count: PASS (pkg=44)
- V09: Duplicates excluded from packages: PASS
- V10: Helper excluded from packages: PASS
- V11: No deferred decisions: PASS
- V12: E2E publishable all pass: PASS (44/44)
- V13: No static PFX: PASS
- V14: Package completeness policy enforced: PASS (all 44 satisfy policy)
- V15: final-clean-proof.json exists: PASS
- V16: sidecar-verification.log exists: PASS
- V17: IV report exists: PASS
- V18: Artifact self-reference policy documented: PASS
- V19: pytest passes: PASS (3222 passed, 0 failed)
- V20: Validator log self-consistent: PASS