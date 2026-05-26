# Generate and Validate Examples

Audience: Operator, Contributor

Use this guide to run generation through validation without live publishing.

## Template Mode

```powershell
python -m plugin_examples run --family cells --dry-run --template-mode --require-validation --promote-latest
```

## LLM Mode

Configure the governed professionalize endpoint and model first. Do not substitute OpenAI, Azure OpenAI, Ollama, or any other endpoint for live generation.

```powershell
$env:GPT_OSS_ENDPOINT = "https://llm.professionalize.com/v1/"
python -m plugin_examples run --family cells --dry-run --require-llm --require-validation --promote-latest
```

## Validation Outputs

Validation writes restore/build/run and output validation evidence under the run evidence directory. Per-example gate files identify PR candidates and blocked examples.

## References

- Provider and env vars: [Environment Variables](../reference/environment-variables.md)
- Config behavior: [Configuration Reference](../reference/config.md)
- Validation behavior: [Validation and Reviewer](../reference/validation-and-reviewer.md)
- Gate results: [Gates and Verdicts](../reference/gates-and-verdicts.md)
