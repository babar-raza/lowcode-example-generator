# Release Process

Last verified: 2026-06-11
Source of truth: this document + `pyproject.toml` version + `CHANGELOG.md`

This document describes how to cut a versioned release of the LowCode Example Generator pipeline.

## Release Cadence

Releases are aligned with **wave sprints**. Each wave that advances the pipeline state (new packages proven, new validators added, major bugs fixed) increments the version.

| Wave scope | Version bump |
|------------|-------------|
| New proven packages, new validators, infrastructure changes | Minor (`0.X.0`) |
| Hotfix to existing wave (evidence correction, test fix) | Patch (`0.X.Y`) |
| Breaking change to pipeline API or evidence contract format | Major (`X.0.0`) |

## Prerequisites

Before cutting a release, verify:

```bash
# 1. All tests pass
PYTHONPATH=src python -m pytest tests/ --timeout=60 -q
# Expected: N passed, 0 failed

# 2. Ruff lint is clean
ruff check src/ tests/

# 3. Doctor check passes
PYTHONPATH=src python -m plugin_examples doctor

# 4. Git status is clean (no uncommitted changes to tracked files)
git status --short
```

## Steps

### Step 1: Determine the new version

Check the current version:
```bash
grep '^version' pyproject.toml
```

Choose the next version following semantic versioning aligned with the wave number.

### Step 2: Update `pyproject.toml`

```toml
[project]
version = "0.X.0"
```

### Step 3: Update `CHANGELOG.md`

Add a new section at the top of `CHANGELOG.md`:

```markdown
## [0.X.0] - YYYY-MM-DD

### Added
- <description of new packages, validators, features>

### Changed
- <description of changes>

### Fixed
- <description of fixes>
```

Keep the format consistent with [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

### Step 4: Commit the version bump

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to 0.X.0"
```

### Step 5: Tag the release

```bash
git tag -a "v0.X.0" -m "Release v0.X.0"
```

### Step 6: Push

```bash
git push origin main
git push origin "v0.X.0"
```

### Step 7: Verify CI passes

Check that the CI pipeline (`build-and-test.yml`) passes on the tagged commit.

### Step 8 (optional): Create GitHub Release

If publishing a formal GitHub Release:

```bash
gh release create "v0.X.0" \
  --title "v0.X.0 — <Wave N description>" \
  --notes-file <(grep -A 50 "## \[0.X.0\]" CHANGELOG.md | head -50)
```

## Evidence Bundle

Each wave sprint produces an evidence bundle:

```
.local/evidence-bundles/
  lowcode-plugin-<sprint-id>.zip          # evidence ZIP
  lowcode-plugin-<sprint-id>.sha256       # SHA-256 sidecar
  lowcode-plugin-<sprint-id>-final-attestation.json
  lowcode-plugin-<sprint-id>-post-freeze-validation.json
```

The evidence bundle is **not committed to git** (it is in `.gitignore`). It is an operational artifact stored locally and referenced in sprint closeout reports.

## Rollback

If a release needs to be rolled back:

1. Identify the last good release tag: `git tag --list 'v*' --sort=-version:refname | head -5`
2. Create a revert commit: `git revert HEAD` (do not use `git reset --hard` on pushed commits)
3. Bump the patch version and re-release.

Do not delete published tags or rewrite history on `main`.

## Related Documents

- [CHANGELOG.md](../../CHANGELOG.md)
- [Incident Response](incident-response.md)
- [SLA](sla.md)
