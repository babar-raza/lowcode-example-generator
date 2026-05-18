# OCR LowCode Discovery Blocker — Escalation Package

**Sprint:** sprint36
**Date:** 2026-05-18
**Blocker:** Aspose.AI.LLM private assembly not on NuGet.org

## Summary

Aspose.OCR 26.5.0 is available on NuGet, but its LowCode namespace
(if any) cannot be discovered because `Aspose.AI.LLM` is a required
dependency that is not published to NuGet.org.

## Repro

```
curl https://api.nuget.org/v3-flatcontainer/aspose.ai.llm/index.json
# Returns: HTTP 404 Not Found
```

Reflection command:
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples discover-lowcode --family ocr
# Error: Unable to resolve Aspose.AI.LLM dependency
```

## Request to Aspose Team

1. Publish `Aspose.AI.LLM` to NuGet.org, OR
2. Provide a private NuGet feed URL and credentials for CI access, OR
3. Provide the DLL directly for offline reflection.

## Impact

Until resolved, OCR LowCode namespace discovery is permanently blocked.
Any LowCode types in Aspose.OCR cannot be enumerated, generated, or published.

## Next Action

Re-run `discover-lowcode --family ocr` after `Aspose.AI.LLM` becomes available.
