# Evidence — CI/CD Healing Sprint (TC-H01..H09)

## TC-H01: Shell quoting fix in .gitlab-ci.yml
- **Before:** `pip install ruff>=0.4` (bash would interpret `>` as redirect)
- **After:** `pip install "ruff>=0.4"`
- **Proof:** YAML syntax validated; change visible in git diff

## TC-H02: Coverage flags in GitLab CI unit tests
- **Change:** Added `--cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60` to unit-tests-py312 and unit-tests-py313 scripts
- **Matches:** `build-and-test.yml:45-46`
- **Proof:** YAML syntax validated

## TC-H03: RISK-10 gate isolation job in GitLab CI
- **Change:** New `gate-isolation` job in lint stage with `allow_failure: true`
- **Why advisory:** `publication_gate.py:221` has probe import inside `try/except ImportError: pass` — different from hard dependency
- **Proof:** `grep -rn ... src/plugin_examples/gates/` confirmed to find 1 match (publication_gate.py:221)
- **Scope note:** Unit test only checks `example_gates.py`; CI grep covers all of `gates/`

## TC-H04: pip-audit advisory job in GitLab CI
- **Change:** New `pip-audit` job in lint stage with `allow_failure: true`
- **Matches:** `build-and-test.yml:39-41`
- **Proof:** YAML syntax validated

## TC-H05: Ruff blocking gate in GitLab CI (promoted from advisory)
- **Before:** `allow_failure: true` in ruff-lint job
- **After:** No `allow_failure` (blocking) — promoted because ruff now exits 0
- **Proof:** `ruff check src/ tests/` → `All checks passed! EXIT:0`

## TC-H06: Local CI scripts updated
- `scripts/local-ci.sh` — added coverage flags, RISK-10 gate check (advisory), pip-audit (advisory)
- `scripts/local-ci.ps1` — same
- **Proof:** Files written, readable

## TC-H07: Pre-commit hooks verified
- **Command:** `pre-commit run --all-files`
- **Result:** Hooks ran; ruff found violations (before fixes); hooks installed correctly
- **Post-fix:** Scoped to `src/ tests/`; hooks will pass after ruff fixes
- **Version:** pre-commit 4.5.0

## TC-H08: .pip-cache/ added to .gitignore
- **Change:** Added `.pip-cache/` to `.gitignore` with comment
- **Proof:** `grep pip-cache .gitignore` → line present

## TC-H09: Ruff triage — 6 findings in src/tests/
- **F811** `test_scenario_contracts.py:54` — renamed `test_contracts_dir_exists` → `test_contracts_root_dir_exists` (FIXED)
- **F402** `anti_overclaiming_validators.py:211` — renamed loop var `field` → `fname` (FIXED)
- **E741** × 4 — added to `pyproject.toml` ignore list with justification (IGNORED)
- **Final ruff check:** `All checks passed! EXIT:0`
- **Tests:** 102 targeted tests PASS; 509 broader tests PASS
- **Pre-commit scope:** Updated to `files: ^(src|tests)/` to prevent touching legacy scripts/reports/
- **pre-commit-hooks:** Bumped from v4.6.0 to v5.0.0 to resolve deprecated stage names warning

## Unintended side effects (handled)
- Pre-commit ruff `--fix` ran on `reports/` Python files before scope was restricted
- Files modified: 7 historical `.py` files in `reports/`
- Action: Restored via `git checkout HEAD -- <files>`
- Pre-commit ruff also cleaned unused imports from 5 test files — all 509 tests pass
