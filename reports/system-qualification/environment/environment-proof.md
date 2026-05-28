# Environment Proof

**Run ID:** sysqual-20260528-001
**Date:** 2026-05-28

## Python

| Item | Value |
|---|---|
| System Python | C:/Python313/python.exe (3.13.2) |
| Repo .venv | .venv/Scripts/python.exe (created this sprint) |
| jsonschema | Available (via .venv) |
| PyYAML | Available (system + .venv) |

**Note:** System Python has no write permission to site-packages. .venv created fresh.

## .NET

| Item | Value |
|---|---|
| dotnet version | 10.0.204 |
| Available SDKs | 9.0.200, 10.0.204 |
| DllReflector | BUILT (tools/DllReflector/DllReflector.csproj, Release) |

## NuGet

| Item | Value |
|---|---|
| Source | nuget.org (https://api.nuget.org/v3/index.json) |
| Access | CONFIRMED (packages downloaded during E2E runs) |

## Environment Verdict

READY — All required components available.
