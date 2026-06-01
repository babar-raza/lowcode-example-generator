# Package Artifact Replay Proof

Sprint: lowcode-pub-proof-repair-pass2-20260601

## Policy: COMPLETE_PACKAGE_ARTIFACT
Each package includes: Program.cs, .csproj, example.manifest.json.
If source has README.md: copied. If source has expected-output.json: copied.
Otherwise: result_classification recorded in manifest.

## Results
- Total packaged: 44
- Main class: 42
- Companion: 1
- Environment dependent: 1
- With README.md: 43
- With expected-output.json: 43
- Without expected-output (classified): 1

## Completeness
All 44 packages satisfy the COMPLETE_PACKAGE_ARTIFACT policy.
