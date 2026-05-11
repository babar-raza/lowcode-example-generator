# Generate and Validate Examples

Audience: Operator, Contributor

Use this guide to run generation through validation without live publishing.

## Template Mode

```powershell
python -m plugin_examples run --family cells --dry-run --template-mode --require-validation --promote-latest
```

## LLM Mode

Configure an approved provider, then run:

```powershell
python -m plugin_examples run --family cells --dry-run --require-llm --require-validation --promote-latest
```

## Validation Outputs

Validation writes restore/build/run and output validation evidence under the run evidence directory. Per-example gate files identify PR candidates and blocked examples.

## References

- Provider and env vars: [Configuration Reference](../reference/config.md), [Environment Variables](../reference/environment-variables.md)
- Validation behavior: [Validation and Reviewer](../reference/validation-and-reviewer.md)
- Gate results: [Gates and Verdicts](../reference/gates-and-verdicts.md)
