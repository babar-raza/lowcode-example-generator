# Contributor Quickstart

Audience: Contributor

## Install

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

```bash
# bash / Linux / macOS
python3 -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run Tests

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

## Find the Main Code Surfaces

- CLI: `src/plugin_examples/__main__.py`
- Pipeline runner: `src/plugin_examples/runner.py`
- Family config schema: `pipeline/schemas/family-config.schema.json`
- Family configs: `pipeline/configs/families/`
- Validation bridge: `src/plugin_examples/verifier_bridge/`
- Gates: `src/plugin_examples/gates/`

## Contributor References

- [Repository Structure](../development/repo-structure.md)
- [Testing and CI](../development/testing.md)
- [System Design](../architecture/system-design.md)
- [Configuration Reference](../reference/config.md)
