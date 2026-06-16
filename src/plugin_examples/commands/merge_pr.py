"""Command: merge-pr."""

from __future__ import annotations

import os
from datetime import UTC

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the merge-pr subcommand."""
    # Merge-PR command (dry-run verification and future live merge)
    parser = subparsers.add_parser(
        "merge-pr",
        help="Verify preconditions and simulate (or execute) PR merge for a family",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    parser.add_argument("--pr-number", required=True, type=int, metavar="N", help="PR number to merge (e.g., 1)")
    merge_pr_mode = parser.add_mutually_exclusive_group()
    merge_pr_mode.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Verify preconditions and simulate merge without performing any remote mutation",
    )
    merge_pr_mode.add_argument(
        "--merge",
        action="store_true",
        help="Perform live merge (blocked; requires APPROVE_MERGE_PR + future sprint enablement)",
    )
    parser.add_argument(
        "--approval-token",
        metavar="VALUE",
        help="Merge approval token. Must equal 'APPROVE_MERGE_PR'. "
        "Must NOT equal 'APPROVE_LIVE_PR'. "
        "Also readable from PLUGIN_EXAMPLES_MERGE_PR_APPROVAL env var.",
    )
    parser.add_argument(
        "--promote-latest",
        action="store_true",
        help="Write report to workspace/verification/latest/",
    )

    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the merge-pr command."""
    import json as _json
    from datetime import datetime, timezone
    from pathlib import Path as _Path

    from plugin_examples.family_config import DisabledFamilyError, load_family_config
    from plugin_examples.publisher.github_pr_merger import MergeError as _MergeError
    from plugin_examples.publisher.github_pr_merger import merge_pr, simulate_merge
    from plugin_examples.publisher.merge_approval_gate import (
        BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN,
        check_merge_approval,
    )

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args,
        command="merge-pr",
        family=args.family,
        repo_root=repo_root,
    )
    config_dir = repo_root / "pipeline" / "configs" / "families"
    verification_dir = repo_root / "workspace" / "verification"

    family = args.family
    pr_number = args.pr_number
    live_mode = getattr(args, "merge", False)
    approval_token = getattr(args, "approval_token", None)

    # Check approval token
    approved, approval_blocked = check_merge_approval(approval_token)

    # Load family config to get target repo
    config_path = config_dir / f"{family}.yml"
    try:
        cfg = load_family_config(config_path)
    except (DisabledFamilyError, FileNotFoundError) as exc:
        print(f"ERROR: Cannot load family config for '{family}': {exc}")
        return 1

    github_cfg = getattr(cfg, "github", None)
    pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None) if github_cfg else None
    target_owner = getattr(pub_repo, "owner", None) if pub_repo else None
    target_repo_name = getattr(pub_repo, "repo", None) if pub_repo else None

    if target_owner is None:
        print(f"ERROR: No publish target configured for family '{family}'")
        return 1
    assert target_repo_name is not None

    # Locate clean-checkout evidence (used by both modes)
    clean_checkout_path = verification_dir / "latest" / f"{family}-live-pr-clean-checkout-validation.json"

    # --- LIVE MERGE MODE ---
    if live_mode:
        github_token = os.environ.get("GITHUB_TOKEN", "")
        if not github_token:
            print("ERROR: --merge requires GITHUB_TOKEN environment variable")
            return 1
        if not approved:
            if approval_blocked == BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN:
                print("ERROR: APPROVE_LIVE_PR cannot be used for merge — use APPROVE_MERGE_PR")
                print("  Merge requires a SEPARATE approval from PR creation.")
            else:
                print(f"ERROR: Merge approval blocked: {approval_blocked}")
                print("  Pass --approval-token APPROVE_MERGE_PR")
            return 1

        print(f"merge-pr LIVE: {family} PR #{pr_number}")
        print(f"  Target: {target_owner}/{target_repo_name}")
        print(f"  Approval: GRANTED (token not logged)")
        print(f"  Merging... (GITHUB_TOKEN is not logged)")

        try:
            merge_result = merge_pr(
                owner=target_owner,
                repo=target_repo_name,
                pr_number=pr_number,
                family=family,
                clean_checkout_evidence_path=clean_checkout_path,
                github_token=github_token,
                merge_method="merge",
            )
        except _MergeError as exc:
            print(f"ERROR: Merge failed: {exc}")
            return 1

        merge_commit_sha = merge_result["merge_commit_sha"]

        live_merge_record = {
            "merge_type": "live_pr_merge_result",
            "merge_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "family": family,
            "pr_number": pr_number,
            "target_repo": f"{target_owner}/{target_repo_name}",
            "live_merge_performed": True,
            "merged": True,
            "merge_commit_sha": merge_commit_sha,
            "merge_method": "merge",
            "pr_title": merge_result["pr_title"],
            "preconditions": merge_result["preconditions"],
            # token is NEVER included
        }

        output_dir = verification_dir / "latest" if args.promote_latest else verification_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{family}-merge-result.json"
        with open(output_path, "w") as _f:
            _json.dump(live_merge_record, _f, indent=2)

        print(f"PR MERGED: #{pr_number} — merge commit SHA: {merge_commit_sha}")
        print(f"  DO NOT delete branch without explicit approval")
        print(f"Report: {output_path}")
        _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
        return 0

    # --- DRY-RUN / SIMULATION MODE ---
    if not approved:
        if approval_blocked == BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN:
            print("ERROR: APPROVE_LIVE_PR cannot be used for merge — use APPROVE_MERGE_PR")
            print("  Merge requires a SEPARATE approval from PR creation.")
        else:
            print(f"ERROR: Merge approval blocked: {approval_blocked}")
            print("  Pass --approval-token APPROVE_MERGE_PR or set PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR")
        # For dry-run: log the blocked reason but continue — simulation still runs to show what would fail

    # Get GitHub token for read-only PR verification
    github_token = os.environ.get("GITHUB_TOKEN", "")

    if not github_token:
        # Can still write a simulation without API calls
        print("WARNING: GITHUB_TOKEN not set — skipping remote PR verification in dry-run")
        simulation_result = {
            "simulation_type": "merge_pr_dry_run_simulation",
            "simulation_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "family": family,
            "pr_number": pr_number,
            "target_repo": f"{target_owner}/{target_repo_name}",
            "dry_run": True,
            "simulation_passed": False,
            "live_merge_performed": False,
            "approval_gate_passed": approved,
            "approval_blocked_reason": approval_blocked if not approved else None,
            "blocked_reasons": ["no_github_token_for_remote_verification"],
            "preconditions": {"github_token_present": {"result": "FAIL", "detail": "GITHUB_TOKEN not set"}},
            "note": "No GITHUB_TOKEN — cannot verify PR state. Set GITHUB_TOKEN and re-run.",
        }
    else:
        simulation = simulate_merge(
            owner=target_owner,
            repo=target_repo_name,
            pr_number=pr_number,
            family=family,
            clean_checkout_evidence_path=clean_checkout_path,
            github_token=github_token,
        )
        simulation_result = {
            "simulation_type": "merge_pr_dry_run_simulation",
            "simulation_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "family": family,
            "pr_number": pr_number,
            "target_repo": f"{target_owner}/{target_repo_name}",
            "dry_run": True,
            "simulation_passed": simulation["simulation_passed"] and approved,
            "live_merge_performed": False,
            "approval_gate_passed": approved,
            "approval_blocked_reason": approval_blocked if not approved else None,
            "blocked_reasons": (simulation["blocked_reasons"] + ([] if approved else [approval_blocked])),
            "preconditions": simulation["preconditions"],
            "pr_data": simulation.get("pr_data", {}),
            "note": simulation["note"],
        }

    output_dir = verification_dir / "latest" if args.promote_latest else verification_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{family}-merge-pr-simulation.json"
    with open(output_path, "w") as _f:
        _json.dump(simulation_result, _f, indent=2)

    sim_status = (
        "SIMULATION_PASSED"
        if simulation_result["simulation_passed"]
        else f"SIMULATION_BLOCKED ({', '.join(simulation_result['blocked_reasons'])})"
    )
    print(f"merge-pr simulation: {family} PR #{pr_number} — {sim_status}")
    print(f"  Target: {target_owner}/{target_repo_name}")
    print(f"  Approval gate: {'PASSED' if approved else f'BLOCKED ({approval_blocked})'}")
    print(f"  live_merge_performed: False")
    print(f"Report: {output_path}")
    _sim_ok = simulation_result["simulation_passed"]
    _finalize_metrics_session(
        msession,
        items_discovered=1,
        items_succeeded=1 if _sim_ok else 0,
        items_failed=0 if _sim_ok else 1,
    )
    return 0 if _sim_ok else 1
