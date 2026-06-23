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

- **`mutmut results` outputs no text when all mutants are killed** (TC-SRHP-22):
  The progress-bar format `🎉 109` printed during the run does NOT appear in
  `mutmut results` output when all mutants are killed. The prior `grep -oP '\d+
  (?=killed)'` regex never matched this format, causing `mutmut-results.json` to
  always report `{"killed": 0, "survived": 0, "total": 0, "score": "N/A"}` on
  perfect-score runs. Fixed in commit (TC-SRHP-22) by querying the `.mutmut-cache`
  SQLite database directly: `SELECT COUNT(*) FROM mutant WHERE status='Killed'`.

---

## Baseline Score

### First Successful Run — 2026-06-21

| Field | Value |
|---|---|
| GitHub Actions run URL | https://github.com/babar-raza/lowcode-example-generator/actions/runs/27901328201 |
| Date | 2026-06-21 |
| Python version | 3.12.13 |
| mutmut version | 2.x (pinned `mutmut<3`) |
| Scope | `src/plugin_examples/quality/example_scorer.py` only |
| Run duration | ~49 minutes |

| Module | Killed | Survived | Timeouts | Total | Score |
|---|---|---|---|---|---|
| `quality/example_scorer.py` | 109 | 0 | 0 | 109 | **100%** 🎉 |

**Interpretation:** GREEN — perfect mutation score. All 109 mutants killed. The 21 tests
in `tests/unit/test_example_scorer.py` cover every reachable code path with discriminating
assertions. No test additions are needed at this time.

**Status: >= 80% target MET. Candidate for future blocking gate once remaining modules are baselined.**

### Pending Baseline Modules

These modules were not included in the first run (3-module run timed out at 60 min,
GHA run 27899842949). To be baselined in future weekly runs:

| Module | Priority | Notes |
|---|---|---|
| `gates/example_gates.py` | High | Gate logic; add in next weekly run |
| `publisher/github_pr_publisher.py` | Medium | PR creation; add after gates baselined |

Evidence path: `workspace/evidence/mutation/mutmut-results.json`
GHA artifact: `mutation-testing-results` (30-day retention)
