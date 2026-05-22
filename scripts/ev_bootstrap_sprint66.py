"""EV bootstrap Phase A for Sprint 66 bundle — exclude self-referential rules."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plugin_examples.evidence_validator import EvidenceValidator

bundle_dir = Path(__file__).resolve().parents[1] / "reports" / "sprint66"
source_root = Path(__file__).resolve().parents[1] / "src" / "plugin_examples"

validator = EvidenceValidator(bundle_dir=bundle_dir, source_root=source_root)

# Phase A: exclude both self-referential rules
phase_a = validator.validate(exclude_rule_ids={
    "bundle_validation_result_present_and_valid",
    "ecc_contract_computed_and_valid",
})

print(f"Phase A: {phase_a.passed}/{phase_a.total_rules} pass, failed={phase_a.failed}, overall={phase_a.overall_valid}")
for r in phase_a.rule_results:
    if not r.passed:
        print(f"  FAIL [{r.rule_id}]: {r.failure_detail[:120]}")

if phase_a.overall_valid:
    # Write Phase A result (for storage — excludes self-ref rules)
    result = phase_a.to_dict()
    out_path = bundle_dir / "evidence" / "sprint66-bundle-validation-result.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote: {out_path}")
else:
    print("\nPhase A FAILED — fix failures before writing result")
    sys.exit(1)
