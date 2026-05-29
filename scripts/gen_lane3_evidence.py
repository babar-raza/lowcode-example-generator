"""Generate Lane 3 evidence files for all 6 families."""
import json
import os
import hashlib

BASE = "reports/lowcode-durable-full-closure-20260529/generation"

RUNS = {
    "cells": {
        "run_id": "pilot-cells-20260529-221017",
        "base_run": "pilot-cells-20260528-142253",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family cells --dry-run --template-mode --replay-from generation --reuse-run pilot-cells-20260528-142253",
        "durable_fix_types": ["SpreadsheetMerger"],
    },
    "diagram": {
        "run_id": "pilot-diagram-20260529-221021",
        "base_run": "pilot-diagram-20260528-142424",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family diagram --dry-run --template-mode --replay-from generation --reuse-run pilot-diagram-20260528-142424",
        "durable_fix_types": ["DiagramConverter", "PdfConverter"],
    },
    "words": {
        "run_id": "pilot-words-20260529-221024",
        "base_run": "pilot-words-heal2-20260528",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family words --dry-run --template-mode --replay-from generation --reuse-run pilot-words-heal2-20260528",
        "durable_fix_types": ["Merger", "Watermarker"],
    },
    "pdf": {
        "run_id": "pilot-pdf-20260529-222233",
        "base_run": "pilot-pdf-heal-20260528",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family pdf --dry-run --template-mode --replay-from generation --reuse-run pilot-pdf-heal-20260528",
        "durable_fix_types": ["TableGenerator"],
    },
    "email": {
        "run_id": "pilot-email-20260529-220716",
        "base_run": "pilot-email-20260528-142456",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family email --dry-run --template-mode --replay-from generation --reuse-run pilot-email-20260528-142456",
        "durable_fix_types": [],
    },
    "slides": {
        "run_id": "pilot-slides-20260529-221814",
        "base_run": "pilot-slides-20260528-143001",
        "command": ".venv/Scripts/python.exe -m plugin_examples run --family slides --dry-run --template-mode --replay-from generation --reuse-run pilot-slides-20260528-143001",
        "durable_fix_types": ["Convert"],
    },
}

for family, info in RUNS.items():
    run_id = info["run_id"]
    out_dir = f"{BASE}/{family}"
    os.makedirs(out_dir, exist_ok=True)

    report = json.load(open(f"workspace/runs/{run_id}/pilot-report.json"))
    gen_stage = None
    val_stage = None
    for s in report.get("stages", []):
        if isinstance(s, dict):
            if s["name"] == "generation":
                gen_stage = s
            if s["name"] == "validation":
                val_stage = s

    # generation-command.txt
    with open(f"{out_dir}/generation-command.txt", "w") as f:
        lines = [
            f"# {family} clean regeneration command (Lane 3)",
            f"# Sprint: lowcode-durable-full-closure-20260529",
            f"# Date: 2026-05-29",
            f"# Replay justification: --replay-from generation reuses NuGet catalog from {info['base_run']}",
            f"# to avoid re-downloading packages while ensuring fresh generation with durable fixes applied.",
            "",
            info["command"],
            "",
            f"# Produced run ID: {run_id}",
        ]
        f.write("\n".join(lines) + "\n")

    # generation-stage-result.json
    stage_result = {
        "run_id": run_id,
        "family": family,
        "generation_stage": gen_stage,
        "validation_stage": val_stage,
        "gate_summary": report.get("gate_summary"),
        "verdict": report.get("verdict"),
        "durable_fix_types_applied": info["durable_fix_types"],
        "replay_mode": "replay-from-generation",
        "base_run": info["base_run"],
    }
    with open(f"{out_dir}/generation-stage-result.json", "w") as f:
        json.dump(stage_result, f, indent=2)

    # generated-example-manifest.json
    example_index = json.load(open(f"workspace/runs/{run_id}/evidence/example-index.json"))
    manifest = {
        "run_id": run_id,
        "family": family,
        "total_examples": len(example_index.get("examples", [])),
        "examples": [
            {
                "scenario_id": e.get("scenario_id"),
                "target_framework": e.get("target_framework"),
                "input_strategy": e.get("input_strategy"),
                "status": e.get("status"),
            }
            for e in example_index.get("examples", [])
        ],
    }
    with open(f"{out_dir}/generated-example-manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # generated-source-tree-list.txt
    gen_dir = f"workspace/runs/{run_id}/generated/{family}"
    tree_lines = [f"# Generated source tree for {family} (run_id={run_id})\n"]
    if os.path.isdir(gen_dir):
        for example_dir in sorted(os.listdir(gen_dir)):
            epath = f"{gen_dir}/{example_dir}"
            if os.path.isdir(epath):
                tree_lines.append(f"{example_dir}/\n")
                for fname in sorted(os.listdir(epath)):
                    tree_lines.append(f"  {fname}\n")
    with open(f"{out_dir}/generated-source-tree-list.txt", "w") as f:
        f.writelines(tree_lines)

    # source-hash-ledger.json
    hashes = {}
    if os.path.isdir(gen_dir):
        for example_dir in sorted(os.listdir(gen_dir)):
            epath = f"{gen_dir}/{example_dir}"
            if os.path.isdir(epath):
                prog = f"{epath}/Program.cs"
                if os.path.exists(prog):
                    content = open(prog, "rb").read()
                    hashes[f"{example_dir}/Program.cs"] = hashlib.sha256(content).hexdigest()
    with open(f"{out_dir}/source-hash-ledger.json", "w") as f:
        json.dump({"run_id": run_id, "family": family, "hashes": hashes}, f, indent=2)

    # no-replay-or-replay-justification.md
    lines = [
        f"# Replay Justification -- {family}",
        "",
        f"**Run ID**: {run_id}",
        f"**Base Run**: {info['base_run']}",
        "**Replay Mode**: `--replay-from generation`",
        "",
        "## Justification",
        "",
        f"A fresh NuGet catalog download for `{family}` was avoided by replaying from `{info['base_run']}`, "
        "which has a verified api-catalog with matching denominator hash. "
        "The `--replay-from generation` mode skips `dependency_resolution`, `extraction`, `nuget_fetch`, and `reflection`, "
        "but re-runs all stages from `scenario_planning` onward including **generation** (with durable-fix templates applied), "
        "**validation** (dotnet build + run), **reviewer**, **publisher**, and **gates**.",
        "",
    ]
    if info["durable_fix_types"]:
        lines += [
            "## Durable Fixes Applied in This Run",
            "",
        ]
        for t in info["durable_fix_types"]:
            lines.append(
                f"- `{t}`: `template_first: true` -- uses deterministic C# template from `_generate_deterministic_template_for_scenario`"
            )
    else:
        lines += [
            "## Durable Fixes Applied",
            "",
            "No new fixes for this family in this sprint. Templates from prior sprint still active.",
        ]
    with open(f"{out_dir}/no-replay-or-replay-justification.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  {family}: evidence written to {out_dir}/")

print("Lane 3 evidence complete for all 6 families.")
