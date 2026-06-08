# Live Repo Validator Rules — lowcode-final-verify-20260603

## V01: Example Count Match
Each family's live repo contains exactly the expected number of examples.
- cells: 9, diagram: 2, email: 1, pdf: 20 (19 ours + 1 pre-existing), slides: 3, words: 9

## V02: No Excluded Example Leak
Excluded examples (email/email-converter, slides/for-each, slides/slides-*) do NOT appear in any live repo.

## V03: Build Success
All 44 examples build successfully (`dotnet build` exit code 0).

## V04: Run Success
All 44 examples run successfully (`dotnet run` exit code 0).

## V05: No Static Certificate Files
Zero .pfx/.p12/.key/.pem/.cer/.crt files exist in any live repo.

## V06: No Duplicate .csproj
Each example directory contains exactly one .csproj file.

## V07: No bin/obj Artifacts
No bin/ or obj/ directories committed to any live repo.

## V08: README Completeness
Each family README lists all examples with correct paths.

## V09: Directory.Packages.props Present
Each repo root contains Directory.Packages.props with correct Aspose package version.

## V10: Directory.Build.props Present
Each repo root contains Directory.Build.props.

## V11: global.json Present
Each repo root contains global.json specifying .NET SDK version.

## V12: Branch Hygiene
All repos have exactly 1 branch (main), 0 open PRs.

## V13: Command Ledger Completeness
Every restore/build/run command has a corresponding stdout-stderr log file.

## V14: Aggregate Consistency
Build aggregate and E2E aggregate are derived from the same single run (no carryforward).

## V15: FormImporter Upstream Bug Documented
FormImporter is classified UPSTREAM_BUG with minimal repro, retry plan, and version probe.

## V16: No Unauthorized Remote Mutations
Only README-fix PRs (#24 pdf, #4 email, #4 slides) were created/merged this sprint.
