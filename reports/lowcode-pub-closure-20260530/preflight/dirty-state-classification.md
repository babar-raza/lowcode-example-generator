# Dirty State Classification — lowcode-pub-closure-20260530

## Pre-sprint dirty state (resolved in commit 31e2069)

### Category 1: workspace/pr-dry-run bin/obj (89 files)
- Classification: TRACKED_BINARY_BUILD_ARTIFACTS
- Root cause: dotnet build ran during pass4 evidence collection; .gitignore rule
  `workspace/pr-dry-run/` already existed but files were committed before rule enforcement
- Resolution: git rm --cached (untracked without deleting from disk); already gitignored

### Category 2: workspace/verification/latest/*.json (12 files)
- Classification: TRACKED_STATE_REFRESH
- Root cause: pipeline evidence collection updated backlog/audit JSONs during pass4
- Resolution: committed as state update (git add -f)

### Category 3: pipeline/configs/denominators/pdf.json (1 file)
- Classification: DENOMINATOR_HASH_UPDATE
- Root cause: api_catalog_sha256 refresh + em-dash Unicode normalization
- Resolution: committed as legitimate denominator update

### Category 4: workspace/pr-dry-run/README.md files (2 files)
- Classification: TIMESTAMP_REFRESH
- Root cause: README regenerated with updated timestamp during pass4
- Resolution: committed

## Post-resolution status
Tracked dirty file count: 0 (verified by git status --short | grep -v ^??)
