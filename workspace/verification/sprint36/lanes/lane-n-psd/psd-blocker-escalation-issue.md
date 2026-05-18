# PSD LowCode Discovery Blocker — Escalation Package

**Sprint:** sprint36
**Date:** 2026-05-18
**Blocker:** Aspose.JavaAttributes private assembly not on NuGet.org

## Summary

Aspose.PSD 26.4.0 is available on NuGet, but reflection-based discovery
fails because `Aspose.JavaAttributes` is a required dependency not on NuGet.

## Repro

```
curl https://api.nuget.org/v3-flatcontainer/aspose.javaattributes/index.json
# Returns: HTTP 404 Not Found
```

## Request to Aspose Team

1. Publish `Aspose.JavaAttributes` to NuGet.org, OR
2. Provide a private NuGet feed URL/credentials, OR
3. Provide the DLL for offline reflection.

## Next Action

Re-run `discover-lowcode --family psd` after dependency is available.
