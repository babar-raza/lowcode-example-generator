# Post-Publication Validator Rules — lowcode-post-pub-monitor-20260603

These validators enforce invariants that must hold after publication. Any failure triggers
the verdict LOWCODE_POST_PUBLICATION_REPAIR_REQUIRED.

## V01: README Lists All Examples
FAIL if any published example directory name is absent from its repo's README.md.
Checked via: case-insensitive grep of each example name against README content.

## V02: Program.cs and .csproj Present
FAIL if any published example directory lacks exactly one Program.cs and exactly one .csproj.

## V03: No Static Certificate Files
FAIL if any .pfx, .p12, .key, .pem, .cer, or .crt file is committed to any repo.

## V04: Diagram Converter Output
FAIL if `diagram/diagram-converter` produces no output file on `dotnet run`.

## V05: Timestamp Environment Documentation
FAIL if pdf/timestamp lacks a comment or documentation noting TSA server dependency.
Currently: Program.cs contains inline comment about FreeTSA.org.

## V06: FormImporter Retry Status Current
FAIL if `upstream-bug-status.md` last-checked date is more than 7 days old.
Current: checked 2026-06-03 (today).

## V07: No Publication Branch After Merge
FAIL if any repo has branches other than `main`.

## V08: No Carryforward E2E Without Proof
FAIL if E2E aggregate references a prior sprint without a no-change SHA proof.
Current patrol: fresh clones from main, same SHAs as final-verify.
