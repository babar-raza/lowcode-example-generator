# Changelog

All notable changes to the LowCode Example Generator are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses wave-based versioning aligned with sprint cycles.

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
