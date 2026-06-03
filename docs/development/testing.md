# Testing and CI

Audience: Contributor

## Local Checks

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/unit -v --timeout=60
python -m compileall src
dotnet build tools/DllReflector/DllReflector.csproj -c Release
```

```bash
# bash / Linux / macOS
PYTHONPATH=src python3 -m pytest tests/unit -v --timeout=60
python3 -m compileall src
dotnet build tools/DllReflector/DllReflector.csproj -c Release
```

## CI

`.github/workflows/build-and-test.yml` runs:

- Python 3.12 and 3.13 unit tests.
- `python -m compileall src`.
- DllReflector build with .NET 8.0.

`.github/workflows/monthly-package-refresh.yml` runs monthly pipeline refresh and published build regression.

## Test Coverage Areas

- Family config and schemas.
- NuGet fetch/dependency resolution.
- Extraction/reflection/plugin detection.
- Scenario planning/generation/validation.
- Gates/lifecycle/evidence.
- Publishing/README/release status.
- Metrics.
