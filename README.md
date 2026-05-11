# lowcode-example-generator

Pipeline repository for generating, validating, and publishing SDK-style C# examples for Aspose .NET plugin APIs, including LowCode and Plugins namespaces.

Published examples live in separate family-specific example repositories. This repository contains the pipeline, configuration, schemas, tests, prompts, and operational tooling.

## Documentation

Start with the docs landing page:

- [Documentation Home](docs/README.md)
- [Product Overview](docs/overview/product.md)
- [Operator Quickstart](docs/getting-started/operator-quickstart.md)
- [Contributor Quickstart](docs/getting-started/contributor-quickstart.md)

## Common Workflows

Run a dry-run pipeline:

```powershell
python -m plugin_examples run --family cells --dry-run --promote-latest
```

Run source-of-truth discovery:

```powershell
python -m plugin_examples discover-lowcode --family cells --promote-latest
```

Run local tests:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/unit -v --timeout=60
python -m compileall src
dotnet build tools/DllReflector/DllReflector.csproj -c Release
```

## Canonical References

- [CLI Reference](docs/reference/cli.md)
- [Configuration Reference](docs/reference/config.md)
- [File Contracts](docs/reference/file-contracts.md)
- [Gates and Verdicts](docs/reference/gates-and-verdicts.md)
- [Validation and Reviewer](docs/reference/validation-and-reviewer.md)
- [Publishing and GitHub](docs/reference/publishing-and-github.md)

## Governance

- Code and schemas are the source of truth.
- Official NuGet packages are authoritative for API symbols.
- Generation must not proceed without source-of-truth proof.
- Publishing is pull-request based; no direct push to `main`.
- Live PR creation and merge require separate approval tokens.
- Evidence must be recorded for successful, partial, and failed runs.

See [Architecture Decisions](docs/architecture/decisions.md).
