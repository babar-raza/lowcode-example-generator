"""Pipeline integration tests for EvidenceValidator wiring — Sprint 61 Phase 3.

Verifies that:
1. EvidenceValidator is importable from __main__.py (source scan passes)
2. `release-status --validate-bundle` calls EvidenceValidator and returns 0 on valid bundle
3. `release-status --validate-bundle` returns 1 on invalid bundle
4. The evidence_validator_wired_in_pipeline rule passes when source_root points to real pipeline
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.evidence_validator import EvidenceValidator


def _make_valid_bundle(tmpdir: str) -> Path:
    """Create a minimal valid bundle (passes all 105 rules)."""
    b = Path(tmpdir)

    (b / "git").mkdir(parents=True)
    (b / "git" / "final-clean-proof.txt").write_text(
        "On branch main\nSprint bundle committed: a1b2c3d4e5f\n"
        "workspace/verification/latest/ -- pre-existing runtime files, GENERATED_WORKSPACE_STATE governance exception\n"
        " M workspace/verification/latest/release-status.json\n"
        "nothing to commit (working tree has governed exceptions)\n",
        encoding="utf-8",
    )

    (b / "destination").mkdir(parents=True)
    (b / "destination" / "content-audit-repaired.json").write_text(
        json.dumps({
            "authority_mapped": "42/42",
            "present_no_authority": 0,
            "total_examples": 42,
            "examples": [
                {
                    "scenario_id": f"s-{i}",
                    "content_match": "MATCH",
                    "input_format_in_programcs": ".docx",
                    "input_classification": "AddInput",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    (b / "readme").mkdir(parents=True)
    (b / "readme" / "example-readme-content-audit.json").write_text(
        json.dumps({"records": [{"scenario_id": "s-0", "family_in_readme": True, "workflow_type_in_readme": True, "package_id_in_readme": True}]}),
        encoding="utf-8",
    )
    (b / "readme" / "readme-gate-implementation.md").write_text("# Gate wired\n", encoding="utf-8")
    (b / "readme" / "readme-gate-test-results.txt").write_text("13 passed, 0 failed\n", encoding="utf-8")
    (b / "readme" / "readme-gate-source-proof.patch").write_text("diff --git a/src ...\n", encoding="utf-8")
    (b / "readme" / "readme-gate-flow-integration.md").write_text(
        "# README Gate Flow Integration\nGate is called in publish-pr live mode.\n", encoding="utf-8"
    )

    (b / "evidence").mkdir(parents=True)
    (b / "evidence" / "validator-test-results.txt").write_text("20 passed, 0 failed in 0.45s\n", encoding="utf-8")
    (b / "evidence" / "sprint61-bundle-validation-result.json").write_text(
        json.dumps({"sprint_id": "sprint61-test", "overall_valid": True, "passed": 21, "failed": 0, "warnings": 0, "total_rules": 21, "rules": []}),
        encoding="utf-8",
    )
    (b / "evidence" / "pipeline-integration-proof.md").write_text(
        "# Pipeline Integration\nEvidenceValidator is called in release-status command.\n", encoding="utf-8"
    )
    (b / "evidence" / "evidence-contract-computed.json").write_text(
        json.dumps({
            "contract_id": "sprint-test",
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

    (b / "todo.md").write_text("- [x] Phase 0 complete\n- [x] Phase 10 complete\n", encoding="utf-8")
    (b / "commands.log").write_text("phase0: done\nphase10: done\n", encoding="utf-8")

    (b / "lanes" / "lane-I").mkdir(parents=True)
    (b / "lanes" / "lane-I" / "test-run.log").write_text("2889 passed, 0 failed, 3 skipped\n", encoding="utf-8")

    (b / "sprint-state.json").write_text(json.dumps({"sprint_id": "sprint61-test"}), encoding="utf-8")

    # Sprint 65+66: destination/content-audit-final.json with all required fields
    # Sprint 66: includes output_kind and api_type (rules 37, ECC check)
    (b / "destination" / "content-audit-final.json").write_text(
        json.dumps({
            "total_publication_artifacts": 42,
            "standard_package_artifacts": 40,
            "special_case_artifacts": 2,
            "records_ready": 42,
            "records": [
                {
                    "scenario_id": f"s-{i}",
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

    # Sprint 65: root-readme/per-family artifacts
    (b / "root-readme" / "per-family").mkdir(parents=True)
    for family in ["cells", "diagram", "email", "pdf", "slides", "words"]:
        (b / "root-readme" / "per-family" / f"{family}-root-readme.md").write_text(
            f"# {family} README\n", encoding="utf-8"
        )

    # Sprint 65: special-cases/special-case-publication-map.json
    (b / "special-cases").mkdir(parents=True)
    (b / "special-cases" / "special-case-publication-map.json").write_text(
        json.dumps({"special_cases": [
            {"scenario_id": "pdf-pdfa-converter", "destination_path": "examples/pdf/lowcode/pdfa-converter"},
            {"scenario_id": "pdf-text-extractor", "destination_path": "examples/pdf/lowcode/text-extractor"},
        ]}),
        encoding="utf-8",
    )

    # Sprint 65: version/version-policy-final.json
    (b / "version").mkdir(parents=True)
    (b / "version" / "version-policy-final.json").write_text(
        json.dumps({"summary": {"total_drift_unresolved": 0}, "families": {}}),
        encoding="utf-8",
    )

    # Sprint 65: final-verdict.md + publication/remote-proof-index.json
    (b / "final-verdict.md").write_text("Verdict: TEST_DRY_RUN_APPROVAL_BLOCKED\n", encoding="utf-8")
    (b / "publication").mkdir(parents=True)
    (b / "publication" / "remote-proof-index.json").write_text(
        json.dumps({"families": ["cells"]}), encoding="utf-8"
    )

    # Sprint 65: evidence/*revalidation*.json — overall_valid=false
    (b / "evidence" / "sprint64-revalidation-result.json").write_text(
        json.dumps({"sprint_id": "sprint64-test", "overall_valid": False, "failed": 3}),
        encoding="utf-8",
    )

    # Sprint 66: remote/remote-pr-proof-index.json — per-example PR coverage (rule 33)
    (b / "remote").mkdir(parents=True)
    (b / "remote" / "remote-pr-proof-index.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "families": {
                "cells": [{"pr_number": 1, "examples_count": 9, "scenario_ids_covered": [f"cells-ex-{i}" for i in range(9)]}],
            },
        }),
        encoding="utf-8",
    )

    # Sprint 66: remote/remote-example-inventory.json — content hashes (rule 34)
    (b / "remote" / "remote-example-inventory.json").write_text(
        json.dumps({
            "generated": "2026-05-22T00:00:00Z",
            "total": 42,
            "records": [
                {
                    "scenario_id": f"s-{i}",
                    "family": "cells",
                    "readme_sha": f"abc{i:04x}",
                    "readme_content_sha256": f"sha256-{i:04x}",
                    "programcs_sha": f"def{i:04x}",
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
            "records": [
                {"scenario_id": f"s-{i}", "family": "cells", "has_io_section": False, "io_status": "OLD_FORMAT"}
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
            f"# {family}\n\n## Input and Output\n\nInput: file\nOutput: result\n",
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
                    "scenario_id": f"s-{i}",
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

    # Sprint 67: cardinality audit artifacts (rules 43-44)
    (b / "root-readme" / "cardinality-audit.json").write_text(
        json.dumps({"families": {"cells": {}, "words": {}, "pdf": {}, "diagram": {}, "email": {}, "slides": {}}}),
        encoding="utf-8",
    )

    # Sprint 67: version decision artifacts (rules 45-46)
    (b / "version" / "pdf-version-decision.md").write_text(
        "# PDF Version Decision\nDecision: 26.5.0 is canonical.\n", encoding="utf-8"
    )
    (b / "version" / "version-truth-matrix.json").write_text(
        json.dumps({"families": {"pdf": {"canonical": "26.5.0"}}}),
        encoding="utf-8",
    )

    # Sprint 67: legacy plan reconciliation (rule 48)
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
    (b / "remote" / "remote-proof-summary.md").write_text(
        "# Remote Proof Summary\nAll 42 examples confirmed.\n0/42 remote READMEs have I/O sections.\n", encoding="utf-8"
    )

    # Sprint 68: PDF root README with 19 rows (rule 53)
    pdf_rows_68 = "\n".join(
        f"| `example-{i}` | `Plugin.Process` | `pdf` | `pdf` | `dotnet run --project examples/pdf/lowcode/example-{i}` |"
        for i in range(19)
    )
    (b / "root-readme" / "per-family" / "pdf-root-readme.md").write_text(
        f"# Aspose.PDF LowCode Examples\n\n## Included Examples\n\n"
        f"| Example | Demonstrated API | Input | Output | Run |\n"
        f"|---------|-----------------|-------|--------|-----|\n"
        f"{pdf_rows_68}\n",
        encoding="utf-8",
    )

    # Sprint 68: splitter cardinality reconciliation (rule 54)
    (b / "legacy-reconciliation").mkdir(parents=True, exist_ok=True)
    (b / "legacy-reconciliation" / "splitter-resolution.md").write_text(
        "# Splitter Cardinality Resolution\nAll splitters: SINGLE_OUTPUT_VALID.\n",
        encoding="utf-8",
    )

    # Sprint 68: sprint-specific content audit with no stale PDF 26.4.0 (rule 55)
    # sprint_id="sprint61-test" → look for content-audit-sprint61-test.json
    (b / "destination" / "content-audit-sprint61-test.json").write_text(
        json.dumps({
            "sprint_id": "sprint61-test",
            "total": 42,
            "records": [
                {"scenario_id": f"s-{i}", "family": "cells", "package_version": "26.5.1"}
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 68: PDF version proof chain (rule 56)
    (b / "version" / "pdf-version-proof-chain.md").write_text(
        "# PDF Version Proof Chain\nHandoff Directory.Packages.props: Aspose.PDF 26.5.0.\n",
        encoding="utf-8",
    )

    # Sprint 68: words README with cardinality markers (rule 57)
    (b / "root-readme" / "per-family" / "words-root-readme.md").write_text(
        "# Aspose.Words LowCode Examples\n\n## Included Examples\n\n"
        "| `merger` | `Merger.Process` | `docx (×N)` | `docx` | `dotnet run ...` |\n"
        "| `splitter` | `Splitter.ExtractPages` | `docx` | `docx (×N)` | `dotnet run ...` |\n",
        encoding="utf-8",
    )

    # ---- Sprint 69: artifacts for rules 58-67 ----

    # Rule 58: handoff_index_version_matches_dpp
    # Also satisfies Sprint 70 rules 68-71: source_path inside sprint handoff,
    # README.md physically present, hash matches.
    # sprint_id="sprint61-test" => source_path must start with
    # reports/sprint61-test/handoff/per-family/{family}/
    import hashlib as _hashlib_fixture_gate
    _gate_fam_readme_hashes = {}
    for family, ver in [("cells", "26.5.1"), ("words", "26.5.0"), ("pdf", "26.5.0"),
                        ("diagram", "26.5.0"), ("email", "26.4.0"), ("slides", "26.5.0")]:
        fam_dir = b / "handoff" / "per-family" / family
        fam_dir.mkdir(parents=True, exist_ok=True)
        readme_content = f"# {family.capitalize()} Root README\n\nInput and Output examples.\n"
        readme_bytes = readme_content.encode("utf-8")
        (fam_dir / "README.md").write_bytes(readme_bytes)
        _gate_fam_readme_hashes[family] = _hashlib_fixture_gate.sha256(readme_bytes).hexdigest()
        (fam_dir / "handoff-index.json").write_text(
            json.dumps({"family": family, "nuget_version": ver, "examples": [],
                        "root_readme": {
                            "source_path": f"reports/sprint61-test/handoff/per-family/{family}/README.md",
                            "sha256": _gate_fam_readme_hashes[family],
                            "destination_path": "README.md",
                            "destination_repo": f"aspose-{family}-net/repo"}}),
            encoding="utf-8",
        )
        (fam_dir / "Directory.Packages.props").write_text(
            f'<Project><ItemGroup><PackageVersion Include="Aspose.Test" Version="{ver}" /></ItemGroup></Project>',
            encoding="utf-8",
        )

    # Rule 59: only_one_canonical_final_audit — content-audit-final.json with current sprint paths
    # Sprint 71 rules 73-74: handoff_path must use current sprint (sprint61-test) and paths must exist.
    dst_dir = b / "destination"
    dst_dir.mkdir(exist_ok=True)
    audit_example_dir = b / "handoff" / "per-family" / "cells" / "example"
    audit_example_dir.mkdir(parents=True, exist_ok=True)
    audit_records = [
        {
            "scenario_id": f"cells-html-converter-{i:02d}",
            "family": "cells",
            "handoff_path": "reports/sprint61-test/handoff/per-family/cells/example",
            "local_package_path": "reports/sprint61-test/handoff/per-family/cells/example",
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
        json.dumps({"sprint_id": "sprint61-test", "total": 42, "records": audit_records}),
        encoding="utf-8",
    )

    # Rule 60: publication_truth_matrix_no_stale_paths — current sprint paths only
    # Sprint 71 rules 74, 76: handoff_package_path must use current sprint and paths must exist.
    pub_dir = b / "publication"
    pub_dir.mkdir(exist_ok=True)
    pub_records = [
        {
            "scenario_id": f"cells-html-converter-{i:02d}",
            "family": "cells",
            "handoff_package_path": "reports/sprint61-test/handoff/per-family/cells/example",
            "remote_example_present": True,
            "remote_readme_has_io_docs": False,
            "remote_example_readme_has_io_docs": False,
            "readme_io_post_merge_verified": False,
            "approval_blocked": True,
        }
        for i in range(42)
    ]
    (pub_dir / "publication-truth-matrix-final.json").write_text(
        json.dumps({"sprint_id": "sprint61-test", "records": pub_records}),
        encoding="utf-8",
    )

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

    # Rule 64: final_verdict_is_precise
    (b / "final-verdict.md").write_text(
        "# Final Verdict\n\n`LOWCODE_PREPUBLICATION_HANDOFF_READY_APPROVAL_BLOCKED`\n",
        encoding="utf-8",
    )

    # Rule 66: handoff_index_has_root_readme_field
    # Rule 71: publication_handoff_root_readme_hash_matches — also needs root_readme_source_path
    handoff_dir = b / "handoff"
    (handoff_dir / "publication-handoff-index.json").write_text(
        json.dumps({"sprint_id": "sprint61-test", "families": [
            {
                "family": f,
                "root_readme_sha256": _gate_fam_readme_hashes[f],
                "root_readme_source_path": f"reports/sprint61-test/handoff/per-family/{f}/README.md",
                "example_count": 1,
            }
            for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
        ]}),
        encoding="utf-8",
    )

    # Rule 72: legacy_simplified_index_superseded
    (leg_dir / "README.md").write_text(
        "# Legacy Reconciliation — Final Authority\nCurrent: exact-legacy-plan-reconciliation-final.md\n",
        encoding="utf-8",
    )

    # Rule 67: version_consistency_final_present
    ver_dir = b / "version"
    ver_dir.mkdir(exist_ok=True)
    (ver_dir / "version-consistency-final.json").write_text(
        json.dumps({"all_consistent": True, "sprint69_mismatches": 0}),
        encoding="utf-8",
    )

    # Sprint 71 rules 73-78: stale-path scanner — add remote/remote-vs-handoff-final.json
    remote_dir = b / "remote"
    remote_dir.mkdir(exist_ok=True)
    (remote_dir / "remote-vs-handoff-final.json").write_text(
        json.dumps({
            "sprint_id": "sprint61-test",
            "comparison": "current",
            "families": [
                {"family": f, "handoff_path": f"reports/sprint61-test/handoff/per-family/{f}/", "status": "OK"}
                for f in ["cells", "words", "pdf", "diagram", "email", "slides"]
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 72 rules 79-85: remote proof consistency
    (remote_dir / "remote-proof-consistency-audit.json").write_text(
        json.dumps({
            "sprint_id": "sprint61-test",
            "consistent": True,
            "checks": [{"check_id": "RPC01", "consistent": True}],
        }),
        encoding="utf-8",
    )
    (remote_dir / "remote-readme-io-audit-final.json").write_text(
        json.dumps({
            "sprint_id": "sprint61-test",
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
    history_dir = b / "history"
    history_dir.mkdir(exist_ok=True)
    (history_dir / "remote-proof-summary-superseded.md").write_text(
        "# SUPERSEDED: Remote Truth Refresh\n\nStatus: SUPERSEDED\nOriginal incorrect claim: 42/42 examples have README I/O sections.\n",
        encoding="utf-8",
    )

    for i in range(40):
        (b / f"pad-{i:02d}.txt").write_text(f"pad {i}\n", encoding="utf-8")

    # Sprint 75 rules 86-93: weekly review classification artifacts

    # Rule 86: weekly_review_claim_matrix_present
    # Rule 93: weekly_review_verdict_not_complete_while_unclassified
    (b / "02-weekly-review-claim-vs-proof-matrix.md").write_text(
        "# Weekly Review Claim vs Proof Matrix\n\n"
        "| Item | Classification |\n"
        "|------|---------------|\n"
        "| 1 | VERIFIED_HISTORICAL_BUT_SUPERSEDED |\n"
        "| 2 | BLOCKED_EXTERNAL |\n"
        "| 3 | NEEDS_REPAIR |\n"
        "| 4 | GOVERNANCE_EXCEPTION_REQUIRED |\n",
        encoding="utf-8",
    )

    # Rule 87: pdf_publication_truth_reconciled
    (b / "pdf-publication").mkdir(parents=True, exist_ok=True)
    (b / "pdf-publication" / "pdf-pr-reconciliation.json").write_text(
        json.dumps({"claim_verdict": "VERIFIED_HISTORICAL_BUT_SUPERSEDED", "sprint_id": "sprint61-test"}),
        encoding="utf-8",
    )

    # Rule 88: formimporter_taskcard_durable
    (b / "formimporter").mkdir(parents=True, exist_ok=True)
    (b / "formimporter" / "formimporter-repro-inventory.json").write_text(
        json.dumps({"next_retest_trigger": "Aspose.PDF NuGet version > 26.5.0", "sprint_id": "sprint61-test"}),
        encoding="utf-8",
    )

    # Rule 89: words_version_drift_documented
    (b / "version-drift").mkdir(parents=True, exist_ok=True)
    (b / "version-drift" / "words-version-drift-current.json").write_text(
        json.dumps({"drift": "REMOTE_DRIFT", "sprint_id": "sprint61-test"}),
        encoding="utf-8",
    )

    # Rule 90: email_slides_runtime_validated
    # Rules 94+95: output_confirmed=true, no NO_INPUT_FIXTURE runtime_result
    (b / "post-merge-runtime").mkdir(parents=True, exist_ok=True)
    (b / "post-merge-runtime" / "post-merge-validation-matrix.json").write_text(
        json.dumps({
            "sprint_id": "sprint61-test",
            "records": [
                {
                    "scenario_id": "email-html-converter",
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
    # Rule 96: dirty_classification_must_match_after_snapshot — no src/tests in classification
    (b / "git" / "dirty-file-classification.md").write_text(
        "# Dirty File Classification\n\nAll dirty files classified.\n"
        "workspace/verification/latest/: GENERATED_WORKSPACE_STATE — EXCLUDE\n",
        encoding="utf-8",
    )

    # Rules 96, 100: dirty-state-after.txt — no src/tests modified
    (b / "git" / "dirty-state-after.txt").write_text(
        "On branch main\nnothing to commit, working tree clean\n",
        encoding="utf-8",
    )

    # Rule 92: sprint27_governance_classified
    (b / "governance").mkdir(parents=True, exist_ok=True)
    (b / "governance" / "sprint27-strict-contract-revalidation.md").write_text(
        "# Sprint 27 Strict Contract Revalidation\n\n"
        "Status: GOVERNANCE_EXCEPTION_REQUIRED\n"
        "Classification: HISTORICAL_NON_COMPLIANT\n",
        encoding="utf-8",
    )

    return b


class TestEvidenceValidatorSourceScan(unittest.TestCase):
    """Verify EvidenceValidator is imported by real pipeline source (SD60-04 fix)."""

    def test_evidence_validator_imported_by_main(self):
        """_scan_source_for_import must find evidence_validator in __main__.py."""
        real_source_root = Path(__file__).resolve().parents[2] / "src" / "plugin_examples"
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            validator = EvidenceValidator(bundle_dir=b, source_root=real_source_root)
            result = validator.validate()

        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed, f"Expected PASS but got FAIL: {rule.failure_detail}")
        self.assertIn("evidence_validator", rule.evidence)

    def test_sprint60_bundle_fails_evidence_validator_wired_rule(self):
        """Sprint 60 source did NOT wire evidence_validator — confirmed by isolation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            # Simulate a source tree WITHOUT evidence_validator import
            fake_src = Path(tmpdir) / "fake_src"
            fake_src.mkdir()
            (fake_src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (fake_src / "__main__.py").write_text("# standalone module, not wired\n", encoding="utf-8")

            validator = EvidenceValidator(bundle_dir=b, source_root=fake_src)
            result = validator.validate()

        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("not imported", rule.failure_detail.lower())


class TestReleaseStatusValidateBundleFlag(unittest.TestCase):
    """Integration tests for release-status --validate-bundle CLI wiring."""

    def _run_validate_bundle(self, bundle_dir: Path) -> int:
        """Call the release-status --validate-bundle path in __main__.main() directly."""
        from plugin_examples.__main__ import main
        argv_backup = sys.argv[:]
        try:
            sys.argv = [
                "plugin_examples",
                "release-status",
                "--validate-bundle", str(bundle_dir),
            ]
            # Mock the heavy release-status computation so we only test the EV wiring
            with patch("plugin_examples.publisher.release_status.compute_release_status") as mock_compute, \
                 patch("plugin_examples.publisher.release_status.write_release_status_report") as mock_write, \
                 patch("plugin_examples.publisher.release_status.ALL_RELEASE_FAMILIES", ["cells"]):
                mock_compute.return_value = {
                    "families": [
                        {
                            "family": "cells",
                            "last_merge_sha": None,
                            "last_post_merge_validation_status": "UNKNOWN",
                            "published_examples_count": 0,
                            "release_scope_status": "UNKNOWN",
                            "next_required_action": "none",
                        }
                    ],
                    "all_merged": False,
                    "all_post_merge_validated": False,
                }
                mock_write.return_value = Path("/tmp/fake-report.json")
                return main()
        finally:
            sys.argv = argv_backup

    def test_returns_0_on_valid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            exit_code = self._run_validate_bundle(b)
        self.assertEqual(exit_code, 0)

    def test_returns_1_on_invalid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            # Introduce a failure: empty clean proof
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            exit_code = self._run_validate_bundle(b)
        self.assertEqual(exit_code, 1)

    def test_validate_bundle_not_called_without_flag(self):
        """Without --validate-bundle, EvidenceValidator is NOT called."""
        from plugin_examples.__main__ import main
        argv_backup = sys.argv[:]
        called = []
        original_ev = EvidenceValidator.__init__

        def spy_init(self_ev, *args, **kwargs):
            called.append(True)
            return original_ev(self_ev, *args, **kwargs)

        try:
            sys.argv = ["plugin_examples", "release-status"]
            with patch("plugin_examples.publisher.release_status.compute_release_status") as mock_compute, \
                 patch("plugin_examples.publisher.release_status.write_release_status_report") as mock_write, \
                 patch("plugin_examples.publisher.release_status.ALL_RELEASE_FAMILIES", ["cells"]), \
                 patch.object(EvidenceValidator, "__init__", spy_init):
                mock_compute.return_value = {
                    "families": [
                        {
                            "family": "cells",
                            "last_merge_sha": None,
                            "last_post_merge_validation_status": "UNKNOWN",
                            "published_examples_count": 0,
                            "release_scope_status": "UNKNOWN",
                            "next_required_action": "none",
                        }
                    ],
                    "all_merged": False,
                    "all_post_merge_validated": False,
                }
                mock_write.return_value = Path("/tmp/fake-report.json")
                main()
        finally:
            sys.argv = argv_backup

        self.assertEqual(called, [], "EvidenceValidator should NOT be called without --validate-bundle")


if __name__ == "__main__":
    unittest.main()
