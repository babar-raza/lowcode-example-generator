# Gap List — README Investigation

## Documented in README (no action required)

1. PDF generation blocked (discovery_only, 2 open taskcards)
2. Words expansion blocked (4 open taskcards)
3. No integration tests (unit tests only, all mocked)
4. example-reviewer is a separate repo, must be cloned separately
5. Merge requires human APPROVE_MERGE_PR token (intentional)
6. Windows recommended for full pipeline (monthly CI uses windows-latest per memory)

## Inconsistency requiring fix (not in README scope, flagged for follow-up)

### AGENTS.md env var names are stale
- **File:** AGENTS.md (Credentials Required section)
- **Problem:** Lists `LLM_PROFESSIONALIZE_API_KEY` as a required secret
- **Actual:** `GPT_OSS_API_KEY` (confirmed in docs/ci/environment-variables.md)
- **Fix:** Update AGENTS.md credentials table to use GPT_OSS_ENDPOINT, GPT_OSS_API_KEY, GPT_OSS_MODEL
- **Risk:** Low (not a functional issue; affects discoverability for new contributors)

## Gaps not yet resolvable from this investigation

1. **Test count (759)** — the number 759 comes from memory/agent report. An actual `pytest --collect-only`
   would give the authoritative count. If it differs slightly, the README says "approximately 759 tests".

2. **Monthly CI workflow details** — the workflow file was not read directly. The cron schedule
   (1st of month) and platform (windows-latest) come from the agent report and memory.
   Verify by reading: .github/workflows/monthly-package-refresh.yml

3. **PDF repo does not yet exist** — pdf.yml points to `aspose/aspose-plugins-examples-dotnet` (central repo)
   not a dedicated PDF repo. This is consistent with the open taskcard for repo-target-mapping.

## Recommended fixes outside README

1. Update AGENTS.md credentials table (low priority, cosmetic)
2. Add a lightweight integration smoke test that exercises DllReflector + scenario planning
3. Verify exact test count by running: PYTHONPATH=src pytest tests/unit --collect-only -q
