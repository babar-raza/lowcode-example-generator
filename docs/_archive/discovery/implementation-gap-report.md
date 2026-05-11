# Implementation Gap Report

**Date:** 2026-04-29
**Baseline commit:** main branch, post-pilot run `pilot-cells-20260429`
**Auditor:** Healing sprint automation

## Summary

16 implementation drifts identified between the approved execution plan (v1.2.0) and the current codebase. 4 are critical (block honest reporting or publishing safety), 6 are high (incorrect behavior that masks failures), 4 are medium (stubs that need real implementation), 2 are low (dependency and hygiene).

## Drift Register

### DRIFT-01: Runner reports success when builds fail
- **Plan requirement:** Gate 15 (validation) must fail if build fails. Gate summary must reflect actual pass/fail counts.
- **Current evidence:** `src/plugin_examples/runner.py` function `run_pipeline()` — stage failure catch-all block converts ALL non-hard-stop failures to `status = "degraded"` via blanket `else` clause. `_stage_validation()` only raises if `require_validation=True` (default False), so 0/14 builds passing produces "success" stage status.
- **Gap classification:** False positive reporting
- **Severity:** Critical
- **Root cause:** Catch-all degradation logic masks real failures; validation is opt-in instead of fail-honest.
- **Required fix:** Remove blanket degradation. Only degrade stages with explicit optional semantics (llm_preflight, reviewer in non-publish mode). All other failures stay `failed`.
- **Verification command:** `python -m pytest tests/unit/test_false_success_contracts.py::test_build_failure_blocks_full_e2e -v`
- **Blocks publishing:** Yes

### DRIFT-02: CLI forces template mode and skips runtime
- **Plan requirement:** Default CLI run must allow production mode. Template mode and skip-run must be explicit opt-in flags.
- **Current evidence:** `src/plugin_examples/__main__.py` function `main()` — hardcoded `skip_run=True, template_mode=True` in `run_pipeline()` call. No CLI flags for `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--tier`, `--promote-latest`.
- **Gap classification:** Configuration override preventing production use
- **Severity:** Critical
- **Root cause:** CLI was written for prototype demonstration, not production operation.
- **Required fix:** Add all missing CLI flags. Default to `skip_run=False, template_mode=False`. Pass all flags through to `run_pipeline()`.
- **Verification command:** `python -m plugin_examples run --help` (must show all flags)
- **Blocks publishing:** Yes

### DRIFT-03: Generated examples missing required output files
- **Plan requirement:** Each generated scenario must include Program.cs, .csproj, README.md, example.manifest.json, expected-output.json.
- **Current evidence:** `src/plugin_examples/generator/project_generator.py` function `generate_project()` — only writes `.csproj` and `Program.cs`. No README.md, example.manifest.json, or expected-output.json.
- **Gap classification:** Incomplete output contract
- **Severity:** High
- **Root cause:** Generator was written for minimum viable output only.
- **Required fix:** Add generation of README.md, example.manifest.json, expected-output.json per scenario. Add Directory.Packages.props, Directory.Build.props, global.json at run level.
- **Verification command:** `ls workspace/runs/*/generated/cells/*/` (must show all 5 files per scenario)
- **Blocks publishing:** Yes

### DRIFT-04: Generated .csproj uses inline package versions
- **Plan requirement:** Projects must use Directory.Packages.props for central version management. .csproj must use `<PackageReference Include="..." />` without Version attribute.
- **Current evidence:** `src/plugin_examples/generator/project_generator.py` function `_generate_csproj()` — template includes `Version="{package_version}"` inline.
- **Gap classification:** Build configuration drift
- **Severity:** High
- **Root cause:** No Directory.Packages.props generation implemented.
- **Required fix:** Generate Directory.Packages.props at run level. Remove Version from .csproj PackageReference.
- **Verification command:** `grep -r "Version=" workspace/runs/*/generated/cells/*/*.csproj` (must return empty)
- **Blocks publishing:** Yes

### DRIFT-05: Output validator ignores expected-output.json
- **Plan requirement:** Output validation must read expected-output.json and check: file existence, size >= minBytes, extension match, expected patterns, forbidden patterns.
- **Current evidence:** `src/plugin_examples/verifier_bridge/output_validator.py` function `validate_output()` — accepts `expected_patterns` as parameter but does not read from any file. No minBytes check, no file existence check, no extension matching.
- **Gap classification:** Validation bypass
- **Severity:** High
- **Root cause:** Validator was written for basic stdout checking only.
- **Required fix:** Add `project_dir` parameter. Read expected-output.json. Implement all checks.
- **Verification command:** `python -m pytest tests/unit/test_false_success_contracts.py::test_output_validator_reads_expected_output_json -v`
- **Blocks publishing:** Yes

### DRIFT-06: Fixture registry registers directory paths as filenames
- **Plan requirement:** Fixture registry must index real fixture files with filename, extension, size, download URL, and availability status.
- **Current evidence:** `src/plugin_examples/fixture_registry/registry.py` function `build_fixture_registry()` — registers directory path strings (e.g., "Examples/Data") as fixture `filename` values with `available=True`. `has_fixture("input.xlsx")` never matches because registered "filenames" are directory paths.
- **Gap classification:** Stub implementation
- **Severity:** High
- **Root cause:** No GitHub Contents API integration; paths registered without file listing.
- **Required fix:** Use GitHub Contents API to list actual files. Register real filenames with real metadata. Mark `available=False` if API fails.
- **Verification command:** Check `workspace/manifests/fixture-registry.json` entries have actual filenames
- **Blocks publishing:** Yes (scenarios with missing fixtures should be blocked)

### DRIFT-07: Example miner registers paths but does not parse C# examples
- **Plan requirement:** Example miner must fetch .cs files, extract using directives, extract Aspose namespace references, cross-check against catalog, classify as reusable/stale/irrelevant.
- **Current evidence:** `src/plugin_examples/example_miner/miner.py` function `mine_examples()` — registers source path strings as example_ids. `extract_symbols_from_code()` exists but is never called.
- **Gap classification:** Stub implementation
- **Severity:** Medium
- **Root cause:** No GitHub API integration for file fetching.
- **Required fix:** Fetch .cs files via GitHub API. Call `extract_symbols_from_code()` on each. Cross-check against catalog.
- **Verification command:** Check `workspace/manifests/existing-examples-index.json` has `used_symbols` populated
- **Blocks publishing:** No (existing examples are reference only)

### DRIFT-08: Scenario planner ignores missing fixtures
- **Plan requirement:** If fixture is needed but not available, scenario must be `blocked_no_fixture`.
- **Current evidence:** `src/plugin_examples/scenario_planner/planner.py` function `_build_scenario()` — when fixtures are needed but not found in registry, executes `pass` (literally does nothing). Scenario stays "ready".
- **Gap classification:** Safety bypass
- **Severity:** High
- **Root cause:** Fixture blocking was deferred and never implemented.
- **Required fix:** Replace `pass` with `status = "blocked_no_fixture"` and set blocked_reason.
- **Verification command:** `python -m pytest tests/unit/test_false_success_contracts.py::test_scenario_missing_fixture_is_blocked -v`
- **Blocks publishing:** Yes

### DRIFT-09: LLM router uses localhost only
- **Plan requirement:** LLM router should support configurable endpoints via environment variables or config.
- **Current evidence:** `src/plugin_examples/llm_router/router.py` — llm_professionalize maps to `http://localhost:8080/v1/chat/completions`, ollama to `http://localhost:11434/api/generate`. No environment variable configuration.
- **Gap classification:** Configuration limitation
- **Severity:** Medium
- **Root cause:** Hardcoded URLs for local development.
- **Required fix:** Add env var overrides (LLM_PROFESSIONALIZE_URL, OLLAMA_URL) and API key configuration.
- **Verification command:** Set env vars and verify they override defaults
- **Blocks publishing:** No (template mode works without LLM)

### DRIFT-10: example-reviewer command is guessed
- **Plan requirement:** Reviewer integration must be proven, not assumed. CLI command, config, and output format must be documented from the actual reviewer repo.
- **Current evidence:** `src/plugin_examples/verifier_bridge/bridge.py` — uses `python -m src.cli.main` which is verified accurate per `docs/discovery/example-reviewer-integration-surface.md`. However, the reviewer is not locally installed and no config for cells exists in the reviewer.
- **Gap classification:** Integration not operational
- **Severity:** Medium
- **Root cause:** Reviewer repo exists but is not cloned or configured for this pipeline.
- **Required fix:** Document exact gaps. Add env var configuration for reviewer path. Block publishing until reviewer is operational.
- **Verification command:** Check `workspace/verification/latest/example-reviewer-integration-surface.json` for gaps
- **Blocks publishing:** Yes (reviewer unavailable blocks publish path)

### DRIFT-11: Publisher does not check all required gates
- **Plan requirement:** Publisher must verify restore_passed, build_passed, run_passed, output_validation_passed, example_reviewer_passed before publishing. Must check full evidence file set.
- **Current evidence:** `src/plugin_examples/publisher/publisher.py` function `publish_examples()` — only checks `status in ("generated", "repaired")`. `_verify_evidence()` only checks 2 files (source-of-truth-proof, validation-results).
- **Gap classification:** Safety bypass
- **Severity:** Critical
- **Root cause:** Publisher was written for dry-run demo, not production gating.
- **Required fix:** Add gate_verdict parameter. Require all 5 gate passes. Expand evidence check to full required set.
- **Verification command:** `python -m pytest tests/unit/test_false_success_contracts.py::test_publisher_rejects_failed_build -v`
- **Blocks publishing:** Yes

### DRIFT-12: Package watcher does not resolve NuGet versions
- **Plan requirement:** Monthly watcher must resolve latest stable version from NuGet API and compare to package-lock.json.
- **Current evidence:** `src/plugin_examples/package_watcher/watcher.py` function `check_for_updates()` — sets `latest_version=None` with comment "Would resolve from NuGet in live run". No API call.
- **Gap classification:** Stub implementation
- **Severity:** Medium
- **Root cause:** NuGet API integration was deferred.
- **Required fix:** Call NuGet Registration API. Compare versions. Trigger delta chain on change.
- **Verification command:** `python -m pytest tests/unit/test_false_success_contracts.py::test_package_watcher_detects_changed_version -v`
- **Blocks publishing:** No (manual runs still work)

### DRIFT-13: Experimental families active by default
- **Plan requirement:** Only cells is the active pilot. Experimental families must not run in monthly or default pipeline runs.
- **Current evidence:** `pipeline/configs/families/email.yml`, `pdf.yml`, `slides.yml`, `words.yml` — all have `enabled: true, status: experimental` and are in the active families directory.
- **Gap classification:** Scope creep
- **Severity:** Medium
- **Root cause:** Families were moved from disabled/ to active/ prematurely.
- **Required fix:** Move experimental configs back to `pipeline/configs/families/disabled/` or add `--allow-experimental` flag enforcement.
- **Verification command:** `ls pipeline/configs/families/` (only cells.yml should be active)
- **Blocks publishing:** No (pipeline runs per-family)

### DRIFT-14: No evidence promotion to durable paths
- **Plan requirement:** Evidence must be promotable to `workspace/verification/latest/` and manifests to `workspace/manifests/` for durable archival.
- **Current evidence:** Runner writes all evidence to `workspace/runs/{run_id}/evidence/`. No `--promote-latest` flag or copy mechanism exists.
- **Gap classification:** Missing feature
- **Severity:** Medium
- **Root cause:** Evidence promotion was not implemented.
- **Required fix:** Add `--promote-latest` flag. Copy evidence files from run to durable paths.
- **Verification command:** `ls workspace/verification/latest/` after run with `--promote-latest`
- **Blocks publishing:** No (evidence exists in run dir)

### DRIFT-15: pytest-timeout not in dependencies
- **Plan requirement:** CI uses `--timeout=60` flag. pytest-timeout must be declared as a dependency.
- **Current evidence:** `pyproject.toml` — no `pytest-timeout` in dependencies or optional-dependencies. `[tool.pytest.ini_options] timeout = 30` is configured but the plugin is not installed.
- **Gap classification:** Missing dependency
- **Severity:** Low
- **Root cause:** Dependency was assumed present from CI environment.
- **Required fix:** Add `pytest-timeout>=2.2` to `[project.optional-dependencies] dev`.
- **Verification command:** `pip install -e ".[dev]" && python -m pytest --co -q` (timeout plugin loads)
- **Blocks publishing:** No

### DRIFT-16: DllReflector build artifacts in working tree
- **Plan requirement:** Build artifacts (bin/, obj/) must not be committed. .gitignore must exclude them.
- **Current evidence:** `tools/DllReflector/bin/` and `obj/` exist locally. `.gitignore` has `bin/` and `obj/` patterns. Files are NOT git-tracked (verified).
- **Gap classification:** Local hygiene only
- **Severity:** Low
- **Root cause:** Local build artifacts from DllReflector compilation.
- **Required fix:** Confirm not tracked. Optionally clean local artifacts.
- **Verification command:** `git ls-files tools/DllReflector/bin/ tools/DllReflector/obj/` (must be empty)
- **Blocks publishing:** No
