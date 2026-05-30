#!/usr/bin/env python3
"""Run pdf pilot with replay-from=generation to validate new templates.

Uses prior pdf run as base for catalog/packages, regenerates all examples
using template_first=True for the new types.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plugin_examples.runner import run_pipeline

repo_root = Path(__file__).resolve().parents[1]

PRIOR_RUN = "pilot-pdf-heal-20260528"
RUN_ID = "pilot-pdf-repair-20260530"

# Clean run dir if exists
run_dir = repo_root / "workspace" / "runs" / RUN_ID
if run_dir.exists():
    shutil.rmtree(run_dir)
    print(f"Cleaned: {run_dir}")

report = run_pipeline(
    family="pdf",
    dry_run=True,
    skip_run=False,
    template_mode=True,
    require_llm=False,
    require_validation=False,
    require_reviewer=False,
    run_id=RUN_ID,
    repo_root=repo_root,
    replay_from="generation",
    reuse_run_id=PRIOR_RUN,
)

gs = report.get("gate_summary", {})
verdict = report.get("verdict", "UNKNOWN")
run_id = report.get("meta", {}).get("run_id", "unknown")

print(f"\n{'='*60}")
print(f"Pilot Run: {run_id}")
print(f"Verdict: {verdict}")
print(f"Stages: {gs.get('passed',0)} passed, {gs.get('degraded',0)} degraded, "
      f"{gs.get('failed',0)} failed, {gs.get('skipped',0)} skipped")
print(f"Duration: {report.get('meta',{}).get('total_duration_ms',0):.0f}ms")
print(f"{'='*60}\n")

if gs.get("hard_stopped"):
    sys.exit(1)
sys.exit(0)
