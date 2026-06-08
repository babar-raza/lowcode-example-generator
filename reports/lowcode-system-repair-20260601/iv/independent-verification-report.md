# Independent Verification Report — lowcode-system-repair-20260601

## E2E Verification
- E2E runner: scripts/run_system_repair_e2e.py
- Result: 49/49 PASS, 0 failures
- Per-example logs: reports/.../e2e/<family>/<example>/{restore,build,run}.log + command.json
- Both e2e-aggregate.json and e2e-aggregate-v2.json are IDENTICAL (single source of truth)
- **Challenge**: Are raw logs consistent with aggregate? YES — all command.json files show e2e_pass=true

## pytest Verification
- Command: .venv/Scripts/python.exe -m pytest tests/ -x --tb=short
- Result: 3222 passed, 18 skipped, 0 failed
- Raw log: reports/.../tests/full-pytest.log
- Summary: reports/.../tests/full-pytest-summary.json
- **Challenge**: Is the raw log present and complete? YES — 362.20 seconds, exit code 0

## PFX Verification
- git ls-files '*.pfx' returns EMPTY — no tracked PFX files
- words/signer and pdf/signature generate PFX at runtime via RSA.Create(2048)
- Runtime PFX files are ephemeral artifacts, not packaged
- **Challenge**: Could runtime PFX leak into package? Only if committed, which is prevented

## Format Authority Verification
- 42 types across 6 families (9+2+1+19+3+8)
- manifest.json matches actual contract counts
- No companion helpers (Signer, ForEach) in format-authority
- **Challenge**: Does E2E count (49) match denominator? YES — 42 main + 2 companion + 1 env-dep + 4 duplicates = 49

## Blocker Verification
- FormImporter: UPSTREAM_BUG — builds but NullReferenceException in Process()
- Timestamp: ENVIRONMENT_DEPENDENT_PASS — works with TSA server
- Words Processor: PERMANENTLY_BLOCKED — no public constructor
- Words OFD: UNSUPPORTED_FORMAT — not a supported output format
- Words Signer: NOT_A_LOWCODE_MAIN_CLASS — no LowCode.Signer class
- Slides ForEach: NON_RUNNABLE_HELPER — utility iterator
- Cells SpreadsheetPrinter: NOT_IN_API_CATALOG — doesn't exist
- **Challenge**: Is FormImporter correctly classified? YES — probe builds, reflection confirms API, but runtime crashes

## PDF Namespace Verification
- `Aspose.Pdf.LowCode` IS VALID in Aspose.PDF 26.5.0
- Previous sprint claim of "invalid namespace" was WRONG
- 21 classes confirmed in namespace via DLL binary search and reflection
- **Challenge**: Why did previous probes fail? They used Aspose.PDF 25.4.0 which doesn't have LowCode namespace

## Version Verification
- versions_intentionally_differ=true (not false agreement)
- Build versions documented per family
- **Challenge**: Any version confusion? Explicitly modeled now

## Publication Verification
- Both gates NOT_SET
- No git push, no PR creation, no merge
- **Challenge**: Could accidental push occur? No — gates checked before any remote operation

## Artifact Verification
- ZIP built via 2-pass process
- Sidecar SHA/size/count written
- **Challenge**: Does sidecar match ZIP? VERIFIED at build time

## Adversarial Findings
1. PDF FormImporter is a real API that could work in a future version — monitor Aspose.PDF releases
2. Timestamp depends on public TSA — could fail if DigiCert changes endpoint
3. 4 duplicate package entries could cause confusion — consider removing duplicates from packages
4. Words Signer companion uses DigitalSignatures namespace (not LowCode) — README must be clear

## Overall IV Verdict
PASS — all local gates verified, no evidence defects found.
