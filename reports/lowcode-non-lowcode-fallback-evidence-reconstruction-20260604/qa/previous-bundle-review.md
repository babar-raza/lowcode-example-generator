# Previous Bundle QA Review

Bundle: non-lowcode-fallback-implementation-20260604.zip
QA Date: 2026-06-04
QA Verdict: NON_LOWCODE_FALLBACK_IMPLEMENTATION_PROGRESS_REAL_BUT_EVIDENCE_RECONSTRUCTION_REQUIRED

## Accepted Progress

- BarCode probe project (Program.cs + csproj) exists; probe-output.png 17210 bytes produced
- Imaging probe project (Program.cs + csproj) exists; probe-output.jpg 1075 bytes from programmatic PNG fixture
- Negative-control pilot correctly blocked hallucinated NonExistentConverter via HallucinationValidator
- NuGet availability proof exists for 20 families (nuget-availability-proof.json)
- Pilot directory structure with catalog/reflection/candidate inputs exists

## Rejected Findings

### CONTR-EV-001: Source files absent from bundle (CRITICAL)
ZIP contains 117 entries, 0 of which are Python source (src/) or test (tests/) files.
All implementation claims (94 new tests, 14 NL-V rules, heuristic matcher, probe generator,
AI acceleration module, runner fallback stage) cannot be verified from bundle contents.

### CONTR-EV-002: Raw test logs absent (CRITICAL)
Only summary counts reported (e.g., "3316 passed"). No actual pytest --tb=short output
captured per test file. Cannot verify which tests ran, which passed, or actual test names.

### CONTR-EV-003: Command ledger is hand-written (HIGH)
commands/raw-commands.log contains representative prose, not real command output.
No commands/stdout-stderr/ directory. No command-index.json.
Cannot verify that dotnet restore/build/run actually executed.

### CONTR-EV-004: 22 compiled binaries in ZIP (HIGH)
bin/, .dll, .exe, .pdb files from probe build output included.
Evidence bundles should contain source and logs, not compiled artifacts.

### CONTR-EV-005: source-bundle-manifest.json incomplete (HIGH)
Manifest covers only reports/ evidence files. Does not include actual source implementation.
SHA hashes for source files cannot be verified.

### CONTR-EV-006: Pilots hand-written (HIGH)
Pilot JSON (catalog-input.json, reflection-input.json, etc.) manually authored.
Not produced by running actual Python modules. No pilot replay from source.

### CONTR-EV-007: No git diff proof (MEDIUM)
No source-diffs.patch or changed-files-list.json proving which files changed.
