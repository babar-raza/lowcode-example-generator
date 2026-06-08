# Public vs Internal Artifact Policy

## Public (committed to target repo PR)
- Program.cs
- <slug>.csproj
- example.manifest.json
- expected-output.json
- README.md (per-example)
- README.md (root, examples index)
- Directory.Packages.props
- Directory.Build.props
- global.json
- .gitignore
- .github/workflows/build.yml
- Input fixture files (e.g. input.docx, minimal.dxf)

## Internal evidence (sprint reports only, NOT committed to target repo)
- output-validation.json — sprint proof, not public contract
- restore.log / build.log / run.log
- source-provenance.json
- package-proof-log.json
- fixture-validation reports

## Rationale
`output-validation.json` records eval-mode watermarks, truncated output values, and sprint-specific
probe metadata. Publishing it would expose internal pipeline mechanics. `expected-output.json` is
the clean public contract stating what the example produces.
