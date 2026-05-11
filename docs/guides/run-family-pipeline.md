# Run a Family Pipeline

Audience: Operator

Use this guide to run the pipeline for one family and inspect its evidence.

## Steps

1. Install the package.

```powershell
pip install -e .
```

2. Build the reflector.

```powershell
dotnet build tools/DllReflector/DllReflector.csproj -c Release
```

3. Run a dry-run family pipeline.

```powershell
python -m plugin_examples run --family cells --dry-run --promote-latest
```

4. Inspect the report and gate verdict.

```powershell
Get-ChildItem workspace/runs -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

## References

- All flags: [CLI Reference](../reference/cli.md)
- Evidence files: [File Contracts](../reference/file-contracts.md)
- Verdict meanings: [Gates and Verdicts](../reference/gates-and-verdicts.md)
