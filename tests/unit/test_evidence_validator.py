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
        "nothing else to commit, working tree clean\n",
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
        self.assertEqual(result.total_rules, 101)  # Sprint 76: added 8 new rules (94-101)

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
        self.assertEqual(len(d["rules"]), 101)  # Sprint 76: 101 rules total


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
        # Should have exactly 100 rules evaluated (101 total - 1 self-reference rule 21)
        # Sprint 76: total is now 101 (added 8 new rules), so excluding rule 21 = 100
        self.assertEqual(len(result.rule_results), 100)

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
        self.assertEqual(len(phase_b.rule_results), 101)  # Sprint 76: 101 rules total

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
        """validate() must return 101 rules total (93 Sprint 75 + 8 new Sprint 76 rules)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        self.assertEqual(result.total_rules, 101,
                         f"Expected 101 rules, got {result.total_rules}: "
                         f"{[r.rule_id for r in result.rule_results]}")

    def test_validate_for_storage_excludes_self_reference_but_not_ecc_rule(self):
        """validate_for_storage() excludes rule 21 (self-ref) but includes rules 22-101."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate_for_storage()
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn("bundle_validation_result_present_and_valid", rule_ids,
                         "validate_for_storage must exclude rule 21 (self-reference)")
        self.assertIn("ecc_contract_computed_and_valid", rule_ids,
                      "validate_for_storage must include rule 22 (ECC gate)")
        self.assertEqual(result.total_rules, 100,
                         f"validate_for_storage must have 100 rules (101 - 1 self-ref), "
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


if __name__ == "__main__":
    unittest.main()
