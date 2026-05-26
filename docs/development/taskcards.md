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

The generated markdown view is:

```text
docs/development/open-taskcard-closure-matrix.md
```

Do not edit the generated markdown directly. Edit the JSON evidence and rerun the sync command.
