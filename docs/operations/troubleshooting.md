# Troubleshooting

Audience: Operator, Contributor

## Source-of-Truth Failure

Check:

- Family config under `pipeline/configs/families/`
- NuGet package availability
- Reflection output under the run catalog directory
- `{family}-source-of-truth-proof.json`

## Build or Runtime Failure

Check:

- `validation-results.json`
- `runtime-failure-classifications.json`
- `repair-attempts.json`
- Generated project under `workspace/runs/{run_id}/generated/`

## Reviewer Unavailable

Check:

- `EXAMPLE_REVIEWER_PATH`
- `reviewer-preflight.json`
- `reviewer-results.json`

## Publishing Blocked

Check:

- `gate-results.json`
- `publish-readiness` evidence
- repo access and permission probe evidence
- approval token value
- `GITHUB_TOKEN`

References:

- [File Contracts](../reference/file-contracts.md)
- [Gates and Verdicts](../reference/gates-and-verdicts.md)
- [Validation and Reviewer](../reference/validation-and-reviewer.md)
