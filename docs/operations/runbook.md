# Operational Runbook

Audience: Operator, On-call Engineer
Version: 1.0 (2026-06-11)
Related: [incident-response.md](incident-response.md), [troubleshooting.md](troubleshooting.md), [sla.md](sla.md)

This runbook covers step-by-step recovery procedures for the most common pipeline failure
scenarios. Each entry follows the format: **Symptom → Root Cause → Recovery Steps → Prevention**.

---

## Scenario 1: LLM Timeout or Rate Limit

**Symptom**
- Pipeline log: `LLM circuit breaker tripped after N consecutive failures`
- `llm-preflight.json`: `preflight_passed: false`
- Generation stage reports `llm_available: false`, falls back to template mode

**Root Cause**
The `LLMRouter` circuit breaker (threshold: 5 consecutive failures) trips when the LLM
endpoint (`GPT_OSS_ENDPOINT`) is unreachable, rate-limited, or returning HTTP 5xx.

**Recovery Steps**
1. Check the LLM endpoint status: `curl -s $GPT_OSS_ENDPOINT/models -H "Authorization: Bearer $GPT_OSS_API_KEY"`
2. If endpoint is down — wait for service recovery or set `TEMPLATE_MODE=true` to skip LLM
3. If rate limited — check token quota; reduce concurrency or wait for quota reset
4. Reset the circuit breaker by restarting the pipeline with `--template-mode` flag until LLM recovers
5. Inspect `decision-audit-<run_id>.jsonl` in `.local/` for the sequence of failures

**Prevention**
- Monitor `LLMRouter._consecutive_failures` in observability logs
- Set `_CIRCUIT_BREAKER_THRESHOLD` environment override for high-concurrency runs
- Keep `TEMPLATE_MODE=true` as fallback in CI environments without LLM access

---

## Scenario 2: NuGet Restore Failure

**Symptom**
- Stage log: `dotnet restore failed` or `NU1101: Unable to find package`
- `package-dry-run-result.json`: `restore_exit_code != 0`
- `validation-results.json`: `restore: false`

**Root Cause**
NuGet package restore fails when:
- Network connectivity to nuget.org is blocked
- Package version is yanked or no longer available
- `global.json` SDK version constraint is incompatible with the installed .NET SDK

**Recovery Steps**
1. Check .NET SDK version: `dotnet --version` (must be ≥ 8.0)
2. If version mismatch: patch `global.json` in the generated project — change `sdk.version` to match installed SDK
3. If package unavailable: update the family YAML in `pipeline/configs/families/<family>.yaml` to use an available version
4. Run dry-run for just the affected package: `plugin-examples run --family <family> --dry-run`
5. Check restore log at `reports/<sprint>/e2e/<family>/<slug>/restore.log`
6. If NuGet.org is blocked: configure a local NuGet feed in `NuGet.Config` and set `NUGET_PACKAGES` env var

**Prevention**
- Pin NuGet package versions in family YAMLs (`version_policy: pinned`)
- Run `dotnet restore --no-cache` periodically to detect yanked packages
- Keep `DllReflector/NuGet.Config` with a fallback local feed for airgapped environments

---

## Scenario 3: Dry-Run Hash Regression

**Symptom**
- Evidence contract validation: `BUNDLE_CONTRACT_FAILED`
- `source-hashes.json` SHA mismatch between two runs
- `test_generation_idempotency.py::test_run_history_save_is_idempotent` fails

**Root Cause**
Non-deterministic output in generated code or evidence files. Common causes:
- Timestamp injected into generated source (instead of run_id)
- Random ordering in dictionary serialization
- Non-pinned LLM temperature (not 0.0)

**Recovery Steps**
1. Run the pipeline twice with identical inputs: `plugin-examples run --family <family> --dry-run`
2. Compare output: `diff run1/generated/ run2/generated/`
3. Identify the non-deterministic field and fix the generator template
4. For LLM-generated code: ensure `temperature=0.0` in `_call_openai_compatible()` and `_call_ollama()`
5. Re-run `pytest tests/integration/test_generation_idempotency.py` to confirm fix

**Prevention**
- Run idempotency tests in CI: `pytest tests/integration/test_generation_idempotency.py`
- Do not inject wall-clock timestamps into generated source code
- Review generator templates for any use of `random` or `uuid4()` outside run_id context

---

## Scenario 4: Evidence Contract Version Mismatch

**Symptom**
- `python -m plugin_examples doctor` shows evidence chain WARN/FAIL
- `StrictEvidenceContractV3.validate_zip()` raises: `BUNDLE_CONTRACT_FAILED`
- Missing categories in contract validation report

**Root Cause**
Sprint evidence bundles must match the contract version used at closeout. Using contract v1
to validate a v3 bundle (or vice versa) causes category mismatches. Contract versions v1-v8
are in `evidence_contract.py`; the current production version is v3.

**Recovery Steps**
1. Check which contract version the bundle was sealed with: read `bundle-contract-definition.json` inside the ZIP
2. Use the matching validator: `StrictEvidenceContractV3` for v3 bundles
3. If re-validating old bundles — use the version-appropriate class
4. If the bundle is incomplete: check `evidence_layout.py` for required artifact paths
5. Re-generate missing artifacts using `evidence_contract_computer.py`

**Prevention**
- Always use `StrictEvidenceContractV3` for new sprints (current default)
- Store `bundle-contract-definition.json` inside each ZIP to make version self-documenting
- Add contract version assertion to closeout gate

---

## Scenario 5: Git Status Dirty at Closeout

**Symptom**
- `git status --short` shows modified files after sprint
- Evidence contract check: `git-status-final.txt contains staged/dirty files`
- Sprint cannot proceed to closeout gate

**Root Cause**
Sprint generated or modified files that were not committed before the final git-status capture.
Common causes:
- Report files written to `reports/` but not staged
- `pipeline/` config files updated but not committed
- `.local/` files accidentally staged

**Recovery Steps**
1. Run `git status --short` to identify dirty files
2. If reports need to be committed: `git add reports/` then commit
3. If pipeline configs changed: review the change, commit if intentional
4. If `.local/` is staged accidentally: `git restore --staged .local/`
5. Re-capture git status: `git status --short > .local/rating-healing-runs/<run>/git-status-final.txt`
6. Re-run evidence contract validation

**Prevention**
- Always commit sprint artifacts before running closeout gate
- Add `.local/` to `.gitignore` (already done)
- Use `final_git_status_validator.py` gate check before closeout

---

## Scenario 6: Test Coverage Below Threshold

**Symptom**
- CI fails: `FAIL Required test coverage of 70% not reached. Total coverage: X%`
- `pytest --cov=src/plugin_examples --cov-fail-under=70` exits non-zero

**Root Cause**
New source code added without corresponding tests, or test files moved/deleted.

**Recovery Steps**
1. Run coverage report: `PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-report=term-missing`
2. Identify uncovered modules in the `MISSING` column
3. Add unit tests for uncovered logic (target the lowest-coverage new modules first)
4. Re-run coverage to confirm threshold is met
5. If threshold seems too high for the new module type — discuss with team before lowering

**Prevention**
- Write tests alongside new source modules (test-alongside discipline)
- Run `PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-report=html` locally before PR
- The `fail_under = 70` threshold in `pyproject.toml` is the floor — aim for 80%+

---

## Scenario 7: Engineering Hygiene Gate Failure (EHV Validators)

**Symptom**
- `python -m plugin_examples doctor` shows `engineering_hygiene: WARN`
- EHV-01 or EHV-02 violations found

**Root Cause**
New code introduced silent bare `except Exception: pass` handlers or bare `except:` clauses.

**Recovery Steps**
1. Run validators: `PYTHONPATH=src python -c "from plugin_examples.fixture_factory.engineering_hygiene_validators import run_all_ehv_validators; from pathlib import Path; [print(r.message, r.detail) for r in run_all_ehv_validators()]"`
2. Find violations in the detail field (shows file:line)
3. Replace `except Exception: pass` with `except Exception as exc: logger.debug("context: %s", exc)`
4. Replace bare `except:` with specific exception types
5. Re-run validators to confirm PASS

**Prevention**
- EHV-01/02 validators run on every `doctor` invocation
- Pre-commit ruff check catches some patterns
- Code review checklist: "Are all exception handlers specific and logged?"

---

## On-Call Quick Reference

| Signal | First Check | Command |
|--------|-------------|---------|
| LLM failure | circuit breaker state | `grep "circuit breaker" .local/logs/latest.log` |
| NuGet failure | restore log | `cat reports/<sprint>/e2e/<family>/<slug>/restore.log` |
| Hash mismatch | idempotency test | `pytest tests/integration/test_generation_idempotency.py` |
| Contract failure | contract version | `unzip -p bundle.zip bundle-contract-definition.json` |
| Git dirty | git status | `git status --short` |
| Coverage fail | coverage report | `pytest tests/unit --cov=src/plugin_examples --cov-report=term-missing` |
| EHV failures | doctor check | `python -m plugin_examples doctor` |

See also: [incident-response.md](incident-response.md) for escalation paths.
