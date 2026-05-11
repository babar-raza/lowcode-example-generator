# Run a Discovery Sweep

Audience: Operator, Contributor

Discovery checks whether configured families expose plugin/LowCode namespaces without running full generation.

## Single Family

```powershell
python -m plugin_examples discover-lowcode --family cells --promote-latest
```

## Multiple Families

```powershell
python -m plugin_examples discover-lowcode --families cells words pdf --rank --promote-latest
```

## Outputs

Discovery writes aggregate and family evidence under `workspace/verification/latest/`.

## References

- [CLI Reference](../reference/cli.md)
- [Configuration Reference](../reference/config.md)
- [File Contracts](../reference/file-contracts.md)
