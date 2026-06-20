# Mutation Testing

Audience: Pipeline engineer, CI/CD operator
Last updated: 2026-06-20

---

## Purpose

Mutation testing verifies that the test suite can detect real bugs.
A mutation is a small, targeted code change (e.g., flipping `==` to `!=`).
If the test suite does not catch the mutation (the mutant survives), that code
path may be undertested.

**TC-SRHP-04** — This document resolves the Docker unreliability blocker for
mutation testing by providing an alternative GitHub Actions path.

---

## Baseline Target

| Metric | Target |
|---|---|
| Mutation score (critical modules) | >= 70% killed |
| Run frequency | Weekly (Sunday 02:00 UTC) |
| CI blocking | NO — advisory only |

---

## How to Run

### GitHub Actions (Recommended — no Docker required)

Mutation testing runs automatically every Sunday via
`.github/workflows/mutation-testing.yml`. To trigger manually:

```
GitHub → Actions → Mutation Testing → Run workflow
```

Results are uploaded as artifacts with 30-day retention.

### Local (WSL — Linux environment)

The existing WSL script runs mutmut inside a Linux environment:

```bash
# Requires WSL with python3-venv installed:
# sudo apt-get install python3-venv

bash scripts/wsl-mutmut.sh
```

Results are written to `workspace/evidence/mutation/`.

### Local (Windows — direct)

```bash
# Activate venv first
.venv/Scripts/python.exe -m pip install mutmut

# Run on critical modules
mutmut run \
  --paths-to-mutate src/plugin_examples/gates/example_gates.py \
  --tests-dir tests/unit

mutmut results
```

---

## Critical Modules (Priority Order)

The following 10 modules are the highest priority for mutation coverage:

| Module | Why critical |
|---|---|
| `gates/example_gates.py` | Gate logic; wrong comparison → wrong publish verdict |
| `runner.py` | Pipeline orchestration; stage skips or wrong context |
| `publisher/github_pr_publisher.py` | PR creation; corrupted files or wrong branch |
| `publisher/publisher.py` | Publishing entry point; wrong dry_run flag |
| `quality/example_scorer.py` | Quality scoring; wrong threshold or criterion |
| `commands/catalog_discover.py` | Discovery entry point; wrong manifest handling |
| `commands/run.py` | Run command parsing; wrong flag defaults |
| `family_config.py` | Config loading; missing fields silently ignored |
| `replay.py` | Replay integrity; wrong path escaping |
| `probe_executor/executor.py` | Probe correctness; wrong status transitions |

---

## Interpreting Results

```
Survived mutations = bugs the tests DON'T catch.
Killed mutations   = bugs the tests DO catch.

Score = killed / (killed + survived)
```

- Score >= 80%: GREEN — excellent test coverage
- Score 60-79%: YELLOW — adequate, but add targeted tests for survivors
- Score < 60%: RED — significant coverage gap; add tests before expanding families

---

## Known Limitations

- **GitLab CI Docker unreliability**: The GitLab shell executor cannot reliably
  run Docker from a `git-runner` SYSTEM service session. Mutation testing via
  `scripts/docker-mutmut.sh` always fails with `script_failure` in 20-27s.
  This is `allow_failure: true` in `.gitlab-ci.yml` and will remain advisory.

- **WSL from SYSTEM service**: `WSL_E_LOCAL_SYSTEM_NOT_SUPPORTED` when running
  GitLab runner as a Windows service. Run the runner interactively to use WSL.

- **GitHub Actions is the reliable path**: Uses `ubuntu-latest` — no Docker
  or WSL needed. This is the primary mutation testing CI path.

---

## Baseline Score (as of 2026-06-20)

Status: PENDING first successful GitHub Actions run.

Once the first run completes, update this table:

| Module | Killed | Survived | Score |
|---|---|---|---|
| `gates/example_gates.py` | TBD | TBD | TBD |
| `quality/example_scorer.py` | TBD | TBD | TBD |
| `publisher/github_pr_publisher.py` | TBD | TBD | TBD |
| **Overall** | TBD | TBD | TBD |

Evidence path: `workspace/evidence/mutation/mutmut-results.json`
