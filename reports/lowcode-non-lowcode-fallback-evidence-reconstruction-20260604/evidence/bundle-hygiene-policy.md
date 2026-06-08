# Evidence Bundle Hygiene Policy

## Excluded Artifact Types

| Pattern | Reason |
|---------|--------|
| bin/ directories | Compiled output; not source evidence |
| obj/ directories | Build intermediates |
| *.dll | NuGet package binaries; large; not source |
| *.exe | Compiled executables |
| *.pdb | Debug symbols |
| *.nupkg | NuGet package archives |
| __pycache__/ | Python bytecode cache |
| *.pyc | Compiled Python bytecodes |
| .local/cache/ | NuGet download cache |
| .local/reflection-runs/ | Extracted DLL artifacts |

## Included Artifact Types

| Pattern | Reason |
|---------|--------|
| *.py | Python source (implementation + tests) |
| *.cs | C# probe source |
| *.csproj | Probe project files |
| *.json | Config, schema, registry, pilot results |
| *.yaml / *.yml | Family config, registry entries |
| *.log | Raw test/command output |
| *.md | Reports and documentation |
| *.patch | Git diffs |
| probe-output.png (<=100KB) | Probe output proof |
| probe-output.jpg (<=100KB) | Probe output proof |
| *.sha256, *.size, *.count | Bundle sidecars (outside ZIP only) |
