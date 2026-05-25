Sprint 87 — Dry-Run Scaffold Plan
===================================
Date: 2026-05-25
Author: Lane 2

## Purpose
Plan the dry-run scaffold for testing README I/O PR creation before live execution.
This allows verification of the PR workflow without requiring approval gates.

## Current Dry-Run Infrastructure
- `workspace/pr-dry-run/` — existing dry-run output directory
- `publish-pr` CLI with `--dry-run` flag support
- `resolve-repo-access --families <f>` must be run before publish

## Scaffold Design

### Phase 1: Local Dry-Run (no API calls)
1. Generate README I/O content for one example per family
2. Write to `workspace/pr-dry-run/{family}-readme-io-test/`
3. Validate generated content against format contracts
4. Verify README structure matches template

### Phase 2: API Dry-Run (read-only API calls)
1. Run `resolve-repo-access` to verify token access
2. Run `publish-pr --dry-run` for one family
3. Capture dry-run output (PR diff preview)
4. Verify no actual PR was created

### Phase 3: Single-Family Pilot (requires approval)
1. Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
2. Run `publish-pr --publish` for one family (e.g., diagram — smallest at 2 examples)
3. Verify PR created with correct content
4. Verify README I/O sections present

## Blockers
- Phase 1: No blockers — can run immediately
- Phase 2: Requires `GH_TOKEN` set
- Phase 3: Requires `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`

## Sprint 87 Status
Phase 1 scaffold design documented. Execution deferred to next sprint with approval.
