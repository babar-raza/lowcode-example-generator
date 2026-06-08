# Public vs Internal Artifact Policy

Date: 2026-06-08

## Public Contract Files (committed to target repo)
These files ARE pushed to public example repos and are part of the published contract:
- `Program.cs` — the executable example
- `<slug>.csproj` — project configuration
- `README.md` — per-example documentation
- `example.manifest.json` — public API contract (inputs, outputs, namespace_source)
- `expected-output.json` — expected output contract for consumers
- Input fixtures (if small, safe, and provenance-documented)

## Internal Evidence Files (sprint evidence; NOT public contract replacements)
These files are generated as sprint evidence and may be committed to target repo for CI:
- `output-validation.json` — sprint proof that example ran; MUST coexist with expected-output.json

## Rule: output-validation.json Cannot Replace expected-output.json
If `output-validation.json` exists but `expected-output.json` does not, PPV-06 fails.
Both must be present if `output-validation.json` is included.
