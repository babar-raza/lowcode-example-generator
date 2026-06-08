# Post-Merge Validator Rules

- V01: All 6 repos have examples on main — PASS
- V02: README.md present in all 6 repos — PASS
- V03: No duplicate .csproj files — PASS (repaired via 5 follow-up PRs)
- V04: No static .pfx in any repo — PASS (repaired via 2 follow-up PRs)
- V05: All input files have CopyToOutputDirectory — PASS (repaired via 2 follow-up PRs)
- V06: Fresh main-branch E2E 44/44 — PASS
- V07: No excluded examples leaked to main — PASS
- V08: All source branches deleted — PASS
- V09: No dangling branches — PASS (all repos main-only)
- V10: No open PRs remain — PASS
- V11: Environment-dependent examples documented — PASS (pdf/timestamp, pdf/signature)
- V12: Diagram Converter output verified — PASS (exit=0, creates files)
- V13: FormImporter upstream-bug retry plan — PASS (Aspose.PDF 26.5.0, no newer version)
- V14: No carryforward-only E2E — PASS (fresh E2E from cloned main)
- V15: All follow-up repairs verified via rerun — PASS
