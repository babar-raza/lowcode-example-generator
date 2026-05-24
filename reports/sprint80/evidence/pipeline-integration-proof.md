# Pipeline Integration Proof -- Sprint 80

**Date:** 2026-05-24

## EvidenceValidator Wired into Pipeline

**Source:** src/plugin_examples/__main__.py
**Import:** from plugin_examples.evidence_validator import EvidenceValidator as _EV
**CLI argument:** --validate-bundle at lines 309-313
**Execution path:** lines 1475-1489

## EV Rule 111 Source

Added to src/plugin_examples/evidence_validator.py:
- Rule ID: no_active_validation_file_with_ambiguous_false
- Dispatch: _maybe(self._rule_no_active_validation_file_with_ambiguous_false())
- Docstring: Closes S79-B1

## SHA256 of evidence_validator.py

See source-hashes.json: 4aff7de73856d595d6d283084aa110675a458f8e0c3eda44e8b773e4924dc2f2
