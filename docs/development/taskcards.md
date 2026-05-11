# Taskcards

Audience: Contributor

Taskcard docs are generated from JSON evidence by `scripts/sync_taskcards.py` or the `sync-taskcard-docs` CLI command.

## Check Sync

```powershell
python scripts/sync_taskcards.py --check
```

## Generate

```powershell
python scripts/sync_taskcards.py
```

The source JSON is expected at:

```text
workspace/verification/latest/open-taskcard-closure-matrix.json
```

The previous generated matrix was archived or replaced during docs consolidation. Regenerate it from evidence when needed.
