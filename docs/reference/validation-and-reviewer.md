# Validation and Reviewer

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/runner.py`, `src/plugin_examples/verifier_bridge/`

Last verified from audit: 2026-05-25

## Dotnet Validation

Generated projects are validated through:

1. `dotnet restore`
2. `dotnet build`
3. `dotnet run`, unless `--skip-run` is set
4. stdout/stderr output validation
5. semantic output file validation when an output file contract exists

Validation results are written to `validation-results.json`.

## Output Validation

The output validator checks stdout/stderr and semantic output files.

Supported semantic file checks include:

- Text
- JSON
- HTML
- PDF
- Image
- XLSX
- OOXML document formats such as DOCX and PPTX
- OLE2 formats such as DOC and XLS
- EML
- MSG

Expected output constraints can come from generated `expected-output.json` files.

## External Example Reviewer

Reviewer integration uses:

- `src/plugin_examples/verifier_bridge/reviewer_preflight.py`
- `src/plugin_examples/verifier_bridge/bridge.py`

The reviewer path is resolved from `EXAMPLE_REVIEWER_PATH` or explicit bridge arguments where provided.

Reviewer evidence:

- `reviewer-preflight.json`
- `reviewer-results.json`

## Fixture and Reviewer Boundary

Fixture discovery is part of pipeline planning and evidence collection. The external reviewer is a later validation gate. Do not treat reviewer fixture notes as source-of-truth API evidence; source-of-truth API symbols come from reflected NuGet catalogs.

Fixture and example mining evidence is documented in [File and Evidence Contracts](file-contracts.md).

## Required vs Degraded Behavior

CLI flags can require validation or reviewer availability:

- `--require-validation`
- `--require-reviewer`

If a later optional stage fails and the corresponding requirement flag is not set, the runner can mark the stage degraded instead of hard-failing the run. Hard-stop stage behavior is documented in [Gates and Verdicts](gates-and-verdicts.md).

## Related Pages

- [CLI Reference](cli.md)
- [Gates and Verdicts](gates-and-verdicts.md)
- [File and Evidence Contracts](file-contracts.md)
