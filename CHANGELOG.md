# Changelog

All notable changes to the LowCode Example Generator are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses wave-based versioning aligned with sprint cycles.

## [0.31.0] - 2026-06-13

### Added
- Stage I/O contracts: declarative StageContract registry for 8 critical-path pipeline stages
- Contract tests: consistency, shape, and snapshot regression tests (25+ tests)
- SLO auto-remediation: 4 rules mapping SLO violations to strategy adjustments
- Doctor check_audit_trail: verifies audit trail presence in evidence directories

### Changed
- Audit trail wired into planner loop: every handler dispatch records AuditEntry (EXECUTE/DEFER/BLOCK)
- Compliance trend wired into planner loop: generates compliance-trend-report.json per run
- SLO remediator wired into planner loop: auto-adjusts loop config on SLO violations
- Mutation testing CI gate: blocking on merge requests with 70% score threshold (was advisory/manual)
- Mutation testing scope widened to gates, policy, SLO monitor, compliance reporter, remediator, contracts
- Atomic checkpoint writes: tmp+replace pattern prevents corruption on crash

## [0.30.0] - 2026-06-13

### Added
- Policy-as-code layer: goals.yml, slo.yml, gates.yml with typed Python loader
- SLI emission module: per-handler telemetry via structured logging (HandlerTimer)
- SLO monitoring: cross-run SLO evaluation with compliance summary
- Compliance reporting: trend analysis (improving/stable/degrading) across runs
- Audit trail: action-to-policy-rule lineage with JSON persistence
- Planner loop checkpoint/resume: per-cycle state snapshots for failure recovery
- Doctor health checks: check_slo_compliance and check_gate_policy (20+ total)
- CI compliance-gate job: policy-as-code enforcement via doctor health checks
- 58 new unit tests across 6 test files (policy, SLI, SLO, audit, compliance)

### Changed
- Planner loop uses policy-as-code gate definitions instead of hardcoded frozensets
- Handler execution wrapped with HandlerTimer for SLI emission
- SLO evaluation runs after every loop completion with evidence persistence
- Doctor run_all_checks() now includes 10 core checks + 10 EHV checks = 20+ total

## [0.29.0] - 2026-06-13

### Added
- SECURITY.md with vulnerability disclosure policy, response timeline, and scope definition
- CONTRIBUTING.md with development setup, coding standards, PR workflow, and CI gate reference
- EHV-09 validator: SECURITY.md presence policy-as-code check
- EHV-10 validator: CONTRIBUTING.md presence policy-as-code check
- Agent loop observable metrics (LoopMetrics) in planner_loop.py with structured logging emission
- Mutation testing CI job (advisory, manual trigger, scoped to gates/)
- Recovery/rollback test scenarios (7 tests for graceful degradation)
- LoopMetrics unit tests (5 tests)

### Changed
- Engineering hygiene validators expanded from EHV-01..08 to EHV-01..10
- planner_loop.py now emits planner-loop-metrics.json to evidence directory
- planner_loop.py uses structured logging via observability.get_logger()

## [0.28.0] - 2026-06-13

### Added
- Bandit SAST blocking gate in GitLab CI (bandit-sast job, lint stage)
- Dependency license policy-as-code (EHV-08 validator + license-check CI job)
- Version/changelog sync validator (EHV-06) with pre-commit hook
- Semver format validator (EHV-07)
- Integration tests for doctor health checks, observability, evidence contract
- Bandit pre-commit hook for local SAST scanning

### Changed
- Fixed 23 silent bare except handlers (EHV-01 now PASS)
- Wired structured logging: __main__.py uses configure_logging(), 10 critical modules use get_logger()
- Engineering hygiene validators expanded from EHV-01..05 to EHV-01..08

## [0.27.0] - 2026-06-10

### Added
- Recruitize rating-healing implementation: CI quality gates, governance artifacts, cross-run state, evidence chain validators
- Coverage measurement in CI with 60% threshold
- Ruff linting enforced in CI
- Security audit step (pip-audit) in CI
- CODEOWNERS file for code ownership tracking
- Incident response and SLA documentation
- Pre-commit configuration for local development
- Cross-run state persistence (`state/run_history.py`) for adaptive retry
- Evidence chain validators (ECV-01..04) for cross-corroboration
- Integration tests for idempotency and failure gates

### Changed
- Version bumped from 0.1.0 to 0.27.0 (semantic versioning aligned with wave state)
- pyproject.toml: added coverage configuration

## [0.26.0] - 2026-06-09

### Added
- Wave 26: 28 DRYRUN scaffold packages, 19 BUILD_PASS
- Wave 25 correction: 8 contradictions documented
- Evidence bundle protocol v2

### Fixed
- W25 closure evidence invalidated and corrected

## [0.25.0] - 2026-06-09

### Added
- Fallback strategy configs and fixture resolution
- CLI flag support and family templates
- AMG governance and non-LowCode wiring

## [0.24.0] - 2026-06-08

### Added
- Wave 24: W23 false claims corrected, real target build
- Live PR branch audits for 3 plugin repos
- 13/13 BUILD_PASS from cloned repos

### Fixed
- W23 checked wrong product SDK repos; corrected to plugin repos

## [0.23.0] - 2026-06-08

### Added
- Pipeline parity closure and SharedDownstreamExecutor
- 19 SDE parity tests
- W22 issues resolved (6 items)

## [0.22.0] - 2026-06-08

### Added
- PLV-01..15 publication lifecycle validators
- 13 READMEs pushed to live branches
- 5 contracts authored

## [0.21.0] - 2026-06-08

### Added
- Non-LowCode pipeline parity: PPV-01..16 validators
- 60 files pushed to 3 live PR branches
- PR titles fixed to `feat(plugins):` convention

## [0.20.0] - 2026-06-07

### Added
- SVG svg-to-image-converter package (71st proven)
- LCV-01..15 lowcode completeness validators
- 13 packages across 3 live PRs

## [0.19.0] - 2026-06-06

### Added
- 4 new packages: cad/convert-dwg-to-pdf, cad/convert-dwg-to-jpg, barcode/1d-barcode-writer, barcode/2d-barcode-writer
- DWG fixture from aspose-cad repo
- 37 PCLC with PR packets

## [0.18.0] - 2026-06-06

### Added
- 11 new packages across barcode, threed, svg, font, finance, cad, omr
- TCC/BMV validators for taskcard closeout
- 33 PCLC PR packets

## [0.17.0] - 2026-06-06

### Added
- threed/convert-3d-model and font/convert-font packages
- TCV + PEV + BAV + PRC + PPL + FGS validators (16 rules)

## [0.16.0] - 2026-06-06

### Added
- html/convert-html-to-markdown, html/merge-html, gis/convert-gis-data, tasks/read-project-data
- EAV + PCLV + SHV + PRV validators (16 rules)

## [0.15.0] - 2026-06-05

### Added
- html/convert-html-to-xps, psd/convert-psd-to-png packages
- Evidence bundle protocol v1.1

## [0.14.0] - 2026-06-05

### Added
- tex/convert-latex-to-pdf, gis/read-gis-data packages
- EVC validators for evidence validity
