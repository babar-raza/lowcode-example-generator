"""Build Sprint 65 evidence-contract.json"""
import json
from pathlib import Path

categories = [
    # Phase 0
    {"id": "EC01", "name": "sprint64_audit_report", "file": "reports/sprint65/00-sprint64-evidence-audit.md", "blocking": True},
    {"id": "EC02", "name": "sprint64_claim_vs_proof_matrix", "file": "reports/sprint65/01-sprint64-claim-vs-proof-matrix.md", "blocking": True},
    {"id": "EC03", "name": "corrected_sprint64_state", "file": "reports/sprint65/02-corrected-sprint64-state.md", "blocking": True},
    {"id": "EC04", "name": "commands_log", "file": "reports/sprint65/commands.log", "blocking": True, "semantic": "must not contain IN_PROGRESS at closure"},
    {"id": "EC05", "name": "sprint65_todo", "file": "reports/sprint65/todo.md", "blocking": True, "semantic": "must have no unchecked [ ] items"},
    # Phase 1 - Root README
    {"id": "EC06", "name": "root_readme_artifact_index", "file": "reports/sprint65/root-readme/root-readme-artifact-index.json", "blocking": True, "semantic": "must list 6 families"},
    {"id": "EC07", "name": "root_readme_vs_authority_final", "file": "reports/sprint65/root-readme/root-readme-vs-authority-final.json", "blocking": True},
    {"id": "EC08", "name": "root_readme_diff_summary", "file": "reports/sprint65/root-readme/root-readme-diff-summary.md", "blocking": True},
    {"id": "EC09", "name": "root_readme_cells", "file": "reports/sprint65/root-readme/per-family/cells-root-readme.md", "blocking": True},
    {"id": "EC10", "name": "root_readme_words", "file": "reports/sprint65/root-readme/per-family/words-root-readme.md", "blocking": True},
    {"id": "EC11", "name": "root_readme_pdf", "file": "reports/sprint65/root-readme/per-family/pdf-root-readme.md", "blocking": True},
    {"id": "EC12", "name": "root_readme_diagram", "file": "reports/sprint65/root-readme/per-family/diagram-root-readme.md", "blocking": True},
    {"id": "EC13", "name": "root_readme_email", "file": "reports/sprint65/root-readme/per-family/email-root-readme.md", "blocking": True},
    {"id": "EC14", "name": "root_readme_slides", "file": "reports/sprint65/root-readme/per-family/slides-root-readme.md", "blocking": True},
    # Phase 2 - Destination audit
    {"id": "EC15", "name": "content_audit_final", "file": "reports/sprint65/destination/content-audit-final.json", "blocking": True, "semantic": "must have 42 entries with output_format, api_type, readme_status"},
    {"id": "EC16", "name": "programcs_vs_authority_final", "file": "reports/sprint65/destination/programcs-vs-authority-final.json", "blocking": True},
    {"id": "EC17", "name": "readme_vs_authority_final", "file": "reports/sprint65/destination/readme-vs-authority-final.json", "blocking": True},
    {"id": "EC18", "name": "package_version_vs_authority", "file": "reports/sprint65/destination/package-version-vs-authority-final.json", "blocking": True},
    {"id": "EC19", "name": "deep_audit_final_summary", "file": "reports/sprint65/destination/deep-audit-final-summary.md", "blocking": True},
    # Phase 3 - Special cases
    {"id": "EC20", "name": "special_case_publication_map", "file": "reports/sprint65/special-cases/special-case-publication-map.json", "blocking": True},
    {"id": "EC21", "name": "special_case_placement_proof", "file": "reports/sprint65/special-cases/special-case-placement-proof.md", "blocking": True},
    {"id": "EC22", "name": "special_case_validator_tests", "file": "reports/sprint65/special-cases/special-case-validator-test-results.txt", "blocking": True, "semantic": "must show 0 failed"},
    # Phase 4 - PDF version
    {"id": "EC23", "name": "pdf_version_final_decision", "file": "reports/sprint65/version/pdf-version-final-decision.md", "blocking": True},
    {"id": "EC24", "name": "pdf_version_audit_final", "file": "reports/sprint65/version/pdf-version-audit-final.json", "blocking": True},
    {"id": "EC25", "name": "version_policy_final", "file": "reports/sprint65/version/version-policy-final.json", "blocking": True},
    # Phase 5 - EV/ECC
    {"id": "EC26", "name": "semantic_rule_gap_analysis", "file": "reports/sprint65/evidence/semantic-rule-gap-analysis.md", "blocking": True},
    {"id": "EC27", "name": "semantic_rule_source_proof", "file": "reports/sprint65/evidence/semantic-rule-source-proof.patch", "blocking": True},
    {"id": "EC28", "name": "semantic_rule_test_results", "file": "reports/sprint65/evidence/semantic-rule-test-results.txt", "blocking": True, "semantic": "must show 0 failed"},
    {"id": "EC29", "name": "sprint64_revalidation_result", "file": "reports/sprint65/evidence/sprint64-revalidation-result.json", "blocking": True, "semantic": "must show overall_valid=false"},
    {"id": "EC30", "name": "sprint65_final_validation_result", "file": "reports/sprint65/evidence/sprint65-final-validation-result.json", "blocking": True, "semantic": "must show overall_valid=true, no internal contradiction"},
    {"id": "EC31", "name": "evidence_contract_computed", "file": "reports/sprint65/evidence/evidence-contract-computed.json", "blocking": True},
    # Phase 6 - Publication truth
    {"id": "EC32", "name": "publication_truth_matrix", "file": "reports/sprint65/publication/publication-truth-matrix.json", "blocking": True},
    {"id": "EC33", "name": "remote_proof_index", "file": "reports/sprint65/publication/remote-proof-index.json", "blocking": True},
    {"id": "EC34", "name": "live_approval_check", "file": "reports/sprint65/publication/live-approval-check.md", "blocking": True},
    {"id": "EC35", "name": "publication_readiness_final", "file": "reports/sprint65/publication/publication-readiness-final.json", "blocking": True},
    # Phase 7 - Handoff
    {"id": "EC36", "name": "handoff_index", "file": "reports/sprint65/handoff/publication-handoff-index.json", "blocking": True},
    {"id": "EC37", "name": "reviewer_summary", "file": "reports/sprint65/handoff/reviewer-summary.md", "blocking": True},
    {"id": "EC38", "name": "rollback_plan", "file": "reports/sprint65/handoff/rollback-plan.md", "blocking": True},
    # Phase 8 - Tests
    {"id": "EC39", "name": "test_run_log", "file": "reports/sprint65/lanes/lane-I/test-run.log", "blocking": True, "semantic": "must show 0 failed"},
    {"id": "EC40", "name": "git_status_end", "file": "reports/sprint65/lanes/lane-I/git-status.txt", "blocking": True},
    # Phase 9 - Final
    {"id": "EC41", "name": "bundle_manifest", "file": "reports/sprint65/bundle-manifest.json", "blocking": True},
    {"id": "EC42", "name": "final_verdict", "file": "reports/sprint65/final-verdict.md", "blocking": True},
    {"id": "EC43", "name": "sprint_state", "file": "reports/sprint65/sprint-state.json", "blocking": True},
    {"id": "EC44", "name": "final_clean_proof", "file": "reports/sprint65/git/final-clean-proof.txt", "blocking": True, "semantic": "nonzero, git header present, captured AFTER final commit"},
    {"id": "EC45", "name": "validator_test_results", "file": "reports/sprint65/evidence/validator-test-results.txt", "blocking": True},
    {"id": "EC46", "name": "sprint65_bundle_validation", "file": "reports/sprint65/evidence/sprint65-bundle-validation-result.json", "blocking": True},
]

contract = {
    "contract_version": "sprint65-v1",
    "sprint_id": "sprint65-publication-truth-repair-root-readme-strict-audit-handoff",
    "created_at": "2026-05-22T00:00:00Z",
    "description": "Sprint 65 evidence contract. Repairs Sprint 64 overclaims: remote proof, root README artifacts, strict destination audit, special-case placement, hardened EV/ECC, publication handoff.",
    "bundle_min_files": 46,
    "required_evidence_categories": [
        dict(id=c["id"], name=c["name"], file=c["file"], blocking=c["blocking"], status="PENDING",
             **{"semantic": c["semantic"]} if "semantic" in c else {})
        for c in categories
    ]
}

out = Path("reports/sprint65/evidence-contract.json")
out.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Created evidence-contract.json with {len(categories)} categories")
