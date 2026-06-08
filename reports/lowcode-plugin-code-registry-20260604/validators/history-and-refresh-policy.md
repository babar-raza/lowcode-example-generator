# History and Refresh Policy

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## History Policy

### Invariant
Every registry entry MUST have at least one history record containing:
- `date`: ISO date string
- `status`: registry_status value at that time
- `analyst_notes`: what was done and by whom (sprint or agent ID)

### Adding History Records
A new history record is added whenever:
1. registry_status changes
2. A new code file is fetched (add code_hash to record)
3. A new package version is used
4. An API modernization is applied (must document what changed)

### History is Append-Only
- Do NOT delete history records
- Do NOT modify past history records
- When correcting an error: add new record with correction note

### Example History
```yaml
history:
  - date: "2026-06-04"
    status: CODE_HARVESTED
    page_hash: "1770337e14ce0847"
    code_hash: "bc77bfce202fa6f5..."
    package_version: "26.5.0"
    analyst_notes: "Sprint lowcode-plugin-code-registry-20260604. Fetched from GitHub BarcodeOutput/StoreBarcodeOutputAsFile.cs"
  - date: "2026-06-05"
    status: READY_FOR_TRANSFORMATION
    code_hash: "bc77bfce202fa6f5..."
    analyst_notes: "DllReflector confirmed BarcodeGenerator class. Symbol extraction complete."
```

---

## Refresh Policy

### When to Refresh
The registry should be refreshed when:
1. A new package version is released (check NuGet for Aspose.* packages monthly)
2. A products.aspose.net page hash changes (indicates content update)
3. An official GitHub repo gets new commits affecting example files
4. An API is deprecated or signature changes

### How to Refresh
1. Re-fetch page: compare new page_hash to stored hash
2. If hash changed: crawl page again; update source links
3. Re-fetch code file: compare new code_hash to stored hash
4. If code changed: re-extract symbols; update registry entry
5. Add new history record documenting the change

### Staleness Threshold
- Page hashes: consider stale after 30 days
- Code hashes: consider stale after 60 days (GitHub code changes less frequently)
- Package versions: refresh when NuGet shows newer version

---

## Anti-Regression Policy

These actions are FORBIDDEN without explicit human approval:
1. Downgrading registry status (e.g., READY_FOR_TRANSFORMATION → CODE_HARVESTED)
2. Changing implementation_model without re-running manual analysis
3. Marking WEBSITE_PATTERN_UNVERIFIED as READY_FOR_TRANSFORMATION
4. Using a family probe result to advance individual plugin status
5. Replacing official code citations with heuristic reflection assignments
