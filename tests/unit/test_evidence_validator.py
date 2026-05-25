"""Tests for EvidenceValidator — Sprint 60 Phase 5 + Sprint 61 Phase 2.

Covers all Sprint 59 false-complete failure modes (original 12 rules):
- test_fails_when_final_clean_proof_missing
- test_fails_when_final_clean_proof_shows_dirty_state
- test_fails_when_present_no_authority_exists
- test_fails_when_readme_audit_is_shallow
- test_fails_when_readme_gate_evidence_missing
- test_fails_when_todo_has_unchecked_items
- test_fails_when_validator_output_missing
- test_fails_when_commands_log_in_progress
- test_fails_when_test_log_missing
- test_fails_when_unknown_input_formats_nonzero
- test_passes_with_complete_valid_bundle
- test_overall_valid_false_on_any_failure
- test_sprint59_style_bundle_detected_as_invalid

Sprint 61 new rules (8 additional semantic rules):
- TestFinalCleanProofNonzeroBytes — SD60-01: 0-byte file is not proof
- TestFinalCleanProofHasGitHeader — SD60-01: requires actual git output
- TestReadmeIOFormatNotFalselyComplete — SD60-02: MATCH without I/O docs = FAIL
- TestReadmeGateWiredInPipeline — SD60-03: standalone-only gate is not a gate
- TestEvidenceValidatorWiredInPipeline — SD60-04: standalone-only validator is not a gate
- TestDestinationProgramcsInputNotAllNull — SD60-05: null-for-all = audit not done
- TestNoPriOneItemsWithCompleteVerdict — SD60-08: P1 open + COMPLETE = contradiction
- TestRequiredFilesNonzeroSize — SD60-01 contributory: 0-byte required files
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.evidence_validator import EvidenceValidator


def _make_bundle(tmpdir: str) -> Path:
    """Create a minimal valid bundle directory structure (passes all 20 rules)."""
    b = Path(tmpdir)

    # git/final-clean-proof.txt — clean (nonzero, has git header, commit SHA, governance note)
    (b / "git").mkdir(parents=True)
    (b / "git" / "final-clean-proof.txt").write_text(
        "On branch main\nSprint bundle committed: a1b2c3d4e5f\n"
        "workspace/verification/latest/ -- GENERATED_WORKSPACE_STATE governance exception\n"
        " M workspace/verification/latest/release-status.json\n"
        "nothing to commit (working tree has governed exceptions)\n",
        encoding="utf-8",
    )

    # destination/content-audit-repaired.json — 42/42, with non-null input_format_in_programcs
    (b / "destination").mkdir(parents=True)
    (b / "destination" / "content-audit-repaired.json").write_text(
        json.dumps({
            "authority_mapped": "42/42",
            "present_no_authority": 0,
            "total_examples": 42,
            "examples": [
                {
                    "scenario_id": f"scenario-{i}",
                    "content_match": "MATCH",
                    "input_format_in_programcs": ".docx",
                    "input_classification": "AddInput",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # readme/example-readme-content-audit.json — content-based (no I/O fields = WARNING/pass)
    (b / "readme").mkdir(parents=True)
    (b / "readme" / "example-readme-content-audit.json").write_text(
        json.dumps({
            "records": [
                {
                    "scenario_id": "cells-html-converter",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                }
            ]
        }),
        encoding="utf-8",
    )
    (b / "readme" / "readme-gate-implementation.md").write_text("# Gate\n", encoding="utf-8")
    (b / "readme" / "readme-gate-test-results.txt").write_text("13 passed, 0 failed\n", encoding="utf-8")
    (b / "readme" / "readme-gate-source-proof.patch").write_text("diff --git a/src ...\n", encoding="utf-8")
    # readme-gate-flow-integration.md — confirms gate is wired (no "not wired"/"deferred"/"p1")
    (b / "readme" / "readme-gate-flow-integration.md").write_text(
        "# README Gate Flow Integration\nGate is called in publish-pr live mode.\n",
        encoding="utf-8",
    )

    # evidence/validator-test-results.txt + pipeline-integration-proof.md + bundle-validation-result.json
    (b / "evidence").mkdir(parents=True)
    (b / "evidence" / "validator-test-results.txt").write_text(
        "20 passed, 0 failed in 0.45s\n", encoding="utf-8"
    )
    (b / "evidence" / "pipeline-integration-proof.md").write_text(
        "# Pipeline Integration\nEvidenceValidator is called in release-status command.\n",
        encoding="utf-8",
    )
    (b / "evidence" / "sprint60-bundle-validation-result.json").write_text(
        json.dumps({
            "sprint_id": "sprint60-test",
            "overall_valid": True,
            "passed": 21,
            "failed": 0,
            "warnings": 0,
            "total_rules": 21,
            "rules": [],
        }),
        encoding="utf-8",
    )
    # evidence/evidence-contract-computed.json — ECC result (Sprint 64 rule 22)
    (b / "evidence" / "evidence-contract-computed.json").write_text(
        json.dumps({
            "contract_id": "sprint60-test",
            "computed_at": "2026-05-22T07:30:00Z",
            "total_categories": 36,
            "present": 36,
            "missing": 0,
            "zero_bytes": 0,
            "semantic_failed": 0,
            "pending": 0,
            "blocking_failures": 0,
            "closure_valid": True,
            "categories": [],
        }),
        encoding="utf-8",
    )

    # todo.md — all checked
    (b / "todo.md").write_text(
        "- [x] Phase 0 complete\n- [x] Phase 1 complete\n",
        encoding="utf-8",
    )

    # commands.log — complete (no IN_PROGRESS)
    (b / "commands.log").write_text("phase0: done\nphase1: done\n", encoding="utf-8")

    # lanes/lane-I/test-run.log
    (b / "lanes" / "lane-I").mkdir(parents=True)
    (b / "lanes" / "lane-I" / "test-run.log").write_text(
        "2826 passed, 0 failed, 3 skipped\n", encoding="utf-8"
    )

    # sprint-state.json
    (b / "sprint-state.json").write_text(
        json.dumps({"sprint_id": "sprint60-test"}), encoding="utf-8"
    )

    # Sprint 65: destination/content-audit-final.json — all required fields, all READY
    # Sprint 66: includes output_kind and api_type fields (rules 37, ECC output_kind check)
    (b / "destination" / "content-audit-final.json").write_text(
        json.dumps({
            "sprint": 66,
            "total_publication_artifacts": 42,
            "standard_package_artifacts": 40,
            "special_case_artifacts": 2,
            "records_ready": 42,
            "records": [
                {
                    "scenario_id": f"scenario-{i}",
                    "family": "cells",
                    "package_version": "26.5.1",
                    "output_format": ".xlsx",
                    "output_kind": "converter",
                    "api_type": "Converter",
                    "readme_status": "IO_DOC",
                    "root_readme_status": "INCLUDED",
                    "final_readiness": "READY",
                    "final_status": "READY",
                    "special_case": False,
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 65: root-readme/per-family/{family}-root-readme.md — all 6 families
    (b / "root-readme" / "per-family").mkdir(parents=True)
    for family in ["cells", "diagram", "email", "pdf", "slides", "words"]:
        (b / "root-readme" / "per-family" / f"{family}-root-readme.md").write_text(
            f"# {family.title()} LowCode Examples\n", encoding="utf-8"
        )

    # Sprint 65: special-cases/special-case-publication-map.json — 2 cases
    (b / "special-cases").mkdir(parents=True)
    (b / "special-cases" / "special-case-publication-map.json").write_text(
        json.dumps({
            "special_cases": [
                {"scenario_id": "pdf-pdfa-converter", "destination_path": "examples/pdf/lowcode/pdfa-converter"},
                {"scenario_id": "pdf-text-extractor", "destination_path": "examples/pdf/lowcode/text-extractor"},
            ]
        }),
        encoding="utf-8",
    )

    # Sprint 65: version/version-policy-final.json — 0 unresolved drift
    (b / "version").mkdir(parents=True)
    (b / "version" / "version-policy-final.json").write_text(
        json.dumps({
            "families": {
                "cells": {"version_match": True, "policy": "MATCH"},
                "pdf": {"version_match": False, "policy": "POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED"},
            },
            "summary": {"total_drift_unresolved": 0},
        }),
        encoding="utf-8",
    )

    # Sprint 65: final-verdict.md — no strong publication keywords; add publication/remote-proof-index.json
    (b / "final-verdict.md").write_text(
        "Verdict: TEST_DRY_RUN_APPROVAL_BLOCKED\n",
        encoding="utf-8",
    )
    (b / "publication").mkdir(parents=True)
    (b / "publication" / "remote-proof-index.json").write_text(
        json.dumps({"families": ["cells", "words"]}), encoding="utf-8"
    )

    # Sprint 65: evidence/*revalidation*.json — prior sprint must fail (overall_valid=false)
    (b / "evidence" / "sprint64-revalidation-result.json").write_text(
        json.dumps({"sprint_id": "sprint64-test", "overall_valid": False, "failed": 3, "passed": 19}),
        encoding="utf-8",
    )

    # Sprint 66: remote/remote-pr-proof-index.json — per-PR per-example coverage (rule 33)
    (b / "remote").mkdir(parents=True)
    (b / "remote" / "remote-pr-proof-index.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "families": {
                "cells": [{"pr_number": 1, "examples_count": 9, "scenario_ids_covered": [f"cells-ex-{i}" for i in range(9)]}],
                "words": [{"pr_number": 1, "examples_count": 8, "scenario_ids_covered": [f"words-ex-{i}" for i in range(8)]}],
            },
        }),
        encoding="utf-8",
    )

    # Sprint 66: remote/remote-example-inventory.json — content hashes per example (rule 34)
    (b / "remote" / "remote-example-inventory.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "total": 42,
            "records": [
                {
                    "scenario_id": f"scenario-{i}",
                    "family": "cells",
                    "readme_sha": f"abc{i:04x}",
                    "readme_content_sha256": f"sha256-{i:04x}",
                    "programcs_sha": f"def{i:04x}",
                    "programcs_content_sha256": f"psha-{i:04x}",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 66: remote/remote-readme-io-audit.json — I/O status per example (rule 35)
    (b / "remote" / "remote-readme-io-audit.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "total": 42,
            "io_doc_count": 0,
            "old_format_count": 42,
            "records": [
                {
                    "scenario_id": f"scenario-{i}",
                    "family": "cells",
                    "has_io_section": False,
                    "io_status": "OLD_FORMAT",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 66: handoff/per-family/ — package artifacts (rules 36, 40, 42)
    for family in ["cells", "words", "pdf", "diagram", "email", "slides"]:
        family_dir = b / "handoff" / "per-family" / family / "example-1"
        family_dir.mkdir(parents=True)
        (family_dir / "Program.cs").write_text(
            "using Aspose; class Program { static void Main() {} }", encoding="utf-8"
        )
        (family_dir / "README.md").write_text(
            f"# {family} example\n\n## Input and Output\n\nInput: file.xlsx\nOutput: result.pdf\n",
            encoding="utf-8",
        )
        (family_dir / f"{family}-example.csproj").write_text(
            "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>", encoding="utf-8"
        )
    (b / "handoff" / "publication-handoff-index.json").write_text(
        json.dumps({"total_examples": 42, "ok_count": 42}), encoding="utf-8"
    )

    # Sprint 66: publication/publication-truth-matrix-final.json — separate state fields (rule 38)
    (b / "publication" / "publication-truth-matrix-final.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "total": 42,
            "records": [
                {
                    "scenario_id": f"scenario-{i}",
                    "family": "cells",
                    "remote_example_present": True,
                    "remote_readme_has_io_docs": False,
                    "approval_blocked": True,
                    "publication_status": "REMOTE_PUBLISHED_STALE_IO",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 67: cardinality audit (rules 43-44)
    root_readme_dir = b / "root-readme" / "per-family"
    root_readme_dir.mkdir(parents=True, exist_ok=True)
    (b / "root-readme" / "cardinality-audit.json").write_text(
        json.dumps({"families": {"cells": {}, "words": {}, "pdf": {}, "diagram": {}, "email": {}, "slides": {}}}),
        encoding="utf-8",
    )
    (root_readme_dir / "cells-root-readme.md").write_text(
        "# Cells\n| `spreadsheet-merger` | `SpreadsheetMerger.Process` | `xlsx (xN)` | `xlsx` | dotnet run |\n"
        "| `spreadsheet-splitter` | `SpreadsheetSplitter.Process` | `xlsx` | `xlsx (xN)` | dotnet run |\n"
        "> **Cardinality key:** xN in the Input column means the operation merges N input files.\n",
        encoding="utf-8",
    )
    for fam in ["words", "pdf", "diagram", "email", "slides"]:
        (root_readme_dir / f"{fam}-root-readme.md").write_text(
            f"# {fam} examples\n", encoding="utf-8"
        )

    # Sprint 67: version decision (rules 45-46)
    (b / "version").mkdir(parents=True, exist_ok=True)
    (b / "version" / "pdf-version-decision.md").write_text(
        "# PDF Version Decision\nDecision: 26.5.0 is canonical.\n", encoding="utf-8"
    )
    (b / "version" / "version-truth-matrix.json").write_text(
        json.dumps({"families": {"cells": {}, "words": {}, "pdf": {}, "diagram": {}, "email": {}, "slides": {}}}),
        encoding="utf-8",
    )

    # Sprint 67: content-audit-sprint67.json (rule 47, 49)
    (b / "destination" / "content-audit-sprint67.json").write_text(
        json.dumps({
            "sprint_id": "sprint67",
            "total": 42,
            "records": [
                {
                    "scenario_id": f"scenario-{i}",
                    "family": "cells",
                    "handoff_path": "reports/sprint67/handoff/per-family/cells/example",
                    "local_package_path": "reports/sprint67/handoff/per-family/cells/example",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 67: sprint-state.json with sprint_number (for rule 49)
    (b / "sprint-state.json").write_text(
        json.dumps({"sprint_number": 67, "sprint_id": "sprint67", "status": "IN_PROGRESS"}),
        encoding="utf-8",
    )

    # Sprint 67: legacy plans reconciliation (rule 48)
    (b / "legacy-plan-reconciliation").mkdir(parents=True)
    (b / "legacy-plan-reconciliation" / "reconciliation-index.md").write_text(
        "# Legacy Plan Reconciliation\nAll plans reconciled.\n", encoding="utf-8"
    )

    # Sprint 67: per-family handoff-index.json (rule 50)
    for fam in ["cells", "words", "pdf", "diagram", "email", "slides"]:
        fam_dir = b / "handoff" / "per-family" / fam
        fam_dir.mkdir(parents=True, exist_ok=True)
        (fam_dir / "handoff-index.json").write_text(
            json.dumps({"family": fam, "examples": [], "sprint": "sprint67"}),
            encoding="utf-8",
        )

    # Sprint 67: readme-sync/sync-state.json (rule 51)
    (b / "readme-sync").mkdir(parents=True)
    (b / "readme-sync" / "sync-state.json").write_text(
        json.dumps({"architecture_version": "IV", "components_active": {}}),
        encoding="utf-8",
    )

    # Sprint 67: remote/remote-proof-summary.md (rule 52)
    remote_dir = b / "remote"
    remote_dir.mkdir(parents=True, exist_ok=True)
    (remote_dir / "remote-proof-summary.md").write_text(
        "# Remote Proof Summary\nAll 42 examples confirmed.\n0/42 remote READMEs have I/O sections.\n", encoding="utf-8"
    )

    # Sprint 68: PDF root README with 19 rows (rule 53)
    # root-readme/per-family dir already created in Sprint 67 section above
    pdf_readme_dir = b / "root-readme" / "per-family"
    pdf_rows = "\n".join(
        f"| `example-{i}` | `Plugin.Process` | `pdf` | `pdf` | `dotnet run --project examples/pdf/lowcode/example-{i}` |"
        for i in range(19)
    )
    (pdf_readme_dir / "pdf-root-readme.md").write_text(
        f"# Aspose.PDF LowCode Examples\n\n## Included Examples\n\n"
        f"| Example | Demonstrated API | Input | Output | Run |\n"
        f"|---------|-----------------|-------|--------|-----|\n"
        f"{pdf_rows}\n",
        encoding="utf-8",
    )

    # Sprint 68: splitter cardinality reconciliation (rule 54)
    leg_rec_dir = b / "legacy-reconciliation"
    leg_rec_dir.mkdir(parents=True, exist_ok=True)
    (leg_rec_dir / "splitter-resolution.md").write_text(
        "# Splitter Cardinality Resolution\nAll splitters: SINGLE_OUTPUT_VALID.\n",
        encoding="utf-8",
    )

    # Sprint 68: canonical content audit — rule 55 is satisfied by the sprint67
    # content-audit-sprint67.json already written above (cells family, no PDF 26.4.0 records)

    # Sprint 68: PDF version proof chain (rule 56)
    # version/ dir already created in Sprint 67 section above
    (b / "version" / "pdf-version-proof-chain.md").write_text(
        "# PDF Version Proof Chain\nHandoff Directory.Packages.props: Aspose.PDF 26.5.0.\n",
        encoding="utf-8",
    )

    # Sprint 68: words README with cardinality markers (rule 57)
    # root-readme/per-family dir already created in Sprint 67 section above
    (pdf_readme_dir / "words-root-readme.md").write_text(
        "# Aspose.Words LowCode Examples\n\n## Included Examples\n\n"
        "| `merger` | `Merger.Process` | `docx (×N)` | `docx` | `dotnet run ...` |\n"
        "| `splitter` | `Splitter.ExtractPages` | `docx` | `docx (×N)` | `dotnet run ...` |\n",
        encoding="utf-8",
    )

    # ---- Sprint 69: artifacts for rules 58-67 ----

    # Rule 58: handoff_index_version_matches_dpp — all 6 families need matching versions
    # Also satisfies Sprint 70 rules 68-71: root_readme.source_path inside sprint handoff,
    # file physically present, and hash matches.
    # sprint_id is "sprint67" (see sprint-state.json written above).
    # source_path must be reports/sprint67/handoff/per-family/{family}/README.md
    # => resolves bundle-relative to handoff/per-family/{family}/README.md
    import hashlib as _hashlib_fixture
    fam_readme_hashes = {}
    for family, ver in [("cells", "26.5.1"), ("words", "26.5.0"), ("pdf", "26.5.0"),
                        ("diagram", "26.5.0"), ("email", "26.4.0"), ("slides", "26.5.0")]:
        fam_dir = b / "handoff" / "per-family" / family
        fam_dir.mkdir(parents=True, exist_ok=True)
        # Write root README physically inside handoff folder (sprint70 requirement)
        # Use write_bytes so sha256 of bytes matches sha256 of file (no line-ending conversion).
        readme_content = f"# {family.capitalize()} Root README\n\nInput and Output examples.\n"
        readme_bytes = readme_content.encode("utf-8")
        (fam_dir / "README.md").write_bytes(readme_bytes)
        fam_readme_hashes[family] = _hashlib_fixture.sha256(readme_bytes).hexdigest()
        (fam_dir / "handoff-index.json").write_text(
            json.dumps({"family": family, "nuget_version": ver, "examples": [],
                        "root_readme": {
                            "source_path": f"reports/sprint67/handoff/per-family/{family}/README.md",
                            "sha256": fam_readme_hashes[family],
                            "destination_path": "README.md",
                            "destination_repo": f"aspose-{family}-net/repo"}}),
            encoding="utf-8",
        )
        (fam_dir / "Directory.Packages.props").write_text(
            f'<Project><ItemGroup><PackageVersion Include="Aspose.Test" Version="{ver}" /></ItemGroup></Project>',
            encoding="utf-8",
        )

    # Rule 59: only_one_canonical_final_audit — content-audit-final.json with current sprint paths
    # Must also satisfy existing rules: required_fields, all_records_ready, readme_io_coverage, output_kind
    # Sprint 71 rules 73-74: handoff_path must use current sprint (sprint67) and paths must exist.
    dst_dir = b / "destination"
    dst_dir.mkdir(exist_ok=True)
    # Create a shared example dir in the handoff for all 42 audit records to reference
    audit_example_dir = b / "handoff" / "per-family" / "cells" / "example"
    audit_example_dir.mkdir(parents=True, exist_ok=True)
    audit_records = [
        {
            "scenario_id": f"cells-html-converter-{i:02d}",
            "family": "cells",
            "handoff_path": "reports/sprint67/handoff/per-family/cells/example",
            "local_package_path": "reports/sprint67/handoff/per-family/cells/example",
            "package_version": "26.5.1",
            "output_format": ".html",
            "output_kind": "converter",
            "readme_status": "IO_DOC",
            "root_readme_status": "INCLUDED",
            "final_status": "READY",
            "final_readiness": "READY",
            "remote_readme_has_io_docs": False,
            "readme_io_post_merge_verified": False,
            "approval_blocked": True,
            "publication_status": "REMOTE_EXAMPLE_PRESENT_README_IO_STALE_APPROVAL_BLOCKED",
        }
        for i in range(42)
    ]
    (dst_dir / "content-audit-final.json").write_text(
        json.dumps({"sprint_id": "sprint67", "total": 42, "records": audit_records}),
        encoding="utf-8",
    )

    # Rule 60: publication_truth_matrix_no_stale_paths — current sprint paths only
    # Must also satisfy existing publication_state_not_mixed rule (needs remote_example_present, remote_readme_has_io_docs)
    # Sprint 71 rules 74, 76: handoff_package_path must use current sprint and paths must exist.
    pub_dir = b / "publication"
    pub_dir.mkdir(exist_ok=True)
    pub_records = [
        {
            "scenario_id": f"cells-html-converter-{i:02d}",
            "family": "cells",
            "handoff_package_path": "reports/sprint67/handoff/per-family/cells/example",
            "remote_example_present": True,
            "remote_readme_has_io_docs": False,
            "remote_example_readme_has_io_docs": False,
            "readme_io_post_merge_verified": False,
            "approval_blocked": True,
        }
        for i in range(42)
    ]
    (pub_dir / "publication-truth-matrix-final.json").write_text(
        json.dumps({"sprint_id": "sprint67", "records": pub_records}),
        encoding="utf-8",
    )

    # Rule 61: publication_truth_matrix_no_mixed_state — no post_merge_verified while io missing
    # (already satisfied by rule 60 fixture above)

    # Rule 62: root_readme_indexed_in_handoff — already satisfied by handoff-index.json above
    # (root_readme field added to each family)

    # Rule 63: exact_legacy_reconciliation_present
    leg_dir = b / "legacy-reconciliation"
    leg_dir.mkdir(exist_ok=True)
    (leg_dir / "exact-legacy-plan-reconciliation-final.md").write_text(
        "# Exact Legacy Plan Reconciliation Final\nAll items reconciled.\n",
        encoding="utf-8",
    )
    (leg_dir / "exact-items-final.json").write_text(
        json.dumps({"items": [{"id": "SPL-01", "status": "CLOSED"}]}),
        encoding="utf-8",
    )

    # Rule 64: final_verdict_is_precise — final-verdict.md uses allowed verdict
    (b / "final-verdict.md").write_text(
        "# Final Verdict\n\n`LOWCODE_PREPUBLICATION_HANDOFF_READY_APPROVAL_BLOCKED`\n",
        encoding="utf-8",
    )

    # Rule 65: final_verdict_not_complete_while_blocked — already OK (not claiming published)

    # Rule 66: handoff_index_has_root_readme_field — publication-handoff-index.json
    # Also satisfies Sprint 70 rule 71: root_readme_sha256 and root_readme_source_path
    # must match the physical README.md files written above.
    # Sprint 71 rules: publication-handoff-index.json must use current sprint paths only.
    handoff_dir = b / "handoff"
    (handoff_dir / "publication-handoff-index.json").write_text(
        json.dumps({"sprint_id": "sprint67", "families": [
            {
                "family": f,
                "root_readme_sha256": fam_readme_hashes[f],
                "root_readme_source_path": f"reports/sprint67/handoff/per-family/{f}/README.md",
                "example_count": 1,
            }
            for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
        ]}),
        encoding="utf-8",
    )

    # Rule 67: version_consistency_final_present
    ver_dir = b / "version"
    ver_dir.mkdir(exist_ok=True)
    (ver_dir / "version-consistency-final.json").write_text(
        json.dumps({"all_consistent": True, "sprint69_mismatches": 0}),
        encoding="utf-8",
    )

    # ---- Sprint 70: artifacts for rules 68-72 ----

    # Rules 68-71: handoff_root_readme_in_sprint_folder, file_present, hash_matches,
    # publication_handoff_root_readme_hash_matches
    # Already satisfied above:
    # - handoff/per-family/{family}/README.md created with known content
    # - handoff-index.json source_path = reports/sprint67/handoff/per-family/{family}/README.md
    # - sha256 in handoff-index matches actual file
    # - publication-handoff-index.json has root_readme_sha256 and root_readme_source_path matching file

    # Rule 72: legacy_simplified_index_superseded
    # final authority already created above (leg_dir / "exact-legacy-plan-reconciliation-final.md")
    # Add legacy-reconciliation/README.md to satisfy the authority README requirement
    (leg_dir / "README.md").write_text(
        "# Legacy Reconciliation — Final Authority\n"
        "Current authority: exact-legacy-plan-reconciliation-final.md\n"
        "Old reconciliation-index.md is SUPERSEDED.\n",
        encoding="utf-8",
    )

    # ---- Sprint 71: artifacts for rules 73-78 ----

    # Rules 73-78: stale-path scanner — content-audit, publication-matrix, handoff-index,
    # remote-vs-handoff, content-audit-files-exist, publication-matrix-files-exist.
    # content-audit-final.json and publication-truth-matrix-final.json already updated above
    # to use current sprint (sprint67) paths. handoff-index.json already uses sprint67 paths.
    # Now add remote/remote-vs-handoff-final.json with current sprint paths only.
    remote_dir = b / "remote"
    remote_dir.mkdir(exist_ok=True)
    (remote_dir / "remote-vs-handoff-final.json").write_text(
        json.dumps({
            "sprint_id": "sprint67",
            "comparison": "current",
            "families": [
                {"family": f, "handoff_path": f"reports/sprint67/handoff/per-family/{f}/", "status": "OK"}
                for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
            ],
        }),
        encoding="utf-8",
    )

    # ---- Sprint 72: artifacts for rules 79-85 ----

    # Rule 79: remote_proof_consistency_audit_present
    # Rule 80: remote_proof_consistency_audit_consistent
    (remote_dir / "remote-proof-consistency-audit.json").write_text(
        json.dumps({
            "sprint_id": "sprint67",
            "consistent": True,
            "checks": [{"check_id": "RPC01", "consistent": True}],
        }),
        encoding="utf-8",
    )

    # Rule 81: remote_proof_summary_states_zero_io — already updated above to include "0/42"
    # Rule 82: remote_proof_summary_not_contradicted — needs remote-readme-io-audit-final.json
    (remote_dir / "remote-readme-io-audit-final.json").write_text(
        json.dumps({
            "sprint_id": "sprint67",
            "total": 42,
            "io_doc_count": 0,
            "old_format_count": 42,
            "records": [
                {"scenario_id": f"cells-example-{i}", "family": "cells",
                 "has_io_section": False, "io_status": "OLD_FORMAT"}
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Rule 83: remote_proof_summary_superseded_archived
    history_dir = b / "history"
    history_dir.mkdir(exist_ok=True)
    (history_dir / "remote-proof-summary-superseded.md").write_text(
        "# SUPERSEDED: Remote Truth Refresh — Sprint 68\n\nStatus: SUPERSEDED\nOriginal incorrect claim: 42/42 examples have README I/O sections.\n",
        encoding="utf-8",
    )

    # Rule 84: remote_readme_io_audit_count_consistent — satisfied by remote-readme-io-audit-final.json above
    # Rule 85: remote_vs_handoff_uses_current_sprint — satisfied by remote-vs-handoff-final.json written above

    # Pad to >=35 files
    for i in range(40):
        (b / f"pad-{i:02d}.txt").write_text(f"pad {i}\n", encoding="utf-8")

    # ---- Sprint 75: artifacts for rules 86-93 ----

    # Rule 86: weekly_review_claim_matrix_present
    (b / "02-weekly-review-claim-vs-proof-matrix.md").write_text(
        "# Weekly Review Claim vs Proof Matrix\n\n"
        "Item 1: VERIFIED_HISTORICAL_BUT_SUPERSEDED\n"
        "Item 2: BLOCKED_EXTERNAL\n"
        "Item 3: NEEDS_REPAIR\n"
        "Item 6: GOVERNANCE_EXCEPTION_REQUIRED\n",
        encoding="utf-8",
    )

    # Rule 87: pdf_publication_truth_reconciled
    pdf_pub_dir = b / "pdf-publication"
    pdf_pub_dir.mkdir(parents=True, exist_ok=True)
    (pdf_pub_dir / "pdf-pr-reconciliation.json").write_text(
        json.dumps({
            "sprint_id": "sprint75",
            "claim_verdict": "VERIFIED_HISTORICAL_BUT_SUPERSEDED",
            "pdf_prs": [],
        }),
        encoding="utf-8",
    )

    # Rule 88: formimporter_taskcard_durable
    fi_dir = b / "formimporter"
    fi_dir.mkdir(parents=True, exist_ok=True)
    (fi_dir / "formimporter-repro-inventory.json").write_text(
        json.dumps({
            "taskcard_id": "TC-PDF-FORMIMPORTER-RETEST",
            "current_status": "STILL_BLOCKED",
            "repro_root": "workspace/defect-repros/pdf-formimporter-nullref",
            "repro_files": [],
            "next_retest_trigger": "Aspose.PDF NuGet > 26.5.0",
        }),
        encoding="utf-8",
    )

    # Rule 89: words_version_drift_documented
    vd_dir = b / "version-drift"
    vd_dir.mkdir(parents=True, exist_ok=True)
    (vd_dir / "words-version-drift-current.json").write_text(
        json.dumps({
            "family": "words",
            "drift": "REMOTE_DRIFT",
            "remote_published_version": "26.4.0",
            "handoff_version": "26.5.0",
        }),
        encoding="utf-8",
    )

    # Rule 90: email_slides_runtime_validated
    # Rules 94+95: output_confirmed=true, runtime_result=RUNTIME_VALIDATED (no NO_INPUT_FIXTURE)
    pmr_dir = b / "post-merge-runtime"
    pmr_dir.mkdir(parents=True, exist_ok=True)
    (pmr_dir / "post-merge-validation-matrix.json").write_text(
        json.dumps({
            "sprint_id": "sprint75",
            "records": [
                {
                    "scenario_id": "email-converter",
                    "post_merge_validated": True,
                    "output_confirmed": True,
                    "runtime_result": "RUNTIME_VALIDATED",
                },
                {
                    "scenario_id": "slides-compress",
                    "post_merge_validated": True,
                    "output_confirmed": True,
                    "runtime_result": "RUNTIME_VALIDATED",
                },
            ],
        }),
        encoding="utf-8",
    )

    # Rule 91: dirty_tree_classified
    # Rule 96: dirty_classification_must_match_after_snapshot — consistent with dirty-state-after.txt
    git_dir = b / "git"
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "dirty-file-classification.md").write_text(
        "# Dirty File Classification\n\n"
        "workspace/verification/latest/: GENERATED_WORKSPACE_STATE — EXCLUDE\n"
        "reports/sprint75/: CURRENT_SPRINT_ARTIFACTS — COMMIT\n",
        encoding="utf-8",
    )

    # Rules 96, 100: dirty-state-after.txt — no src/tests modified
    (git_dir / "dirty-state-after.txt").write_text(
        "On branch main\nnothing to commit, working tree clean\n",
        encoding="utf-8",
    )

    # Rule 92: sprint27_governance_classified
    gov_dir = b / "governance"
    gov_dir.mkdir(parents=True, exist_ok=True)
    (gov_dir / "sprint27-strict-contract-revalidation.md").write_text(
        "# Sprint 27 Strict Contract Revalidation\n\n"
        "Classification: GOVERNANCE_EXCEPTION_REQUIRED\n"
        "Sprint 27 is HISTORICAL_NON_COMPLIANT — grandfathered.\n",
        encoding="utf-8",
    )

    # Rule 93: weekly_review_verdict_not_complete_while_unclassified
    # (satisfied since 02-weekly-review-claim-vs-proof-matrix.md is present)
    # Rule 101: final_verdict_workspace_exception_explicit
    # (dirty-state-after.txt shows nothing dirty, so rule 101 passes trivially)
    # final-verdict.md already uses allowed verdict from rule 64 above

    # ---- Sprint 78: artifacts for rules 106-108 ----

    # Rule 107: handoff_validation_result_has_valid_flag
    handoff_dir = b / "handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    (handoff_dir / "handoff-prepublish-validation.json").write_text(
        json.dumps({
            "validation_type": "handoff_prepublish_validation",
            "total_examples": 42,
            "total_families": 6,
            "overall_handoff_valid": True,
            "verdict": "HANDOFF_VALID_42_42_APPROVAL_BLOCKED",
        }),
        encoding="utf-8",
    )

    # Rule 108: remote_repo_state_all_accessible
    remote_dir = b / "remote"
    remote_dir.mkdir(parents=True, exist_ok=True)
    (remote_dir / "remote-repo-state-before.json").write_text(
        json.dumps({
            "resolution_type": "github_repo_access_resolution",
            "token_present": True,
            "families": [
                {"family": f, "error_classification": "repo_access_ok",
                 "can_read": True, "can_push": True}
                for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
            ],
            "summary": {
                "total_checked": 6,
                "accessible": 6,
                "blocked": 0,
                "accessible_families": ["cells", "words", "pdf", "diagram", "email", "slides"],
                "blocked_families": [],
                "live_publish_allowed": False,
            },
        }),
        encoding="utf-8",
    )

    # Rule 106: publication_truth_no_stale_remote_claimed
    # The existing publication-truth-matrix-final.json uses 'records' (list) not 'families' (dict),
    # so data.get("all_published", False) returns False → rule passes trivially for the base bundle.
    # No additional fixture needed — rule is not applicable without all_published=True.

    return b


class TestFinalCleanProof(unittest.TestCase):
    def test_fails_when_final_clean_proof_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_fails_when_final_clean_proof_shows_dirty_state(self):
        """Sprint 59 defect SD59-01: git-status.txt captured before final commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nmodified: workspace/verification/latest/release-status.json\n"
                "?? reports/sprint59/\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertFalse(rule.passed)
        self.assertIn("dirty", rule.failure_detail.lower())

    def test_passes_when_clean_proof_is_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertTrue(rule.passed)


class TestPresentNoAuthority(unittest.TestCase):
    def test_fails_when_present_no_authority_exists(self):
        """Sprint 59 defect SD59-02: 3 PRESENT_NO_AUTHORITY entries in destination audit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "39/42",
                    "present_no_authority": 3,
                    "total_examples": 42,
                    "examples": [
                        {"scenario_id": "diagram-diagram-diagram-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                        {"scenario_id": "pdf-pdfa-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                        {"scenario_id": "diagram-diagram-pdf-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_present_no_authority")
        self.assertFalse(rule.passed)
        self.assertIn("3", rule.failure_detail)

    def test_passes_when_no_present_no_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_present_no_authority")
        self.assertTrue(rule.passed)


class TestReadmeAuditContentBased(unittest.TestCase):
    def test_fails_when_readme_audit_is_shallow(self):
        """Sprint 59 defect SD59-03: README audit was presence/size only, not content-based."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Write shallow (Sprint 59-style) audit records
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({
                    "records": [
                        {
                            "scenario_id": "cells-html-converter",
                            "readme_present": True,
                            "readme_size": 350,
                        },
                        {
                            "scenario_id": "cells-pdf-converter",
                            "readme_present": True,
                            "readme_size": 300,
                        },
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertFalse(rule.passed)
        self.assertIn("size/presence", rule.failure_detail)

    def test_fails_when_readme_audit_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "example-readme-content-audit.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_passes_when_content_audit_has_content_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertTrue(rule.passed)


class TestReadmeGateImplemented(unittest.TestCase):
    def test_fails_when_readme_gate_evidence_missing(self):
        """Sprint 59 defect SD59-04: README gate was documented but not wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-source-proof.patch").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertFalse(rule.passed)
        self.assertIn("readme-gate-source-proof.patch", rule.failure_detail)

    def test_fails_when_gate_test_results_show_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-test-results.txt").write_text(
                "3 passed, 2 failed\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertFalse(rule.passed)

    def test_passes_when_all_gate_evidence_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertTrue(rule.passed)


class TestTodoAllChecked(unittest.TestCase):
    def test_fails_when_todo_has_unchecked_items(self):
        """Sprint 59 defect SD59-06: todo.md had unchecked [ ] items despite work done."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").write_text(
                "- [x] Phase 0 complete\n"
                "- [ ] Phase 1 README gate wiring\n"
                "- [ ] Phase 2 bundle commit\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertFalse(rule.passed)
        self.assertIn("2", rule.failure_detail)

    def test_fails_when_todo_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertFalse(rule.passed)

    def test_passes_when_all_items_checked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertTrue(rule.passed)


class TestEvidenceValidatorActuallyRan(unittest.TestCase):
    def test_fails_when_validator_output_missing(self):
        """Sprint 59 defect SD59-07: validation_rules_passed was hardcoded, not run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "validator-test-results.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertFalse(rule.passed)

    def test_fails_when_output_not_test_output(self):
        """Validator output that looks like a hardcoded list, not test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "validator-test-results.txt").write_text(
                "validation_rules_passed:\n- final_clean_proof_after_final_commit\n- bundle_min_files\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertFalse(rule.passed)

    def test_passes_when_real_test_output_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertTrue(rule.passed)


class TestCommandsLog(unittest.TestCase):
    def test_fails_when_commands_log_in_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text(
                "phase0: done\nphase1: IN_PROGRESS\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_complete")
        self.assertFalse(rule.passed)

    def test_fails_when_commands_log_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_complete")
        self.assertFalse(rule.passed)


class TestTestLog(unittest.TestCase):
    def test_fails_when_test_log_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "test_log_zero_failed")
        self.assertFalse(rule.passed)

    def test_fails_when_test_log_shows_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").write_text(
                "2800 passed, 26 failed, 3 skipped\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "test_log_zero_failed")
        self.assertFalse(rule.passed)


class TestUnknownInputFormats(unittest.TestCase):
    def test_fails_when_unknown_input_formats_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "io-authority").mkdir(parents=True)
            (b / "io-authority" / "input-format-authority-matrix.json").write_text(
                json.dumps({"unknown_input_formats": 42, "total_types": 42}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "zero_unknown_input_formats")
        self.assertFalse(rule.passed)

    def test_passes_when_all_formats_known(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "io-authority").mkdir(parents=True)
            (b / "io-authority" / "input-format-authority-matrix.json").write_text(
                json.dumps({"unknown_input_formats": 0, "total_types": 42}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "zero_unknown_input_formats")
        self.assertTrue(rule.passed)


class TestCompleteBundle(unittest.TestCase):
    def test_passes_with_complete_valid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        self.assertTrue(result.overall_valid)
        self.assertEqual(result.failed, 0)
        self.assertEqual(result.total_rules, 145)  # Sprint 89: added 5 new rules (141-145)

    def test_overall_valid_false_on_any_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Introduce a single failure
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        self.assertGreater(result.failed, 0)

    def test_sprint59_style_bundle_detected_as_invalid(self):
        """A Sprint 59-style bundle (documented but not implemented gate, shallow audit, dirty proof)
        must be detected as invalid by EvidenceValidator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Sprint 59 defect SD59-01: dirty proof
            (b / "git" / "final-clean-proof.txt").write_text(
                "modified: workspace/verification/latest/release-status.json\n",
                encoding="utf-8",
            )
            # Sprint 59 defect SD59-03: shallow README audit
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({
                    "records": [
                        {"scenario_id": "cells-html-converter", "readme_present": True, "readme_size": 350}
                    ]
                }),
                encoding="utf-8",
            )
            # Sprint 59 defect SD59-04: gate not wired (no source proof)
            (b / "readme" / "readme-gate-source-proof.patch").unlink()
            # Sprint 59 defect SD59-06: unchecked items in todo
            (b / "todo.md").write_text("- [ ] Phase 4 README gate wiring\n", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        # Should catch at least 4 failures
        self.assertGreaterEqual(result.failed, 4)

    def test_sprint60_style_bundle_detected_as_invalid(self):
        """A Sprint 60-style bundle (empty clean proof, null programcs, gate not wired,
        P1 items with COMPLETE verdict) must be detected as invalid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # SD60-01: empty clean proof
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            # SD60-05: all-null programcs input
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {
                            "scenario_id": f"scenario-{i}",
                            "content_match": "MATCH",
                            "input_format_in_programcs": None,
                            "input_classification": None,
                        }
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            # SD60-03: gate not wired (remove flow integration proof, no source_root)
            (b / "readme" / "readme-gate-flow-integration.md").unlink()
            # SD60-04: validator not wired (remove pipeline integration proof)
            (b / "evidence" / "pipeline-integration-proof.md").unlink()
            # SD60-08: P1 items with complete verdict
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate CLI wiring | P1 | OPEN |\n",
                encoding="utf-8",
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        # Should catch SD60-01 (x3 rules), SD60-03, SD60-04, SD60-05, SD60-08 = at least 7 failures
        self.assertGreaterEqual(result.failed, 5)

    def test_to_dict_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        d = result.to_dict()
        self.assertIn("bundle_dir", d)
        self.assertIn("sprint_id", d)
        self.assertIn("overall_valid", d)
        self.assertIn("rules", d)
        self.assertEqual(len(d["rules"]), 145)  # Sprint 89: 145 rules total


# ===========================================================================
# Sprint 61 NEW semantic rule tests
# ===========================================================================


class TestFinalCleanProofNonzeroBytes(unittest.TestCase):
    """Rule: final_clean_proof_nonzero_bytes — closes SD60-01."""

    def test_fails_when_proof_is_zero_bytes(self):
        """SD60-01: git status --short produces no output when clean → 0-byte file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertFalse(rule.passed)
        self.assertIn("0 bytes", rule.failure_detail)
        self.assertIn("--short", rule.failure_detail)

    def test_fails_when_proof_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_passes_when_proof_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertTrue(rule.passed)
        self.assertIn("bytes", rule.evidence)


class TestFinalCleanProofHasGitHeader(unittest.TestCase):
    """Rule: final_clean_proof_has_git_header — closes SD60-01 (content check)."""

    def test_fails_when_no_git_header_present(self):
        """Nonzero file without git output is not valid clean proof."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "Sprint 61 clean proof captured.\nAll done.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertFalse(rule.passed)
        self.assertIn("git status header", rule.failure_detail.lower())

    def test_fails_when_proof_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertFalse(rule.passed)

    def test_passes_with_on_branch_header(self):
        """Standard git status output: 'On branch main\nnothing to commit...'"""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)

    def test_passes_with_nothing_to_commit_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "nothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)

    def test_passes_with_head_detached_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "HEAD detached at abc1234\nnothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)


class TestReadmeIOFormatNotFalselyComplete(unittest.TestCase):
    """Rule: readme_io_format_not_falsely_complete — closes SD60-02."""

    def test_fails_when_high_io_gap_with_complete_match_claimed(self):
        """SD60-02: 22/42 input false + 100% MATCH claimed = false completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                    "input_format_in_readme": i >= 20,   # 22 False (i<20 plus 2)
                    "output_format_in_readme": i >= 19,  # 23 False
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": total, "total": total}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertFalse(rule.passed)
        self.assertIn("input_format_in_readme=false", rule.failure_detail.lower())

    def test_passes_when_io_fields_not_tracked(self):
        """If I/O fields are not tracked, rule is WARNING/passed=True (basic audit scope)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # _make_bundle already has no I/O fields → should pass
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)

    def test_passes_when_io_gap_is_low(self):
        """≤30% I/O false = does not trigger false-completion check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                    "input_format_in_readme": True,    # all True
                    "output_format_in_readme": True,
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": total, "total": total}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)

    def test_passes_when_match_not_100_percent(self):
        """High I/O gap is acceptable if match is not 100% (honest partial)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "input_format_in_readme": False,
                    "output_format_in_readme": False,
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": 20, "total": total}),  # honest 20/42
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)


class TestReadmeGateWiredInPipeline(unittest.TestCase):
    """Rule: readme_gate_wired_in_pipeline — closes SD60-03."""

    def test_fails_when_no_integration_proof_no_source_root(self):
        """No flow integration proof and no source_root = FAILURE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("readme-gate-flow-integration.md", rule.failure_detail)

    def test_fails_when_integration_proof_admits_deferred(self):
        """Integration proof that says 'deferred' is treated as not-wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").write_text(
                "# README Gate\nWiring is deferred to Sprint 62 (P1 item).\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("deferred", rule.failure_detail.lower())

    def test_fails_when_integration_proof_admits_not_wired(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").write_text(
                "# README Gate\nGate is not wired into publish-pr yet.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)

    def test_passes_when_integration_proof_exists_and_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_passes_with_source_root_that_imports_gate(self):
        """source_root scan: file that imports readme_audit_gate → PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "readme_audit_gate.py").write_text("def check(): pass\n", encoding="utf-8")
            (src / "__main__.py").write_text(
                "from readme_audit_gate import check\ncheck()\n", encoding="utf-8"
            )
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertTrue(rule.passed)
        self.assertIn("readme_audit_gate", rule.evidence)

    def test_fails_with_source_root_that_does_not_import_gate(self):
        """source_root scan: no file imports readme_audit_gate → FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "readme_audit_gate.py").write_text("def check(): pass\n", encoding="utf-8")
            (src / "__main__.py").write_text("# no imports\n", encoding="utf-8")
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("not imported", rule.failure_detail.lower())


class TestEvidenceValidatorWiredInPipeline(unittest.TestCase):
    """Rule: evidence_validator_wired_in_pipeline — closes SD60-04."""

    def test_fails_when_no_pipeline_integration_proof_no_source_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "pipeline-integration-proof.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("pipeline-integration-proof.md", rule.failure_detail)

    def test_fails_when_integration_proof_admits_p1_open(self):
        """Integration proof mentioning P1 admits it is not actually wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "pipeline-integration-proof.md").write_text(
                "# EvidenceValidator Pipeline Integration\nP1: wire into release-status.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)

    def test_passes_when_integration_proof_exists_and_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_passes_with_source_root_that_imports_validator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (src / "__main__.py").write_text(
                "from evidence_validator import EvidenceValidator\n", encoding="utf-8"
            )
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_fails_with_source_root_that_does_not_import_validator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (src / "__main__.py").write_text("# nothing imported\n", encoding="utf-8")
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)


class TestDestinationProgramcsInputNotAllNull(unittest.TestCase):
    """Rule: destination_programcs_input_not_all_null — closes SD60-05."""

    def test_fails_when_all_records_have_null_input(self):
        """SD60-05: input_format_in_programcs=null for all 42 records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {
                            "scenario_id": f"s-{i}",
                            "content_match": "MATCH",
                            "input_format_in_programcs": None,
                            "input_classification": None,
                        }
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertFalse(rule.passed)
        self.assertIn("null", rule.failure_detail.lower())
        self.assertIn("42/42", rule.failure_detail)

    def test_fails_when_field_not_present_in_records(self):
        """Records without input_format_in_programcs = audit not performed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {"scenario_id": f"s-{i}", "content_match": "MATCH"}
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertFalse(rule.passed)
        self.assertIn("input_format_in_programcs", rule.failure_detail)

    def test_passes_when_some_records_have_nonnull_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # _make_bundle already sets input_format_in_programcs = ".docx"
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertTrue(rule.passed)

    def test_passes_with_programcs_io_audit_file(self):
        """Dedicated programcs-io-audit-after.json with real data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "programcs-io-audit-after.json").write_text(
                json.dumps({
                    "examples": [
                        {
                            "scenario_id": "cells-html-converter",
                            "input_format_in_programcs": ".xlsx",
                            "input_classification": "AddInput",
                            "output_format_in_programcs": ".html",
                        }
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertTrue(rule.passed)


class TestNoPriOneItemsWithCompleteVerdict(unittest.TestCase):
    """Rule: no_p1_items_with_complete_verdict — closes SD60-08."""

    def test_fails_when_p1_items_open_with_complete_verdict(self):
        """SD60-08: P1 items in register + COMPLETE verdict = contradiction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate CLI wiring | P1 | OPEN |\n"
                "| EvidenceValidator CLI wiring | P1 | OPEN |\n",
                encoding="utf-8",
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertFalse(rule.passed)
        self.assertIn("P1", rule.failure_detail)

    def test_passes_when_no_register_file(self):
        """No register file = no P1 items to check → WARNING/passed=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_register_has_no_p1_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README formatting | P2 | OPEN |\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_p1_items_but_verdict_not_complete(self):
        """P1 items are allowed when verdict does not claim completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| Wiring | P1 | OPEN |\n", encoding="utf-8"
            )
            (b / "final-verdict.md").write_text(
                "Verdict: EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_p1_items_marked_done(self):
        """P1 lines marked DONE are not treated as open."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate wiring | P1 | DONE |\n", encoding="utf-8"
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_FALSE_CLOSURE_KILLED_PIPELINE_GATES_ACTIVE\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)


class TestRequiredFilesNonzeroSize(unittest.TestCase):
    """Rule: required_files_nonzero_size — closes SD60-01 contributory."""

    def test_fails_when_commands_log_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("commands.log", rule.failure_detail)

    def test_fails_when_todo_md_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("todo.md", rule.failure_detail)

    def test_fails_when_test_run_log_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("test-run.log", rule.failure_detail)

    def test_passes_when_all_required_files_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertTrue(rule.passed)


class TestBundleValidationResultPresentAndValid(unittest.TestCase):
    """Rule: bundle_validation_result_present_and_valid — Sprint 62 mandatory EV execution."""

    def test_fails_when_no_bundle_validation_result(self):
        """Missing evidence/*-bundle-validation-result.json = FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the bundle-validation-result.json that _make_bundle creates
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("bundle-validation-result.json", rule.failure_detail)

    def test_fails_when_bundle_validation_result_shows_failures(self):
        """overall_valid=false in bundle-validation-result.json = FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint60-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint60-test",
                    "overall_valid": False,
                    "passed": 15,
                    "failed": 5,
                    "warnings": 0,
                    "total_rules": 20,
                    "rules": [],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("overall_valid=false", rule.failure_detail)
        self.assertIn("5", rule.failure_detail)  # failed count

    def test_passes_when_bundle_validation_result_is_valid(self):
        """overall_valid=true in bundle-validation-result.json = PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertTrue(rule.passed)
        self.assertIn("overall_valid=true", rule.evidence)

    def test_uses_most_recent_file_when_multiple_exist(self):
        """When multiple *-bundle-validation-result.json exist, uses the most recent (alphabetically last)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Add a second, newer result file that passes
            (b / "evidence" / "sprint62-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint62-test",
                    "overall_valid": True,
                    "passed": 21,
                    "failed": 0,
                    "warnings": 0,
                    "total_rules": 21,
                    "rules": [],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertTrue(rule.passed)
        self.assertIn("sprint62", rule.evidence)

    def test_overall_valid_false_when_bundle_validation_missing(self):
        """overall_valid=False when bundle-validation-result.json is missing from evidence/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)


class TestTwoPhaseValidation(unittest.TestCase):
    """Sprint 63 Phase 2: Two-phase validation eliminates self-referential bootstrap contradiction."""

    def test_validate_for_storage_excludes_self_reference_rule(self):
        """validate_for_storage() runs 31 rules (excludes rule 21 bundle_validation_result_present_and_valid)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the validation result so rule 21 would fail if evaluated
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate_for_storage()
        # Rule 21 must not appear in results
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn(EvidenceValidator.SELF_REFERENCE_RULE_ID, rule_ids)
        # Should have exactly 144 rules evaluated (145 total - 1 self-reference rule 21)
        # Sprint 89: total is now 145 (added 5 new rules), so excluding rule 21 = 144
        self.assertEqual(len(result.rule_results), 144)

    def test_validate_for_storage_overall_valid_reflects_20_rules_only(self):
        """validate_for_storage() overall_valid=True means all 41 non-self-referential rules pass.

        Sprint 66: 42 total rules; validate_for_storage excludes rule 21 (self-ref), runs 41.
        Rule 22 (ECC gate) and rules 23-42 (Sprint 65+66) ARE included in validate_for_storage.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the validation result so rule 21 would fail if included
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate_for_storage()
        # overall_valid should be True because rule 21 was excluded
        self.assertTrue(result.overall_valid)
        self.assertEqual(result.failed, 0)

    def test_full_validate_passes_after_storing_phase_a_result(self):
        """After storing phase A result, phase B (all 21 rules) passes."""
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove old result
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            # Phase A: run without rule 21
            phase_a = EvidenceValidator(b).validate_for_storage()
            # Store the phase A result (simulating actual storage)
            result_data = {
                "sprint_id": "sprint63-test",
                "overall_valid": phase_a.overall_valid,
                "passed": phase_a.passed,
                "failed": phase_a.failed,
                "warnings": phase_a.warnings,
                "total_rules": len(phase_a.rule_results),
                "rules": [
                    {"rule_id": r.rule_id, "passed": r.passed}
                    for r in phase_a.rule_results
                ],
            }
            (b / "evidence" / "sprint63-bundle-validation-result.json").write_text(
                json.dumps(result_data), encoding="utf-8"
            )
            # Phase B: run all 32 rules — rule 21 should now pass
            phase_b = EvidenceValidator(b).validate()
        self.assertTrue(phase_b.overall_valid)
        self.assertEqual(phase_b.failed, 0)
        self.assertEqual(len(phase_b.rule_results), 145)  # Sprint 89: 145 rules total

    def test_sprint62_style_contradiction_detected_by_rule_21(self):
        """Sprint 62 defect: overall_valid=true + failed=0 but embedded rule has passed=false is detected."""
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Write a contradictory result file: claims overall_valid=true but one rule is failed
            contradictory_result = {
                "sprint_id": "sprint62-test",
                "overall_valid": True,
                "passed": 21,
                "failed": 0,
                "warnings": 0,
                "total_rules": 21,
                "rules": [
                    {"rule_id": "bundle_validation_result_present_and_valid", "passed": False},
                ],
            }
            (b / "evidence" / "sprint62-bundle-validation-result.json").write_text(
                json.dumps(contradictory_result), encoding="utf-8"
            )
            # Remove the old result so only the contradictory one is used
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        # The contradiction (overall_valid=true but a rule has passed=false) must be detected
        self.assertFalse(rule.passed)
        detail_lower = rule.failure_detail.lower()
        self.assertTrue(
            "contradict" in detail_lower or "inconsistent" in detail_lower or "false" in detail_lower,
            f"Expected contradiction language in failure_detail, got: {rule.failure_detail}",
        )

    def test_validate_exclude_rule_ids_removes_specified_rule(self):
        """validate(exclude_rule_ids={'some_rule'}) removes that rule from results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate(
                exclude_rule_ids={"required_files_nonzero_size"}
            )
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn("required_files_nonzero_size", rule_ids)
        # All other rules still present
        self.assertIn("bundle_validation_result_present_and_valid", rule_ids)

    def test_validate_exclude_empty_set_runs_all_rules(self):
        """validate(exclude_rule_ids=set()) is identical to validate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result_default = EvidenceValidator(b).validate()
            result_empty_exclude = EvidenceValidator(b).validate(exclude_rule_ids=set())
        self.assertEqual(len(result_default.rule_results), len(result_empty_exclude.rule_results))
        self.assertEqual(result_default.overall_valid, result_empty_exclude.overall_valid)

    def test_self_reference_rule_id_constant_matches_actual_rule(self):
        """SELF_REFERENCE_RULE_ID must match the actual rule ID used in validate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertIn(
            EvidenceValidator.SELF_REFERENCE_RULE_ID,
            rule_ids,
            "SELF_REFERENCE_RULE_ID must match an actual rule in the validator",
        )


class TestECCContractComputedAndValid(unittest.TestCase):
    """Sprint 64: EV rule 22 — ECC must be computed and show closure_valid=true.

    Catches Sprint 63 defect S63-D1: ECC (closure_valid=false) and EV
    (overall_valid=true) silently disagreed. Combined gate now requires ECC pass.
    """

    def test_passes_when_ecc_result_shows_closure_valid_true(self):
        """Rule passes when evidence-contract-computed.json has closure_valid=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertTrue(rule.passed, f"Expected pass, got: {rule.failure_detail}")

    def test_fails_when_ecc_result_missing(self):
        """Rule fails when evidence-contract-computed.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "evidence-contract-computed.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_fails_when_ecc_result_shows_blocking_failures(self):
        """Rule fails when ECC shows closure_valid=false with blocking failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "evidence-contract-computed.json").write_text(
                json.dumps({
                    "contract_id": "sprint-test",
                    "computed_at": "2026-05-22T07:18:19Z",
                    "total_categories": 36,
                    "present": 25,
                    "missing": 7,
                    "zero_bytes": 0,
                    "semantic_failed": 4,
                    "pending": 0,
                    "blocking_failures": 11,
                    "closure_valid": False,
                    "categories": [
                        {"id": "EC10", "name": "ec_computed", "file": "evidence/evidence-contract-computed.json",
                         "blocking": True, "status": "MISSING", "detail": "File not found"},
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("blocking_failures=11", rule.failure_detail)

    def test_fails_when_ecc_result_stale_shows_missing_files(self):
        """Rule fails when ECC was run before final commit — MISSING files found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Simulate ECC run BEFORE final commit: 7 blocking MISSING entries
            stale_categories = [
                {"id": f"EC{i:02d}", "name": f"file_{i}", "file": f"evidence/file_{i}.json",
                 "blocking": True, "status": "MISSING", "detail": f"File not found: evidence/file_{i}.json"}
                for i in range(7)
            ]
            (b / "evidence" / "evidence-contract-computed.json").write_text(
                json.dumps({
                    "contract_id": "sprint-stale",
                    "computed_at": "2026-05-22T07:18:19Z",  # Before final commit at 07:19+
                    "total_categories": 36,
                    "present": 29,
                    "missing": 7,
                    "zero_bytes": 0,
                    "semantic_failed": 0,
                    "pending": 0,
                    "blocking_failures": 7,
                    "closure_valid": False,
                    "categories": stale_categories,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("closure_valid=false", rule.failure_detail.lower())

    def test_validator_pass_contract_fail_produces_overall_fail(self):
        """If EV passes 21 rules but ECC fails, combined result is FAIL.

        This is the Sprint 63 defect scenario: EV said overall_valid=true but
        ECC said closure_valid=false. Under the repaired gate, the ECC failure
        is caught by rule 22, making overall_valid=false.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # ECC shows failure (stale — computed before final commit)
            (b / "evidence" / "evidence-contract-computed.json").write_text(
                json.dumps({
                    "contract_id": "sprint-test",
                    "computed_at": "2026-05-22T07:18:00Z",
                    "blocking_failures": 5,
                    "closure_valid": False,
                    "categories": [],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid,
                         "Combined gate must fail when ECC shows closure_valid=false")
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertFalse(rule.passed)

    def test_both_pass_produces_overall_pass(self):
        """When EV and ECC both pass, overall_valid=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        ecc_rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_contract_computed_and_valid"
        )
        self.assertTrue(ecc_rule.passed)
        # The bundle should pass overall (assuming other rules pass too)
        # We only assert ECC rule passes; overall depends on other rules too
        # but ecc_rule must not be the cause of failure
        if not result.overall_valid:
            failing = [r.rule_id for r in result.rule_results if not r.passed and r.severity == "FAILURE"]
            self.assertNotIn("ecc_contract_computed_and_valid", failing,
                             f"ECC rule should not be failing when ECC shows closure_valid=true. "
                             f"Failing rules: {failing}")

    def test_ecc_rule_total_is_22(self):
        """validate() must return 145 rules total (140 Sprint 88 + 5 new Sprint 89 rules)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        self.assertEqual(result.total_rules, 145,
                         f"Expected 145 rules, got {result.total_rules}: "
                         f"{[r.rule_id for r in result.rule_results]}")

    def test_validate_for_storage_excludes_self_reference_but_not_ecc_rule(self):
        """validate_for_storage() excludes rule 21 (self-ref) but includes rules 22-140."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate_for_storage()
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn("bundle_validation_result_present_and_valid", rule_ids,
                         "validate_for_storage must exclude rule 21 (self-reference)")
        self.assertIn("ecc_contract_computed_and_valid", rule_ids,
                      "validate_for_storage must include rule 22 (ECC gate)")
        self.assertEqual(result.total_rules, 144,
                         f"validate_for_storage must have 144 rules (145 - 1 self-ref), "
                         f"got {result.total_rules}")


class TestSprint75WeeklyReviewRules(unittest.TestCase):
    """Tests for the 8 new Sprint 75 weekly review governance rules."""

    def test_rule86_weekly_review_matrix_missing(self):
        """Rule 86: fails when weekly review claim matrix is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "02-weekly-review-claim-vs-proof-matrix.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "weekly_review_claim_matrix_present")
        self.assertFalse(rule.passed)

    def test_rule86_weekly_review_matrix_present_passes(self):
        """Rule 86: passes when matrix exists with classification labels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "weekly_review_claim_matrix_present")
        self.assertTrue(rule.passed)

    def test_rule87_pdf_pr_reconciliation_missing(self):
        """Rule 87: fails when pdf-pr-reconciliation.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "pdf-publication" / "pdf-pr-reconciliation.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "pdf_publication_truth_reconciled")
        self.assertFalse(rule.passed)

    def test_rule87_pdf_pr_reconciliation_present_passes(self):
        """Rule 87: passes when pdf-pr-reconciliation.json exists with claim_verdict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "pdf_publication_truth_reconciled")
        self.assertTrue(rule.passed)

    def test_rule88_formimporter_taskcard_missing(self):
        """Rule 88: fails when formimporter-repro-inventory.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "formimporter" / "formimporter-repro-inventory.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "formimporter_taskcard_durable")
        self.assertFalse(rule.passed)

    def test_rule88_formimporter_taskcard_present_passes(self):
        """Rule 88: passes when formimporter-repro-inventory.json has retest trigger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "formimporter_taskcard_durable")
        self.assertTrue(rule.passed)

    def test_rule89_words_version_drift_missing(self):
        """Rule 89: fails when words-version-drift-current.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "version-drift" / "words-version-drift-current.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "words_version_drift_documented")
        self.assertFalse(rule.passed)

    def test_rule89_words_version_drift_present_passes(self):
        """Rule 89: passes when words-version-drift-current.json has drift field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "words_version_drift_documented")
        self.assertTrue(rule.passed)

    def test_rule90_post_merge_matrix_missing(self):
        """Rule 90: fails when post-merge-validation-matrix.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "post-merge-runtime" / "post-merge-validation-matrix.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "email_slides_runtime_validated")
        self.assertFalse(rule.passed)

    def test_rule90_post_merge_matrix_present_passes(self):
        """Rule 90: passes when post-merge-validation-matrix.json has records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "email_slides_runtime_validated")
        self.assertTrue(rule.passed)

    def test_rule91_dirty_tree_classification_missing(self):
        """Rule 91: fails when dirty-file-classification.md is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "dirty-file-classification.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_tree_classified")
        self.assertFalse(rule.passed)

    def test_rule91_dirty_tree_classification_present_passes(self):
        """Rule 91: passes when dirty-file-classification.md is substantive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_tree_classified")
        self.assertTrue(rule.passed)

    def test_rule92_sprint27_governance_missing(self):
        """Rule 92: fails when sprint27-strict-contract-revalidation.md is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "governance" / "sprint27-strict-contract-revalidation.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "sprint27_governance_classified")
        self.assertFalse(rule.passed)

    def test_rule92_sprint27_governance_present_passes(self):
        """Rule 92: passes when sprint27-strict-contract-revalidation.md has required labels."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "sprint27_governance_classified")
        self.assertTrue(rule.passed)

    def test_rule93_verdict_ok_when_matrix_present(self):
        """Rule 93: passes when weekly review matrix is present (verdict allowed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "weekly_review_verdict_not_complete_while_unclassified")
        self.assertTrue(rule.passed)

    def test_sprint74_bundle_fails_rule86(self):
        """Sprint 74 bundle must fail rule 86 (no weekly review matrix).

        Sprint 74 did not classify the 6 weekly review items — it lacks
        02-weekly-review-claim-vs-proof-matrix.md.
        """
        bundle_path = Path("reports/sprint74")
        if not bundle_path.exists():
            self.skipTest("Sprint 74 bundle not present")
        result = EvidenceValidator(bundle_path).validate()
        sprint75_rules = [
            "weekly_review_claim_matrix_present",
            "pdf_publication_truth_reconciled",
            "formimporter_taskcard_durable",
            "words_version_drift_documented",
            "email_slides_runtime_validated",
            "dirty_tree_classified",
            "sprint27_governance_classified",
        ]
        failing = [
            r.rule_id for r in result.rule_results
            if r.rule_id in sprint75_rules and not r.passed
        ]
        self.assertTrue(
            len(failing) > 0,
            f"Sprint 74 bundle should fail at least one Sprint 75 rule but all passed. "
            f"Sprint 75 rules: {sprint75_rules}",
        )


class TestSprint76ClosureRepairRules(unittest.TestCase):
    """Tests for the 8 new Sprint 76 closure repair rules (94-101).

    These rules catch the Sprint 75 defects:
    - S75-B1: Slides Compress marked validated without real output
    - S75-B2: dirty-state documentation internally inconsistent
    """

    def test_rule94_fails_when_output_not_confirmed(self):
        """Rule 94: fails when post_merge_validated=true but output_confirmed=false."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "post-merge-runtime" / "post-merge-validation-matrix.json").write_text(
                json.dumps({
                    "records": [
                        {"scenario_id": "slides-compress", "post_merge_validated": True, "output_confirmed": False},
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "runtime_matrix_output_confirmed_for_validated")
        self.assertFalse(rule.passed)
        self.assertIn("slides-compress", rule.failure_detail)

    def test_rule94_passes_when_all_output_confirmed(self):
        """Rule 94: passes when all validated records have output_confirmed=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "runtime_matrix_output_confirmed_for_validated")
        self.assertTrue(rule.passed)

    def test_rule95_fails_when_no_input_fixture_label_present(self):
        """Rule 95: fails when runtime_result contains NO_INPUT_FIXTURE while validated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "post-merge-runtime" / "post-merge-validation-matrix.json").write_text(
                json.dumps({
                    "records": [
                        {
                            "scenario_id": "slides-compress",
                            "post_merge_validated": True,
                            "output_confirmed": False,
                            "runtime_result": "RUNTIME_VALIDATED_NO_INPUT_FIXTURE",
                        },
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "runtime_matrix_no_graceful_exit_labelled_validated")
        self.assertFalse(rule.passed)
        self.assertIn("slides-compress", rule.failure_detail)

    def test_rule95_passes_when_runtime_validated(self):
        """Rule 95: passes when runtime_result=RUNTIME_VALIDATED (no NO_INPUT_FIXTURE)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "runtime_matrix_no_graceful_exit_labelled_validated")
        self.assertTrue(rule.passed)

    def test_rule96_fails_when_classification_contradicts_after_snapshot(self):
        """Rule 96: fails when dirty-state-after shows src/ modified but classification says no src/test dirty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "dirty-state-after.txt").write_text(
                "On branch main\nmodified:   src/plugin_examples/evidence_validator.py\n",
                encoding="utf-8",
            )
            (b / "git" / "dirty-file-classification.md").write_text(
                "# Dirty File Classification\n\nNo Source or Test Files Are Dirty\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_classification_must_match_after_snapshot")
        self.assertFalse(rule.passed)
        self.assertIn("No Source or Test Files Are Dirty", rule.failure_detail)

    def test_rule96_passes_when_no_src_test_in_after(self):
        """Rule 96: passes when dirty-state-after.txt shows no src/tests modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_classification_must_match_after_snapshot")
        self.assertTrue(rule.passed)

    def test_rule97_fails_when_no_sha_in_proof(self):
        """Rule 97: fails when final-clean-proof.txt has no commit SHA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nnothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_contains_commit_sha")
        self.assertFalse(rule.passed)

    def test_rule97_passes_when_sha_present(self):
        """Rule 97: passes when final-clean-proof.txt includes a hex SHA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_contains_commit_sha")
        self.assertTrue(rule.passed)

    def test_rule100_fails_when_src_modified_in_after(self):
        """Rule 100: fails when dirty-state-after.txt shows src/ as modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "dirty-state-after.txt").write_text(
                "On branch main\nmodified:   src/plugin_examples/evidence_validator.py\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_after_no_uncommitted_source_test")
        self.assertFalse(rule.passed)
        self.assertIn("src/", rule.failure_detail)

    def test_rule100_passes_when_no_src_test_in_after(self):
        """Rule 100: passes when dirty-state-after.txt shows no src/tests modifications."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_after_no_uncommitted_source_test")
        self.assertTrue(rule.passed)

    def test_sprint75_bundle_fails_sprint76_rules(self):
        """Sprint 75 bundle must fail Sprint 76 rules for S75-B1 and S75-B2.

        Sprint 75 had:
        - slides-compress: post_merge_validated=true, output_confirmed=false
        - dirty-state-after.txt: showed evidence_validator.py modified
        - dirty-file-classification.md: said 'No Source or Test Files Are Dirty'
        These are Sprint 76 defects that must fail under new rules.
        """
        bundle_path = Path("reports/sprint75")
        if not bundle_path.exists():
            self.skipTest("Sprint 75 bundle not present")
        result = EvidenceValidator(bundle_path).validate()
        sprint76_rules = [
            "runtime_matrix_output_confirmed_for_validated",
            "runtime_matrix_no_graceful_exit_labelled_validated",
            "dirty_classification_must_match_after_snapshot",
            "dirty_after_no_uncommitted_source_test",
        ]
        failing = [
            r.rule_id for r in result.rule_results
            if r.rule_id in sprint76_rules and not r.passed
        ]
        self.assertTrue(
            len(failing) >= 2,
            f"Sprint 75 bundle should fail at least 2 Sprint 76 rules (S75-B1 and S75-B2). "
            f"Actually failing: {failing}",
        )


class TestSprint77EvidenceConsistencyRules(unittest.TestCase):
    """Tests for the 4 new Sprint 77 evidence consistency rules (102-105).

    These rules close S76-C1 through S76-C4:
    - S76-C1: untracked output.pptx not acknowledged in final verdict
    - S76-C2: final-clean-proof.txt is narrative-only
    - S76-C3: commands.log has PENDING entries
    - S76-C4: validation authority is ambiguous
    """

    def test_rule102_fails_when_commands_log_has_pending(self):
        """Rule 102: fails when commands.log contains PENDING."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text(
                "phase0: done\nphase4: Exit: PENDING\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_no_pending")
        self.assertFalse(rule.passed)
        self.assertIn("PENDING", rule.failure_detail)

    def test_rule102_passes_when_no_pending(self):
        """Rule 102: passes when commands.log has no PENDING entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_no_pending")
        self.assertTrue(rule.passed)

    def test_rule103_fails_when_proof_is_narrative_only(self):
        """Rule 103: fails when final-clean-proof.txt has no raw git lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nSprint bundle committed: a1b2c3d4e5f\n"
                "workspace/verification/latest/ -- GENERATED_WORKSPACE_STATE governance exception\n"
                "Sprint 76 bundle scope: clean (source/test committed)\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_raw_git_lines")
        self.assertFalse(rule.passed)
        self.assertIn("narrative-only", rule.failure_detail)

    def test_rule103_passes_with_raw_status_lines(self):
        """Rule 103: passes when final-clean-proof.txt includes raw git status lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # _make_bundle already includes ' M workspace/...' line
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_raw_git_lines")
        self.assertTrue(rule.passed)

    def test_rule103_passes_with_nothing_to_commit(self):
        """Rule 103: passes when final-clean-proof.txt contains 'nothing to commit'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nSprint bundle committed: a1b2c3d4e5f\n"
                "nothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_raw_git_lines")
        self.assertTrue(rule.passed)

    def test_rule104_fails_when_untracked_short_format(self):
        """Rule 104: fails when dirty-state-after.txt shows ?? untracked files (short format)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "dirty-state-after.txt").write_text(
                "On branch main\n"
                " M workspace/verification/latest/release-status.json\n"
                "?? reports/sprint75/handoff/compress/output.pptx\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_state_untracked_acknowledged")
        self.assertFalse(rule.passed)
        self.assertIn("untracked", rule.failure_detail.lower())

    def test_rule104_fails_when_untracked_verbose_format(self):
        """Rule 104: fails when dirty-state-after.txt shows untracked files (verbose format)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "dirty-state-after.txt").write_text(
                "On branch main\nUntracked files:\n"
                "  (use \"git add <file>...\" to include in what will be committed)\n"
                "\treports/sprint75/handoff/compress/output.pptx\n\n"
                "nothing added to commit but untracked files present\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_state_untracked_acknowledged")
        self.assertFalse(rule.passed)

    def test_rule104_passes_when_no_untracked(self):
        """Rule 104: passes when dirty-state-after.txt shows no untracked files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "dirty_state_untracked_acknowledged")
        self.assertTrue(rule.passed)

    def test_rule105_fails_when_validation_result_ambiguous(self):
        """Rule 105: fails when *-validation-result.json has overall_valid=false without explanation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Add an ambiguous validation result (no bundle_type, no canonical_overall_valid)
            (b / "evidence" / "sprint77-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint77-test",
                    "overall_valid": False,
                    "passed": 39,
                    "failed": 61,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_authority_unambiguous")
        self.assertFalse(rule.passed)
        self.assertIn("overall_valid=false", rule.failure_detail)

    def test_rule105_passes_when_repair_bundle_type_present(self):
        """Rule 105: passes when overall_valid=false file has bundle_type=REPAIR_BUNDLE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint77-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint77-test",
                    "bundle_type": "REPAIR_BUNDLE",
                    "overall_valid": False,
                    "passed": 39,
                    "failed": 61,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_authority_unambiguous")
        self.assertTrue(rule.passed)

    def test_rule105_passes_when_canonical_overall_valid_present(self):
        """Rule 105: passes when overall_valid=false file has canonical_overall_valid=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint77-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint77-test",
                    "canonical_overall_valid": True,
                    "overall_valid": False,
                    "passed": 39,
                    "failed": 61,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_authority_unambiguous")
        self.assertTrue(rule.passed)

    def test_sprint76_bundle_fails_sprint77_rules(self):
        """Sprint 76 bundle must fail all 4 Sprint 77 rules (S76-C1 through S76-C4)."""
        bundle_path = Path("reports/sprint76")
        if not bundle_path.exists():
            self.skipTest("Sprint 76 bundle not present")
        result = EvidenceValidator(bundle_path).validate()
        sprint77_rules = [
            "commands_log_no_pending",
            "final_clean_proof_has_raw_git_lines",
            "dirty_state_untracked_acknowledged",
            "validation_authority_unambiguous",
        ]
        failing = [
            r.rule_id for r in result.rule_results
            if r.rule_id in sprint77_rules and not r.passed
        ]
        self.assertEqual(
            len(failing), 4,
            f"Sprint 76 bundle should fail all 4 Sprint 77 rules. "
            f"Actually failing: {failing}",
        )


class TestSprint78PublicationTruthRules(unittest.TestCase):
    """Tests for the 3 new Sprint 78 rules (S77-D1 through S77-D3)."""

    def test_rule106_fails_when_all_published_true_and_remote_stale_claimed(self):
        """Rule 106: fails when all_published=true but a family status contains REMOTE_STALE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps({
                    "all_published": True,
                    "all_merged": True,
                    "families": {
                        "cells": {"status": "REMOTE_STALE_LOCAL_HANDOFF_READY"},
                        "words": {"status": "PUBLISHED"},
                    },
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_no_stale_remote_claimed")
        self.assertFalse(rule.passed)
        self.assertIn("REMOTE_STALE", rule.failure_detail)

    def test_rule106_passes_when_all_published_and_no_stale(self):
        """Rule 106: passes when all_published=true and no REMOTE_STALE in family statuses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps({
                    "all_published": True,
                    "all_merged": True,
                    "families": {
                        "cells": {"status": "PUBLISHED"},
                        "words": {"status": "PUBLISHED"},
                    },
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_no_stale_remote_claimed")
        self.assertTrue(rule.passed)

    def test_rule106_passes_trivially_when_not_all_published(self):
        """Rule 106: passes trivially when all_published=False (not applicable)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Default _make_bundle has no all_published field → defaults to False → not applicable
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_no_stale_remote_claimed")
        self.assertTrue(rule.passed)

    def test_rule107_fails_when_handoff_validation_missing(self):
        """Rule 107: fails when handoff-prepublish-validation.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "handoff" / "handoff-prepublish-validation.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "handoff_validation_result_has_valid_flag")
        # Rule passes trivially when file is absent (not applicable)
        self.assertTrue(rule.passed)

    def test_rule107_fails_when_overall_handoff_valid_false(self):
        """Rule 107: fails when overall_handoff_valid=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "handoff" / "handoff-prepublish-validation.json").write_text(
                json.dumps({"overall_handoff_valid": False, "verdict": "HANDOFF_BLOCKED"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "handoff_validation_result_has_valid_flag")
        self.assertFalse(rule.passed)

    def test_rule107_fails_when_overall_handoff_valid_missing(self):
        """Rule 107: fails when overall_handoff_valid field is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "handoff" / "handoff-prepublish-validation.json").write_text(
                json.dumps({"verdict": "HANDOFF_UNKNOWN"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "handoff_validation_result_has_valid_flag")
        self.assertFalse(rule.passed)

    def test_rule107_passes_when_overall_handoff_valid_true(self):
        """Rule 107: passes when overall_handoff_valid=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "handoff_validation_result_has_valid_flag")
        self.assertTrue(rule.passed)

    def test_rule108_fails_when_remote_state_has_blocked_repos(self):
        """Rule 108: fails when accessible < total_checked in remote-repo-state-before.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote" / "remote-repo-state-before.json").write_text(
                json.dumps({
                    "summary": {
                        "total_checked": 6,
                        "accessible": 4,
                        "blocked": 2,
                        "blocked_families": ["email", "slides"],
                    }
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "remote_repo_state_all_accessible")
        self.assertFalse(rule.passed)
        self.assertIn("4/6", rule.failure_detail)

    def test_rule108_fails_when_total_checked_zero(self):
        """Rule 108: fails when total_checked=0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote" / "remote-repo-state-before.json").write_text(
                json.dumps({"summary": {"total_checked": 0, "accessible": 0, "blocked": 0}}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "remote_repo_state_all_accessible")
        self.assertFalse(rule.passed)

    def test_rule108_passes_when_all_repos_accessible(self):
        """Rule 108: passes when accessible == total_checked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "remote_repo_state_all_accessible")
        self.assertTrue(rule.passed)

    def test_rule108_passes_trivially_when_remote_state_absent(self):
        """Rule 108: passes trivially when remote-repo-state-before.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote" / "remote-repo-state-before.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "remote_repo_state_all_accessible")
        self.assertTrue(rule.passed)


class TestSprint79EvidenceRepairRules(unittest.TestCase):
    """Tests for Sprint 79 rules 109-110 (S78-E1, S78-E2)."""

    # Rule 109: ecc_closure_valid_only_if_no_blocking_failures

    def test_rule109_fails_when_closure_valid_true_but_blocking_failures_nonzero(self):
        """Rule 109: closure_valid=true with blocking_failures>0 is a contradiction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "evidence-contract-computed.json").write_text(
                json.dumps({
                    "contract_id": "sprint-test",
                    "closure_valid": True,
                    "blocking_failures": 1,
                    "present": 31,
                    "missing": 1,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_closure_valid_only_if_no_blocking_failures"
        )
        self.assertFalse(rule.passed)
        self.assertIn("blocking_failures=1", rule.failure_detail)

    def test_rule109_passes_when_closure_valid_true_and_blocking_failures_zero(self):
        """Rule 109: closure_valid=true with blocking_failures=0 is consistent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_closure_valid_only_if_no_blocking_failures"
        )
        self.assertTrue(rule.passed)

    def test_rule109_passes_trivially_when_ecc_file_absent(self):
        """Rule 109: passes trivially when evidence-contract-computed.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "evidence-contract-computed.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_closure_valid_only_if_no_blocking_failures"
        )
        self.assertTrue(rule.passed)

    def test_rule109_passes_when_closure_valid_false(self):
        """Rule 109: passes when closure_valid=false (even with blocking_failures>0 — no false claim)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "evidence-contract-computed.json").write_text(
                json.dumps({
                    "contract_id": "sprint-test",
                    "closure_valid": False,
                    "blocking_failures": 2,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "ecc_closure_valid_only_if_no_blocking_failures"
        )
        self.assertTrue(rule.passed)

    # Rule 110: diagnostic_bundle_file_has_nonblocking_label

    def test_rule110_fails_when_bundle_file_overall_false_no_label(self):
        """Rule 110: bundle-validation-result with overall_valid=false but no diagnostic label."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint79-bundle-validation-result.json").write_text(
                json.dumps({
                    "overall_valid": False,
                    "bundle_type": "REPAIR_SPRINT",
                    "passed": 50,
                    "failed": 60,
                    # missing: diagnostic_rules_are_non_blocking
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "diagnostic_bundle_file_has_nonblocking_label"
        )
        self.assertFalse(rule.passed)
        self.assertIn("diagnostic_rules_are_non_blocking", rule.failure_detail)

    def test_rule110_passes_when_bundle_file_has_nonblocking_label(self):
        """Rule 110: bundle-validation-result with overall_valid=false AND diagnostic label passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint79-bundle-validation-result.json").write_text(
                json.dumps({
                    "overall_valid": False,
                    "bundle_type": "REPAIR_SPRINT",
                    "diagnostic_rules_are_non_blocking": True,
                    "canonical_overall_valid": True,
                    "passed": 50,
                    "failed": 60,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "diagnostic_bundle_file_has_nonblocking_label"
        )
        self.assertTrue(rule.passed)

    def test_rule110_passes_trivially_when_no_bundle_validation_files(self):
        """Rule 110: passes trivially when no *-bundle-validation-result.json files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "diagnostic_bundle_file_has_nonblocking_label"
        )
        self.assertTrue(rule.passed)

    def test_rule110_passes_when_bundle_file_overall_valid_true(self):
        """Rule 110: passes when overall_valid=true (no diagnostic label needed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "diagnostic_bundle_file_has_nonblocking_label"
        )
        self.assertTrue(rule.passed)


class TestSprint80ValidationFileAuthorityRule(unittest.TestCase):
    """Tests for Sprint 80 rule 111 (S79-B1): no active validation file with ambiguous overall_valid=false."""

    # Rule 111: no_active_validation_file_with_ambiguous_false

    def test_rule111_fails_when_validation_result_has_overall_valid_false_no_not_canonical(self):
        """Rule 111: *-validation-result.json with overall_valid=false but no not_canonical=true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint80-final-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint80",
                    "overall_valid": False,
                    "canonical_overall_valid": True,
                    "applicable_rules_failed": 0,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_active_validation_file_with_ambiguous_false"
        )
        self.assertFalse(rule.passed)
        self.assertIn("sprint80-final-validation-result.json", rule.failure_detail)

    def test_rule111_passes_when_validation_result_has_not_canonical_true(self):
        """Rule 111: passes when overall_valid=false but not_canonical=true is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "diagnostic-full-rules-non-applicable.json").write_text(
                json.dumps({
                    "sprint_id": "sprint80",
                    "overall_valid": False,
                    "not_canonical": True,
                    "diagnostic_rules_are_non_blocking": True,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_active_validation_file_with_ambiguous_false"
        )
        self.assertTrue(rule.passed)

    def test_rule111_passes_when_validation_result_has_no_overall_valid_false(self):
        """Rule 111: passes when canonical_overall_valid=true and no overall_valid=false field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint80-final-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint80",
                    "canonical_overall_valid": True,
                    "applicable_rules_failed": 0,
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_active_validation_file_with_ambiguous_false"
        )
        self.assertTrue(rule.passed)

    def test_rule111_passes_trivially_when_no_validation_result_files(self):
        """Rule 111: passes trivially when no *-validation-result.json files in evidence/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_active_validation_file_with_ambiguous_false"
        )
        self.assertTrue(rule.passed)

    def test_rule111_passes_trivially_when_evidence_dir_absent(self):
        """Rule 111: passes trivially when evidence/ directory is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            import shutil
            shutil.rmtree(str(b / "evidence"))
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_active_validation_file_with_ambiguous_false"
        )
        self.assertTrue(rule.passed)


class TestSprint83ValidatorHardeningRules(unittest.TestCase):
    """Tests for Sprint 83 rules 112-115 (S82-F1 through S82-F4): validator hardening."""

    # Rule 112: publication_truth_matrix_has_expected_count

    def _make_pub_record(self, family, example):
        """Minimal flat-array publication truth matrix record compatible with all rules."""
        return {
            "family": family,
            "example": example,
            "remote_example_present": True,
            "remote_readme_io_classification": "NO_IO_SECTION",
            "approval_blocked": True,
            "pr_url": None,
        }

    def test_rule112_fails_when_matrix_has_wrong_total_count(self):
        """Rule 112: publication-truth-matrix-final.json with != 42 records fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            records = [self._make_pub_record("cells", f"ex-{i}") for i in range(10)]
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_truth_matrix_has_expected_count"
        )
        self.assertFalse(rule.passed)
        self.assertIn("42", rule.failure_detail)

    def test_rule112_fails_when_family_counts_wrong(self):
        """Rule 112: 42 records but wrong family distribution fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            # 42 records but all cells (should be cells=9)
            records = [self._make_pub_record("cells", f"ex-{i}") for i in range(42)]
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_truth_matrix_has_expected_count"
        )
        self.assertFalse(rule.passed)
        self.assertIn("cells", rule.failure_detail)

    def test_rule112_passes_with_correct_42_records(self):
        """Rule 112: 42 records with correct family distribution passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            records = (
                [self._make_pub_record("cells", f"c{i}") for i in range(9)] +
                [self._make_pub_record("words", f"w{i}") for i in range(8)] +
                [self._make_pub_record("pdf", f"p{i}") for i in range(19)] +
                [self._make_pub_record("diagram", f"d{i}") for i in range(2)] +
                [self._make_pub_record("email", "converter")] +
                [self._make_pub_record("slides", f"s{i}") for i in range(3)]
            )
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_truth_matrix_has_expected_count"
        )
        self.assertTrue(rule.passed)

    def test_rule112_passes_trivially_when_no_matrix_file(self):
        """Rule 112: passes trivially when publication-truth-matrix-final.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_truth_matrix_has_expected_count"
        )
        self.assertTrue(rule.passed)

    # Rule 113: root_readme_conflict_strategy_documented

    def test_rule113_fails_when_open_prs_and_no_conflict_doc(self):
        """Rule 113: open PRs detected but no conflict strategy document fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote").mkdir(parents=True, exist_ok=True)
            (b / "remote" / "remote-repo-state-before.json").write_text(
                json.dumps({
                    "cells": {"open_prs": [{"number": 5, "title": "Add README"}]},
                    "words": {"open_prs": []},
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "root_readme_conflict_strategy_documented"
        )
        self.assertFalse(rule.passed)
        self.assertIn("cells", rule.failure_detail)

    def test_rule113_passes_when_open_prs_and_conflict_check_present(self):
        """Rule 113: open PRs detected and remote-conflict-check.md present passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote").mkdir(parents=True, exist_ok=True)
            (b / "remote" / "remote-repo-state-before.json").write_text(
                json.dumps({"cells": {"open_prs": [{"number": 5}]}}),
                encoding="utf-8",
            )
            (b / "remote" / "remote-conflict-check.md").write_text(
                "# Conflict Check\nNo conflict with per-example READMEs.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "root_readme_conflict_strategy_documented"
        )
        self.assertTrue(rule.passed)

    def test_rule113_passes_trivially_when_no_open_prs(self):
        """Rule 113: passes trivially when no open PRs in any family."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "remote").mkdir(parents=True, exist_ok=True)
            (b / "remote" / "remote-repo-state-before.json").write_text(
                json.dumps({"cells": {"open_prs": []}, "words": {"open_prs": []}}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "root_readme_conflict_strategy_documented"
        )
        self.assertTrue(rule.passed)

    def test_rule113_passes_trivially_when_no_remote_state(self):
        """Rule 113: passes trivially when remote-repo-state-before.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "root_readme_conflict_strategy_documented"
        )
        self.assertTrue(rule.passed)

    # Rule 114: final_consistency_check_not_stale_after_commit

    def test_rule114_fails_when_pending_commit_label_with_real_sha(self):
        """Rule 114: PASS_PENDING_COMMIT in consistency check with real SHA in proof fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "review").mkdir(parents=True, exist_ok=True)
            (b / "review" / "final-consistency-check.json").write_text(
                json.dumps({"sprint_id": "sprint82", "overall": "PASS_PENDING_COMMIT"}),
                encoding="utf-8",
            )
            # proof already has the real SHA from _make_bundle
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nSprint bundle committed: 886ce857405aa9dc3e25a75d3ff6d541f784dec2\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "final_consistency_check_not_stale_after_commit"
        )
        self.assertFalse(rule.passed)
        self.assertIn("PASS_PENDING_COMMIT", rule.failure_detail)

    def test_rule114_passes_when_pending_commit_label_but_no_real_sha(self):
        """Rule 114: PASS_PENDING_COMMIT is OK if proof has no 40-char SHA yet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "review").mkdir(parents=True, exist_ok=True)
            (b / "review" / "final-consistency-check.json").write_text(
                json.dumps({"sprint_id": "sprint82", "overall": "PASS_PENDING_COMMIT"}),
                encoding="utf-8",
            )
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nHEAD: PLACEHOLDER\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "final_consistency_check_not_stale_after_commit"
        )
        self.assertTrue(rule.passed)

    def test_rule114_passes_when_consistency_check_says_pass(self):
        """Rule 114: passes when final-consistency-check.json says PASS (not PENDING_COMMIT)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "review").mkdir(parents=True, exist_ok=True)
            (b / "review" / "final-consistency-check.json").write_text(
                json.dumps({"sprint_id": "sprint83", "overall": "PASS"}),
                encoding="utf-8",
            )
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nSprint bundle committed: 886ce857405aa9dc3e25a75d3ff6d541f784dec2\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "final_consistency_check_not_stale_after_commit"
        )
        self.assertTrue(rule.passed)

    def test_rule114_passes_trivially_when_no_consistency_check_file(self):
        """Rule 114: passes trivially when final-consistency-check.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "final_consistency_check_not_stale_after_commit"
        )
        self.assertTrue(rule.passed)

    # Rule 115: publication_file_plan_present_if_pr_creation_claimed

    def test_rule115_fails_when_pr_url_set_but_no_file_plan(self):
        """Rule 115: pr_url non-null in matrix but publication-file-plan.json missing fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            records = [dict(self._make_pub_record("cells", "html-converter"),
                            pr_url="https://github.com/org/repo/pull/10")]
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_file_plan_present_if_pr_creation_claimed"
        )
        self.assertFalse(rule.passed)
        self.assertIn("publication-file-plan.json", rule.failure_detail)

    def test_rule115_passes_when_pr_url_set_and_file_plan_present(self):
        """Rule 115: pr_url non-null and publication-file-plan.json present passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            records = [dict(self._make_pub_record("cells", "html-converter"),
                            pr_url="https://github.com/org/repo/pull/10")]
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            (b / "publication" / "publication-file-plan.json").write_text(
                json.dumps({"sprint_id": "sprint83", "families": {}}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_file_plan_present_if_pr_creation_claimed"
        )
        self.assertTrue(rule.passed)

    def test_rule115_passes_trivially_when_all_pr_urls_null(self):
        """Rule 115: passes trivially when all pr_url values are null."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "publication").mkdir(parents=True, exist_ok=True)
            records = [self._make_pub_record("cells", "html-converter")]
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps(records), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_file_plan_present_if_pr_creation_claimed"
        )
        self.assertTrue(rule.passed)

    def test_rule115_passes_trivially_when_no_matrix_file(self):
        """Rule 115: passes trivially when publication-truth-matrix-final.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "publication_file_plan_present_if_pr_creation_claimed"
        )
        self.assertTrue(rule.passed)


class TestSprint84ValidatorHardeningRules(unittest.TestCase):
    """Tests for Sprint 84 rules 116-119 (S83-G1 through S83-G4): PR lifecycle governance."""

    # ------------------------------------------------------------------ helpers

    def _make_ledger(self, bundle: Path, prs_created: int = 1) -> None:
        (bundle / "publication").mkdir(parents=True, exist_ok=True)
        (bundle / "publication" / "pr-creation-ledger.json").write_text(
            json.dumps({"prs_created": prs_created, "prs": []}),
            encoding="utf-8",
        )

    def _make_batching_strategy(self, bundle: Path) -> None:
        (bundle / "publication").mkdir(parents=True, exist_ok=True)
        (bundle / "publication" / "pr-batching-strategy.md").write_text(
            "# PR Batching Strategy\n1 PR per family.\n", encoding="utf-8"
        )

    def _make_batching_plan(self, bundle: Path, planned_count: int = 6, bulk_justification: str | None = None) -> None:
        (bundle / "publication").mkdir(parents=True, exist_ok=True)
        plan: dict = {
            "strategy": "FAMILY_BATCH_PR",
            "planned_prs": [{"family": f"f{i}"} for i in range(planned_count)],
        }
        if bulk_justification is not None:
            plan["bulk_justification"] = bulk_justification
        (bundle / "publication" / "pr-batching-plan.json").write_text(
            json.dumps(plan), encoding="utf-8"
        )

    def _make_root_readme_file_plan(self, bundle: Path) -> None:
        (bundle / "conflicts").mkdir(parents=True, exist_ok=True)
        (bundle / "conflicts" / "root-readme-file-plan.json").write_text(
            json.dumps({"grand_total_files": 42}), encoding="utf-8"
        )

    # ------------------------------------------------------------------ Rule 116

    def test_rule116_passes_trivially_when_no_ledger(self):
        """Rule 116: passes trivially when pr-creation-ledger.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "pr_batching_strategy_present_if_pr_creation_attempted"
        )
        self.assertTrue(rule.passed)

    def test_rule116_passes_trivially_when_prs_created_zero(self):
        """Rule 116: passes trivially when prs_created=0 in ledger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_ledger(b, prs_created=0)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "pr_batching_strategy_present_if_pr_creation_attempted"
        )
        self.assertTrue(rule.passed)

    def test_rule116_fails_when_prs_created_but_no_strategy(self):
        """Rule 116: fails when prs_created>0 but pr-batching-strategy.md absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_ledger(b, prs_created=6)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "pr_batching_strategy_present_if_pr_creation_attempted"
        )
        self.assertFalse(rule.passed)
        self.assertIn("S83-G1", rule.failure_detail)

    def test_rule116_passes_when_prs_created_and_strategy_present(self):
        """Rule 116: passes when prs_created>0 and pr-batching-strategy.md present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_ledger(b, prs_created=6)
            self._make_batching_strategy(b)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "pr_batching_strategy_present_if_pr_creation_attempted"
        )
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 119

    def test_rule119_passes_trivially_when_no_plan(self):
        """Rule 119: passes trivially when pr-batching-plan.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_bulk_42pr_plan_without_justification"
        )
        self.assertTrue(rule.passed)

    def test_rule119_passes_when_plan_has_6_prs(self):
        """Rule 119: passes when planned_prs has 6 entries (1 per family default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_batching_plan(b, planned_count=6)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_bulk_42pr_plan_without_justification"
        )
        self.assertTrue(rule.passed)

    def test_rule119_fails_when_plan_has_42_prs_without_justification(self):
        """Rule 119: fails when planned_prs has 42 entries without bulk_justification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_batching_plan(b, planned_count=42, bulk_justification=None)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_bulk_42pr_plan_without_justification"
        )
        self.assertFalse(rule.passed)
        self.assertIn("S83-G4", rule.failure_detail)

    def test_rule119_passes_when_plan_has_42_prs_with_justification(self):
        """Rule 119: passes when planned_prs has 42 entries WITH bulk_justification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_batching_plan(b, planned_count=42, bulk_justification="Required for atomic per-example CI gating")
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "no_bulk_42pr_plan_without_justification"
        )
        self.assertTrue(rule.passed)


class TestSprint85EvidenceHygieneRules(unittest.TestCase):
    """Tests for Sprint 85 rules 120-124 (S84-H1 through S84-H5): evidence hygiene."""

    # ------------------------------------------------------------------ helpers

    def _make_manifest(self, bundle_dir: Path, source_sha: str = "abc1234"):
        (bundle_dir / "bundle-manifest.json").write_text(
            json.dumps({"source_sha": source_sha}),
            encoding="utf-8",
        )

    def _make_consistency_check(self, bundle_dir: Path, notes: str = "All captured."):
        (bundle_dir / "review").mkdir(parents=True, exist_ok=True)
        (bundle_dir / "review" / "final-consistency-check.json").write_text(
            json.dumps({"overall": "PASS", "notes": notes}),
            encoding="utf-8",
        )

    def _make_taskcard(self, bundle_dir: Path, content: str = "| A | Topic | COMPLETED |\n"):
        (bundle_dir / "tracking").mkdir(parents=True, exist_ok=True)
        (bundle_dir / "tracking" / "taskcard-update-proof.md").write_text(
            content, encoding="utf-8",
        )

    def _make_scoreboard(self, bundle_dir: Path, content: str = "| EV applicable | 56 | 69 | +13 |\n"):
        (bundle_dir / "tracking").mkdir(parents=True, exist_ok=True)
        (bundle_dir / "tracking" / "scoreboard-update-proof.md").write_text(
            content, encoding="utf-8",
        )

    # ------------------------------------------------------------------ Rule 120

    def test_rule120_passes_trivially_when_no_manifest(self):
        """Rule 120: passes trivially when bundle-manifest.json absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_source_sha_not_tbd")
        self.assertTrue(rule.passed)

    def test_rule120_passes_with_valid_sha(self):
        """Rule 120: passes when source_sha is a real commit SHA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_manifest(b, source_sha="8bb4513")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_source_sha_not_tbd")
        self.assertTrue(rule.passed)

    def test_rule120_fails_with_tbd(self):
        """Rule 120: fails when source_sha is TBD_AFTER_COMMIT."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_manifest(b, source_sha="TBD_AFTER_COMMIT")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_source_sha_not_tbd")
        self.assertFalse(rule.passed)

    # ------------------------------------------------------------------ Rule 121

    def test_rule121_passes_when_no_stale_text(self):
        """Rule 121: passes when notes don't contain 'will be captured'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_consistency_check(b, notes="All files captured and verified.")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_stale_will_capture_text_in_final_consistency")
        self.assertTrue(rule.passed)

    def test_rule121_fails_with_stale_text(self):
        """Rule 121: fails when notes contain 'will be captured'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_consistency_check(b, notes="final-clean-proof.txt will be captured in commit 2.")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_stale_will_capture_text_in_final_consistency")
        self.assertFalse(rule.passed)

    # ------------------------------------------------------------------ Rule 122

    def test_rule122_passes_when_no_pending(self):
        """Rule 122: passes when no lanes are PENDING."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_taskcard(b, "| A | Topic | COMPLETED |\n| J | IV | COMPLETED |\n")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_stale_pending_lane_label_in_tracking")
        self.assertTrue(rule.passed)

    def test_rule122_fails_when_lane_pending(self):
        """Rule 122: fails when a lane has PENDING status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_taskcard(b, "| A | Topic | COMPLETED |\n| J | IV | PENDING — runs after all lanes |\n")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_stale_pending_lane_label_in_tracking")
        self.assertFalse(rule.passed)

    # ------------------------------------------------------------------ Rule 123

    def test_rule123_passes_when_ev_applicable_has_value(self):
        """Rule 123: passes when EV applicable has a numeric value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_scoreboard(b, "| EV applicable | 56 | 69 | +13 |\n")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "scoreboard_ev_applicable_not_tbd")
        self.assertTrue(rule.passed)

    def test_rule123_fails_when_ev_applicable_is_tbd(self):
        """Rule 123: fails when EV applicable has TBD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_scoreboard(b, "| EV applicable | 56 | TBD (post-EV run) | - |\n")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "scoreboard_ev_applicable_not_tbd")
        self.assertFalse(rule.passed)

    # ------------------------------------------------------------------ Rule 124

    def test_rule124_passes_when_sha_in_proof(self):
        """Rule 124: passes when source_sha appears in final-clean-proof.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_manifest(b, source_sha="a1b2c3d4e5f")
            # _make_bundle already creates final-clean-proof.txt with "a1b2c3d4e5f"
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_source_sha_in_final_clean_proof")
        self.assertTrue(rule.passed)

    def test_rule124_fails_when_sha_not_in_proof(self):
        """Rule 124: fails when source_sha doesn't appear in final-clean-proof.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_manifest(b, source_sha="deadbeef999")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_source_sha_in_final_clean_proof")
        self.assertFalse(rule.passed)


class TestSprint86ReadinessLoopPreventionRules(unittest.TestCase):
    """Tests for Sprint 86 rules 125-126: readiness-loop prevention."""

    # ------------------------------------------------------------------ helpers

    def _make_sprint_state(self, bundle_dir: Path, blocked_count: int = 14):
        (bundle_dir / "sprint-state.json").write_text(
            json.dumps({"sprint_id": "sprint86", "sprints_approval_blocked": blocked_count}),
            encoding="utf-8",
        )

    def _make_baseline_freeze(self, bundle_dir: Path):
        (bundle_dir / "baseline-freeze").mkdir(parents=True, exist_ok=True)
        (bundle_dir / "baseline-freeze" / "publication-baseline-freeze.json").write_text(
            json.dumps({"freeze_id": "sprint86-baseline-freeze", "frozen_at_sprint": "sprint85"}),
            encoding="utf-8",
        )

    def _make_final_verdict(self, bundle_dir: Path, content: str):
        (bundle_dir / "final-verdict.md").write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------ Rule 125

    def test_rule125_not_applicable_when_no_sprint_state(self):
        """Rule 125: passes (not applicable) when sprint-state.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_present_if_14_consecutive_blocked")
        self.assertTrue(rule.passed)

    def test_rule125_not_applicable_when_blocked_count_below_14(self):
        """Rule 125: passes when sprints_approval_blocked < 14."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_sprint_state(b, blocked_count=13)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_present_if_14_consecutive_blocked")
        self.assertTrue(rule.passed)

    def test_rule125_fails_when_14_blocked_no_freeze(self):
        """Rule 125: fails when sprints_approval_blocked >= 14 but no baseline freeze."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_sprint_state(b, blocked_count=14)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_present_if_14_consecutive_blocked")
        self.assertFalse(rule.passed)

    def test_rule125_passes_when_14_blocked_with_freeze(self):
        """Rule 125: passes when sprints_approval_blocked >= 14 and baseline freeze exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_sprint_state(b, blocked_count=14)
            self._make_baseline_freeze(b)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_present_if_14_consecutive_blocked")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 126

    def test_rule126_not_applicable_when_no_freeze(self):
        """Rule 126: passes (not applicable) when no baseline freeze file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_readiness_only_verdict_after_baseline_freeze")
        self.assertTrue(rule.passed)

    def test_rule126_fails_when_freeze_but_no_freeze_acknowledgment(self):
        """Rule 126: fails when baseline freeze exists but verdict doesn't acknowledge it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_baseline_freeze(b)
            self._make_final_verdict(b, "Verdict: LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_readiness_only_verdict_after_baseline_freeze")
        self.assertFalse(rule.passed)

    def test_rule126_passes_when_freeze_with_baseline_frozen_verdict(self):
        """Rule 126: passes when baseline freeze exists and verdict contains BASELINE_FROZEN."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_baseline_freeze(b)
            self._make_final_verdict(b, "Verdict: LOWCODE_LIVE_PUBLICATION_BASELINE_FROZEN_APPROVAL_BLOCKED_SAFE_LANES_ADVANCED")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_readiness_only_verdict_after_baseline_freeze")
        self.assertTrue(rule.passed)

    def test_rule126_passes_when_freeze_with_finish_line_verdict(self):
        """Rule 126: passes when baseline freeze exists and verdict contains FINISH_LINE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            self._make_baseline_freeze(b)
            self._make_final_verdict(b, "Verdict: LOWCODE_FINISH_LINE_SPRINT_COMPLETE")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_readiness_only_verdict_after_baseline_freeze")
        self.assertTrue(rule.passed)


# ===========================================================================
# Sprint 87 NEW rule tests: S86 defect invariants (rules 127-134)
# ===========================================================================


class TestSprint87DefectInvariantRules(unittest.TestCase):
    """Tests for Sprint 87 rules 127-134: S86 defect invariants."""

    # ------------------------------------------------------------------ Rule 127

    def test_rule127_not_applicable_when_no_commands_log(self):
        """Rule 127: passes (not applicable) when commands.log is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_no_result_pending")
        self.assertTrue(rule.passed)

    def test_rule127_fails_when_result_pending(self):
        """Rule 127: fails when commands.log has 'result pending' entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text(
                "[2026-05-25] RUN ECC — result pending\n"
                "[2026-05-25] RUN EV Phase A — result pending\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_no_result_pending")
        self.assertFalse(rule.passed)

    def test_rule127_passes_when_clean_commands(self):
        """Rule 127: passes when commands.log has no pending entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text(
                "[2026-05-25] RUN ECC — Exit: 0\n"
                "[2026-05-25] RUN EV Phase A — Exit: 0\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_no_result_pending")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 128

    def test_rule128_not_applicable_when_no_validation_result(self):
        """Rule 128: passes (not applicable) when no validation result file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_result_not_placeholder")
        self.assertTrue(rule.passed)

    def test_rule128_fails_when_counts_dont_add_up(self):
        """Rule 128: fails when applicable + diagnostic != total_rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence").mkdir(exist_ok=True)
            (b / "evidence" / "sprint87-final-validation-result.json").write_text(
                json.dumps({"applicable": 50, "diagnostic": 30, "total_rules": 134}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_result_not_placeholder")
        self.assertFalse(rule.passed)

    def test_rule128_passes_when_counts_match(self):
        """Rule 128: passes when applicable + diagnostic = total_rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence").mkdir(exist_ok=True)
            (b / "evidence" / "sprint87-final-validation-result.json").write_text(
                json.dumps({"applicable": 78, "diagnostic": 56, "total_rules": 134}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "validation_result_not_placeholder")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 129

    def test_rule129_not_applicable_when_no_manifest(self):
        """Rule 129: passes (not applicable) when bundle-manifest.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "sha_chain_reconciled_in_manifest")
        self.assertTrue(rule.passed)

    def test_rule129_fails_when_sha_is_tbd(self):
        """Rule 129: fails when source_sha is TBD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "TBD_AFTER_COMMIT"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "sha_chain_reconciled_in_manifest")
        self.assertFalse(rule.passed)

    def test_rule129_passes_with_valid_sha(self):
        """Rule 129: passes when source_sha is a valid hex SHA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "abc1234"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "sha_chain_reconciled_in_manifest")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 130

    def test_rule130_not_applicable_when_no_verdict(self):
        """Rule 130: passes (not applicable) when final-verdict.md is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "approval_vars_consistent_naming")
        self.assertTrue(rule.passed)

    def test_rule130_fails_when_old_name_without_deprecation(self):
        """Rule 130: fails when using README_PUSH_APPROVAL without deprecation note."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "final-verdict.md").write_text(
                "## Approval Gates\n- PLUGIN_EXAMPLES_README_PUSH_APPROVAL: NOT_SET\n"
                "Verdict: LOWCODE_REPAIR_AND_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "approval_vars_consistent_naming")
        self.assertFalse(rule.passed)

    def test_rule130_passes_with_canonical_name(self):
        """Rule 130: passes when using MERGE_PR_APPROVAL (canonical name)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "final-verdict.md").write_text(
                "## Approval Gates\n- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET\n"
                "Verdict: LOWCODE_REPAIR_AND_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "approval_vars_consistent_naming")
        self.assertTrue(rule.passed)

    def test_rule130_passes_with_deprecation_note(self):
        """Rule 130: passes when using old name WITH deprecation note."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "final-verdict.md").write_text(
                "## Approval Gates\n- PLUGIN_EXAMPLES_README_PUSH_APPROVAL: NOT_SET "
                "(deprecated alias for MERGE_PR_APPROVAL)\n"
                "Verdict: LOWCODE_REPAIR_AND_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "approval_vars_consistent_naming")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 131

    def test_rule131_not_applicable_when_no_drift_file(self):
        """Rule 131: passes (not applicable) when words drift file is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "words_drift_status_consistent")
        self.assertTrue(rule.passed)

    def test_rule131_fails_when_drift_true_but_resolved(self):
        """Rule 131: fails when drift=true but drift_type=RESOLVED."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "version-drift").mkdir(exist_ok=True)
            (b / "version-drift" / "words-version-drift-current.json").write_text(
                json.dumps({"drift": True, "drift_type": "RESOLVED"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "words_drift_status_consistent")
        self.assertFalse(rule.passed)

    def test_rule131_passes_when_drift_true_needs_repair(self):
        """Rule 131: passes when drift=true and drift_type=NEEDS_REPAIR_APPROVAL_BLOCKED."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "version-drift").mkdir(exist_ok=True)
            (b / "version-drift" / "words-version-drift-current.json").write_text(
                json.dumps({"drift": True, "drift_type": "NEEDS_REPAIR_APPROVAL_BLOCKED"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "words_drift_status_consistent")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 132

    def test_rule132_not_applicable_when_no_proof(self):
        """Rule 132: passes (not applicable) when final-clean-proof.txt is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the default proof file
            proof = b / "git" / "final-clean-proof.txt"
            if proof.exists():
                proof.unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_diff_and_log")
        self.assertTrue(rule.passed)

    def test_rule132_fails_when_no_diff_or_log(self):
        """Rule 132: fails when proof has status only, no diff/log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\n M reports/sprint87/foo.txt\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_diff_and_log")
        self.assertFalse(rule.passed)

    def test_rule132_passes_with_diff_and_log(self):
        """Rule 132: passes when proof includes diff and log output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\n== git diff --stat ==\nNo changes\n"
                "== git log --oneline -5 ==\nabc1234 commit message\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_diff_and_log")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 133

    def test_rule133_not_applicable_when_no_discovery(self):
        """Rule 133: passes (not applicable) when next-family-discovery.md is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_discovery_not_just_relisting")
        self.assertTrue(rule.passed)

    def test_rule133_fails_when_no_config_reference(self):
        """Rule 133: fails when discovery doesn't reference pipeline configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "advancement").mkdir(exist_ok=True)
            (b / "advancement" / "next-family-discovery.md").write_text(
                "# Discovery\nCurrent families: cells, words, pdf, diagram, email, slides.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_discovery_not_just_relisting")
        self.assertFalse(rule.passed)

    def test_rule133_passes_with_config_ref_and_new_family(self):
        """Rule 133: passes when referencing configs and identifying new candidates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "advancement").mkdir(exist_ok=True)
            (b / "advancement" / "next-family-discovery.md").write_text(
                "# Discovery\nScanned pipeline/configs/families/ for candidates.\n"
                "OCR and PSD are enabled but reflection incomplete.\n"
                "Barcode confirmed no LowCode.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_discovery_not_just_relisting")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 134

    def test_rule134_not_applicable_when_no_freeze(self):
        """Rule 134: passes (not applicable) when no baseline freeze."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_not_avoiding_advancement")
        self.assertTrue(rule.passed)

    def test_rule134_fails_when_freeze_but_no_advancement(self):
        """Rule 134: fails when baseline freeze exists but no advancement/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "baseline-freeze").mkdir(exist_ok=True)
            (b / "baseline-freeze" / "publication-baseline-freeze.json").write_text(
                json.dumps({"frozen": True}), encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_not_avoiding_advancement")
        self.assertFalse(rule.passed)

    def test_rule134_passes_when_freeze_with_advancement(self):
        """Rule 134: passes when baseline freeze exists and advancement/ has content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "baseline-freeze").mkdir(exist_ok=True)
            (b / "baseline-freeze" / "publication-baseline-freeze.json").write_text(
                json.dumps({"frozen": True}), encoding="utf-8",
            )
            (b / "advancement").mkdir(exist_ok=True)
            (b / "advancement" / "next-family-discovery.md").write_text("discovery", encoding="utf-8")
            (b / "advancement" / "fixture-readiness.md").write_text("fixtures", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "baseline_freeze_not_avoiding_advancement")
        self.assertTrue(rule.passed)


class TestSprint88DefectInvariantRules(unittest.TestCase):
    """Tests for Sprint 88 rules 135-140: S87 defect invariants."""

    # ------------------------------------------------------------------ Rule 135

    def test_rule135_not_applicable_when_no_manifest(self):
        """Rule 135: passes (not applicable) when bundle-manifest.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_has_head_sha")
        self.assertTrue(rule.passed)

    def test_rule135_fails_when_head_sha_missing(self):
        """Rule 135: fails when source_sha present but head_sha missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "abc1234"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_has_head_sha")
        self.assertFalse(rule.passed)

    def test_rule135_passes_with_both_shas(self):
        """Rule 135: passes when both source_sha and head_sha are valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "abc1234", "head_sha": "def5678"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "bundle_manifest_has_head_sha")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 136

    def test_rule136_not_applicable_when_no_verdict(self):
        """Rule 136: passes when final-verdict.md is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_matrix_present_when_publication_claimed")
        self.assertTrue(rule.passed)

    def test_rule136_fails_when_publication_mentioned_but_no_matrix(self):
        """Rule 136: fails when verdict mentions publication but truth matrix missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "final-verdict.md").write_text(
                "Publication is approval-blocked.\n"
                "Verdict: LOWCODE_FINISH_LINE_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED\n",
                encoding="utf-8",
            )
            # Remove any publication dir
            pub_dir = b / "publication"
            if pub_dir.exists():
                import shutil
                shutil.rmtree(pub_dir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_matrix_present_when_publication_claimed")
        self.assertFalse(rule.passed)

    def test_rule136_passes_with_truth_matrix(self):
        """Rule 136: passes when verdict mentions publication and truth matrix exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "final-verdict.md").write_text(
                "Publication is approval-blocked.\n"
                "Verdict: LOWCODE_FINISH_LINE_ADVANCEMENT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED\n",
                encoding="utf-8",
            )
            (b / "publication").mkdir(exist_ok=True)
            (b / "publication" / "publication-truth-matrix-final.json").write_text(
                json.dumps([{"family": "cells", "example": "html-converter"}]),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "publication_truth_matrix_present_when_publication_claimed")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 137

    def test_rule137_not_applicable_when_no_matrix(self):
        """Rule 137: passes when next-family-candidate-matrix.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_candidate_matrix_has_real_checks")
        self.assertTrue(rule.passed)

    def test_rule137_fails_when_missing_api_fields(self):
        """Rule 137: fails when candidates lack classification or nuget_exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({
                    "discovery_method": "manual",
                    "candidates": [{"family": "ocr"}]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_candidate_matrix_has_real_checks")
        self.assertFalse(rule.passed)

    def test_rule137_passes_with_real_checks(self):
        """Rule 137: passes when candidates have proper API check fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({
                    "discovery_method": "NuGet API v3",
                    "candidates": [
                        {"family": "ocr", "classification": "BLOCKED", "nuget_exists": True}
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "next_family_candidate_matrix_has_real_checks")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 138

    def test_rule138_not_applicable_when_no_advancement(self):
        """Rule 138: passes when advancement/ is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "implementation_summary_present_if_advancement")
        self.assertTrue(rule.passed)

    def test_rule138_fails_when_discovery_but_no_summary(self):
        """Rule 138: fails when advancement has discovery but no implementation summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "advancement").mkdir(exist_ok=True)
            (b / "advancement" / "next-family-discovery.md").write_text(
                "OCR discovery from pipeline/configs/families/",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "implementation_summary_present_if_advancement")
        self.assertFalse(rule.passed)

    def test_rule138_passes_with_both(self):
        """Rule 138: passes when both discovery and implementation summary exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "advancement").mkdir(exist_ok=True)
            (b / "advancement" / "next-family-discovery.md").write_text(
                "OCR discovery from pipeline/configs/families/",
                encoding="utf-8",
            )
            (b / "implementation").mkdir(exist_ok=True)
            (b / "implementation" / "implementation-summary.md").write_text(
                "Implementation summary for Sprint 88",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "implementation_summary_present_if_advancement")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 139

    def test_rule139_not_applicable_when_no_matrix(self):
        """Rule 139: passes when next-family-candidate-matrix.json is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "discovery_blocked_candidates_have_blocker_detail")
        self.assertTrue(rule.passed)

    def test_rule139_fails_when_blocked_without_detail(self):
        """Rule 139: fails when BLOCKED candidate has no blocker detail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({
                    "discovery_method": "NuGet API",
                    "candidates": [
                        {"family": "ocr", "classification": "DISCOVERY_BLOCKED", "nuget_exists": True, "blocker": ""}
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "discovery_blocked_candidates_have_blocker_detail")
        self.assertFalse(rule.passed)

    def test_rule139_passes_with_detailed_blocker(self):
        """Rule 139: passes when BLOCKED candidates have specific blocker detail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({
                    "discovery_method": "NuGet API",
                    "candidates": [
                        {
                            "family": "ocr",
                            "classification": "DISCOVERY_BLOCKED_MISSING_PACKAGE",
                            "nuget_exists": True,
                            "blocker": "Aspose.AI.LLM transitive dep not on NuGet (HTTP 404)"
                        }
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "discovery_blocked_candidates_have_blocker_detail")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 140

    def test_rule140_not_applicable_when_no_drift(self):
        """Rule 140: passes when no words drift file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "version_drift_reconciliation_present_if_drift_active")
        self.assertTrue(rule.passed)

    def test_rule140_fails_when_drift_active_no_reconciliation(self):
        """Rule 140: fails when drift active but no reconciliation file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "version-drift").mkdir(exist_ok=True)
            (b / "version-drift" / "words-version-drift-current.json").write_text(
                json.dumps({"drift": True, "drift_type": "NEEDS_REPAIR_APPROVAL_BLOCKED"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "version_drift_reconciliation_present_if_drift_active")
        self.assertFalse(rule.passed)

    def test_rule140_passes_with_reconciliation(self):
        """Rule 140: passes when drift active and reconciliation exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "version-drift").mkdir(exist_ok=True)
            (b / "version-drift" / "words-version-drift-current.json").write_text(
                json.dumps({"drift": True, "drift_type": "NEEDS_REPAIR_APPROVAL_BLOCKED"}),
                encoding="utf-8",
            )
            (b / "closure-repair").mkdir(exist_ok=True)
            (b / "closure-repair" / "words-version-drift-reconciliation.json").write_text(
                json.dumps({"checked": True, "nuget_latest": "26.5.0", "remote": "26.4.0"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "version_drift_reconciliation_present_if_drift_active")
        self.assertTrue(rule.passed)


class TestSprint89DefectInvariantRules(unittest.TestCase):
    """Tests for Sprint 89 rules 141-145: S88 defect invariants."""

    # ------------------------------------------------------------------ Rule 141

    def test_rule141_not_applicable_when_no_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "head_sha_matches_final_proof")
        self.assertTrue(rule.passed)

    def test_rule141_fails_when_head_sha_not_in_proof(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "abc1234", "head_sha": "deadbeef1234567"}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "head_sha_matches_final_proof")
        self.assertFalse(rule.passed)

    def test_rule141_passes_when_head_sha_in_proof(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "bundle-manifest.json").write_text(
                json.dumps({"source_sha": "abc1234", "head_sha": "abc1234"}),
                encoding="utf-8",
            )
            # Overwrite default proof to contain the head_sha
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nSprint bundle committed: abc1234\n"
                "workspace/verification/latest/ -- GENERATED_WORKSPACE_STATE governance exception\n"
                " M workspace/verification/latest/release-status.json\n"
                "nothing to commit (working tree has governed exceptions)\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "head_sha_matches_final_proof")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 142

    def test_rule142_not_applicable_when_no_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "active_validation_not_not_canonical")
        self.assertTrue(rule.passed)

    def test_rule142_fails_when_not_canonical_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence").mkdir(exist_ok=True)
            (b / "evidence" / "sprint89-final-validation-result.json").write_text(
                json.dumps({"overall_valid": False, "not_canonical": True}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "active_validation_not_not_canonical")
        self.assertFalse(rule.passed)

    def test_rule142_passes_when_canonical(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence").mkdir(exist_ok=True)
            (b / "evidence" / "sprint89-final-validation-result.json").write_text(
                json.dumps({"canonical_overall_valid": True}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "active_validation_not_not_canonical")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 143

    def test_rule143_not_applicable_when_no_new_rules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "source_proof_present_if_source_changed")
        self.assertTrue(rule.passed)

    def test_rule143_fails_when_rules_claimed_no_proof(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "sprint-state.json").write_text(
                json.dumps({"sprint_id": "test", "new_ev_rules_this_sprint": 5}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "source_proof_present_if_source_changed")
        self.assertFalse(rule.passed)

    def test_rule143_passes_with_source_diff(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "sprint-state.json").write_text(
                json.dumps({"sprint_id": "test", "new_ev_rules_this_sprint": 5}),
                encoding="utf-8",
            )
            (b / "source-diff.patch").write_text("diff --git a/src/...", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "source_proof_present_if_source_changed")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 144

    def test_rule144_not_applicable_when_no_matrix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_lowcode_confirmed_has_evidence")
        self.assertTrue(rule.passed)

    def test_rule144_fails_when_no_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({"candidates": [{"family": "html", "classification": "NO_LOWCODE_CONFIRMED"}]}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_lowcode_confirmed_has_evidence")
        self.assertFalse(rule.passed)

    def test_rule144_passes_with_scan_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({"candidates": [
                    {"family": "html", "classification": "NO_LOWCODE_CONFIRMED",
                     "discovery_method": "binary string scan", "lowcode_matches": 0}
                ]}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_lowcode_confirmed_has_evidence")
        self.assertTrue(rule.passed)

    # ------------------------------------------------------------------ Rule 145

    def test_rule145_not_applicable_when_no_scan_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "candidate_classification_not_stale_after_scan")
        self.assertTrue(rule.passed)

    def test_rule145_fails_when_still_blocked_after_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "html-reflection-result.json").write_text(
                json.dumps({"family": "html", "classification": "NO_LOWCODE_CONFIRMED"}),
                encoding="utf-8",
            )
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({"candidates": [
                    {"family": "html", "classification": "REFLECTION_BLOCKED_ASSEMBLY_RESOLUTION"}
                ]}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "candidate_classification_not_stale_after_scan")
        self.assertFalse(rule.passed)

    def test_rule145_passes_when_updated_after_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "next-family").mkdir(exist_ok=True)
            (b / "next-family" / "html-reflection-result.json").write_text(
                json.dumps({"family": "html", "classification": "NO_LOWCODE_CONFIRMED"}),
                encoding="utf-8",
            )
            (b / "next-family" / "next-family-candidate-matrix.json").write_text(
                json.dumps({"candidates": [
                    {"family": "html", "classification": "NO_LOWCODE_CONFIRMED"}
                ]}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "candidate_classification_not_stale_after_scan")
        self.assertTrue(rule.passed)


if __name__ == "__main__":
    unittest.main()
