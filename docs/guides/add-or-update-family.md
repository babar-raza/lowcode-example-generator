# Add or Update a Family

Audience: Contributor

Use this guide when adding or changing `pipeline/configs/families/{family}.yml`.

## Steps

1. Start from `pipeline/configs/families/_templates/family-template.yml`.
2. Set `family`, `display_name`, `enabled`, and `status`.
3. Configure NuGet package resolution under `nuget`.
4. Configure plugin namespace patterns under `plugin_detection.namespace_patterns`.
5. Configure official example and publish target repositories under `github`.
6. Configure fixture and existing example sources.
7. Set generation, validation, LLM, and optional template hints.
8. Run focused tests.

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/unit/test_family_config.py tests/unit/test_denominator_model.py -q
```

## References

- Full key list: [Configuration Reference](../reference/config.md)
- Schemas: [Schemas and Contracts](../reference/schemas-and-contracts.md)
- Discovery verification: [Run a Discovery Sweep](discovery-sweep.md)
