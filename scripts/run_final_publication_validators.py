"""
Validators for lowcode-final-publication-20260601 sprint.
10 validation rules checking consistency across all artifacts.
"""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORT = REPO / "reports" / "lowcode-final-publication-20260601"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append({"rule": name, "status": status, "detail": detail})
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return condition

def main():
    print("Running 10 validation rules...\n")
    all_pass = True

    # 1. Decision board has 56 entries
    board = load_json(REPORT / "decisions" / "final-publication-decision-board.json")
    items = board.get("items", board.get("decisions", []))
    if not check("V01: Decision board has 56 items", len(items) == 56, f"found {len(items)}"):
        all_pass = False

    # 2. No human-deferred items
    deferred = [i for i in items if "HUMAN" in str(i.get("decision", "")).upper() or "PENDING" in str(i.get("decision", "")).upper() or "DEFERRED" in str(i.get("decision", "")).upper()]
    if not check("V02: No human-deferred items", len(deferred) == 0, f"found {len(deferred)}"):
        all_pass = False

    # 3. Denominator model exists and says 42
    denom_path = REPORT / "denominators" / "final-denominator-model.md"
    denom_text = denom_path.read_text(encoding="utf-8") if denom_path.exists() else ""
    if not check("V03: Denominator model states 42 canonical", "42" in denom_text and "Canonical Denominator" in denom_text):
        all_pass = False

    # 4. Format authority contracts sum to 42
    contracts_dir = REPO / "pipeline" / "format-authority" / "contracts"
    total_types = 0
    for f in contracts_dir.glob("*.json"):
        c = load_json(f)
        total_types += len(c.get("types", c.get("entries", [])))
    if not check("V04: Format authority contracts sum to 42", total_types == 42, f"found {total_types}"):
        all_pass = False

    # 5. Completion queue has 42 POST_MERGE_VERIFIED
    queue = load_json(REPO / "workspace" / "queues" / "example-completion-queue.json")
    pmv = sum(1 for e in queue["entries"] if e["state"] == "POST_MERGE_VERIFIED")
    if not check("V05: Completion queue has 42 POST_MERGE_VERIFIED", pmv == 42, f"found {pmv}"):
        all_pass = False

    # 6. Decision counts sum to 56
    decision_counts = {}
    for item in items:
        d = item.get("decision", "UNKNOWN")
        decision_counts[d] = decision_counts.get(d, 0) + 1
    total_decisions = sum(decision_counts.values())
    if not check("V06: Decision counts sum to 56", total_decisions == 56, f"found {total_decisions}"):
        all_pass = False

    # 7. Publish decisions = 44 (42 main + 1 companion + 1 env-dep)
    publish_count = sum(1 for item in items if "PUBLISH" in str(item.get("decision", "")))
    if not check("V07: Publish decisions = 44", publish_count == 44, f"found {publish_count}"):
        all_pass = False

    # 8. Exclude decisions = 12
    exclude_count = sum(1 for item in items if "EXCLUDE" in str(item.get("decision", "")) or "EXTERNAL" in str(item.get("decision", "")))
    if not check("V08: Exclude decisions = 12", exclude_count == 12, f"found {exclude_count}"):
        all_pass = False

    # 9. Policy files all exist
    policy_files = [
        REPORT / "policy" / "main-class-publication-policy.md",
        REPORT / "policy" / "companion-example-policy.md",
        REPORT / "policy" / "environment-dependent-example-policy.md",
        REPORT / "decisions" / "duplicate-example-policy.md",
    ]
    missing = [str(p.name) for p in policy_files if not p.exists()]
    if not check("V09: All policy files exist", len(missing) == 0, f"missing: {missing}"):
        all_pass = False

    # 10. No static PFX in tracked git
    import subprocess
    r = subprocess.run(["git", "ls-files", "*.pfx"], capture_output=True, text=True, cwd=str(REPO))
    pfx_files = [f for f in r.stdout.strip().split("\n") if f]
    if not check("V10: No static PFX in tracked git", len(pfx_files) == 0, f"found: {pfx_files}"):
        all_pass = False

    # Write results
    out = REPORT / "validators" / "validation-results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "sprint": "lowcode-final-publication-20260601",
        "total_rules": len(results),
        "pass": sum(1 for r in results if r["status"] == "PASS"),
        "fail": sum(1 for r in results if r["status"] == "FAIL"),
        "all_pass": all_pass,
        "rules": results,
    }
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n{'ALL PASS' if all_pass else 'FAILURES DETECTED'}: {summary['pass']}/{summary['total_rules']}")
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
