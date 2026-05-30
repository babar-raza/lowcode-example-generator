# Fallback Review Policy — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## When Fallback Review Applies
When LLM-based reviewer is unavailable or score is below threshold,
deterministic fallback review checks:

1. Canonical provenance: example was generated through pilot_run.py pipeline
2. Main-class coverage: Program.cs calls at least one LowCode main-class method
3. No stubs/no-op: No forbidden patterns (no suitable overload, TODO, stub)
4. Output validation: output file exists and is non-empty
5. README correctness: README.md exists and references the correct class
6. Package completeness: Program.cs + .csproj + README.md + example.manifest.json exist
7. Fixture correctness: All input_files from manifest exist in example directory
8. Forbidden patterns: No banned comment patterns
9. Idempotency: canonical_packager produces identical output across runs
10. Duplicate cleanup: No duplicate slugs in package output
