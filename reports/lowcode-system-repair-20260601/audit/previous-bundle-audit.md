# Previous Bundle Audit — lowcode-true-closure-20260531-evidence.zip

## Bundle Identity
- Sprint: lowcode-true-closure-20260531
- SHA-256: 2ef9f2af6e3466d1710c7954f41fa849259373e5ea905f1a0cee9f743ba93dd9
- Size: 172,164 bytes
- Entries: 270
- HEAD at build: f727b0266b43949f97a8d7a199ab0d02645fe74e

## Rejection Verdict
LOWCODE_TRUE_CLOSURE_ATTEMPT_REJECTED_E2E_PACKAGE_FIXTURE_AND_SYSTEM_INTEGRATION_REPAIR_REQUIRED

## Accepted Claims
1. Words Signer classification investigation — SignerContext is CONTEXT_MODEL, no LowCode.Signer class
2. Slides ForEach classification investigation — NON_RUNNABLE_HELPER utility iterator
3. Words Processor reflection evidence — abstract/base/non-instantiable type (CS1729 + CS0120)
4. Words OFD investigation — LowCode Converter does not support OFD output
5. Static PFX risk was detected by a validator
6. Command ledger improved to 105 commands

## Rejected Claims
1. Final closure not accepted — system integration not proven
2. Artifact metadata does not match actual uploaded ZIP
3. E2E contradiction: e2e-aggregate.json = 40/49 pass (9 fail); e2e-aggregate-v2.json = 49/49 pass
4. Raw build logs contradict e2e-aggregate-v2.json claims for PDF examples
5. PDF examples fail with MSB1011 — multiple .csproj files in same directory
6. No full pytest raw log or summary bundled
7. No full package-artifacts or generated-source snapshots bundled
8. Static test-cert.pfx remains in signer package despite runtime-only PFX policy
9. Validator matrix includes failure for static PFX
10. PDF FormImporter and Timestamp probes use invalid namespace (Aspose.Pdf.LowCode)
11. package-artifacts/ effectively missing from bundle
12. Cannot support approval-only publication with these defects

## Specific Contradictions
| ID | Category | Description | Severity |
|----|----------|-------------|----------|
| RC-001 | E2E | e2e-aggregate.json 40/49 vs e2e-aggregate-v2.json 49/49 | CRITICAL |
| RC-002 | PACKAGE | PDF dirs have duplicate .csproj causing MSB1011 | CRITICAL |
| RC-003 | FIXTURE | Static test-cert.pfx in signer package | HIGH |
| RC-004 | BLOCKER | PDF FormImporter probe uses nonexistent Aspose.Pdf.LowCode | HIGH |
| RC-005 | BLOCKER | PDF Timestamp probe uses nonexistent Aspose.Pdf.LowCode | HIGH |
| RC-006 | EVIDENCE | No full pytest raw log in bundle | MEDIUM |
| RC-007 | EVIDENCE | package-artifacts/ missing from bundle | MEDIUM |
| RC-008 | ARTIFACT | Artifact metadata may not match ZIP | MEDIUM |
| RC-009 | VERSION | versions_agree=true while catalog 26.5.0 != build 25.5.0 | LOW |
