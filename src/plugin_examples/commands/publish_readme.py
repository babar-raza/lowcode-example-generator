"""Command: publish-readme."""

from __future__ import annotations

import os

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the publish-readme subcommand."""
    # publish-readme command
    parser = subparsers.add_parser(
        "publish-readme",
        help="Create a README-only PR in the target repo (backfill pipeline-generated README)",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    parser.add_argument(
        "--publish", action="store_true",
        help="Live mode: create real PR on GitHub (requires GITHUB_TOKEN + approval token)",
    )
    parser.add_argument(
        "--approval-token", metavar="TOKEN",
        help="Approval token (must equal APPROVE_LIVE_PR for live mode)",
    )
    parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write evidence to workspace/verification/latest/ (always on)",
    )
    
    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the publish-readme command."""
    import json as _json
    import re as _re
    import tempfile as _tempfile
    from plugin_examples.family_config import load_family_config, DisabledFamilyError
    from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme, write_readme
    from plugin_examples.publisher.readme_auditor import audit_readme
    from plugin_examples.publisher.approval_gate import check_approval
    from datetime import datetime, timezone
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[2]
    verification_dir = repo_root / "workspace" / "verification"
    family = args.family
    msession, mcollector = _create_metrics_session(
        args, command="publish-readme", family=family, repo_root=repo_root,
    )
    live_mode = getattr(args, "publish", False)
    dry_run = not live_mode
    generation_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    # --- Load family config ---
    config_path = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
    try:
        cfg = load_family_config(config_path)
    except (DisabledFamilyError, FileNotFoundError) as exc:
        print(f"ERROR: Cannot load family config for '{family}': {exc}")
        return 1

    # --- Resolve package path ---
    package_path = repo_root / "workspace" / "pr-dry-run" / f"{family}-controlled-pilot"
    if not package_path.exists():
        package_path = repo_root / "workspace" / "pr-dry-run" / family
    if not package_path.exists():
        print(f"ERROR: Package path not found: {package_path}")
        print(f"  Run 'render-root-readme --family {family}' first to create the package.")
        return 1

    # --- Cumulative example discovery via readme_inventory ---
    from plugin_examples.publisher.readme_inventory import (
        discover_family_inventory as _discover_inv_pr,
        build_cumulative_examples_meta as _build_cum_meta_pr,
        build_package_path_map as _build_pkg_map_pr,
    )
    _inv_entries_pr, _inv_trail_pr = _discover_inv_pr(
        family=family,
        repo_root=repo_root,
        inventory_mode="repo_actual",
    )
    _examples_meta_pr = _build_cum_meta_pr(_inv_entries_pr)
    _pkg_path_map_pr = _build_pkg_map_pr(_inv_entries_pr)
    example_dirs = [e["name"] for e in _examples_meta_pr]

    if not example_dirs:
        print(f"ERROR: No examples discovered for family '{family}'")
        return 1

    # --- Resolve package version ---
    pkg_version = "unknown"
    live_pr_path = verification_dir / "latest" / f"{family}-live-pr-result.json"
    if live_pr_path.exists():
        try:
            _d = _json.loads(live_pr_path.read_text(encoding="utf-8"))
            pkg_version = _d.get("nuget_version", "") or "unknown"
        except (OSError, _json.JSONDecodeError):
            pass
    if pkg_version == "unknown":
        props_path = package_path / "Directory.Packages.props"
        if props_path.exists():
            try:
                _m = _re.search(r'Version="([^"]+)"', props_path.read_text())
                if _m:
                    pkg_version = _m.group(1)
            except OSError:
                pass

    # --- Render README ---
    try:
        ctx = build_readme_context(
            family=family,
            family_config=cfg,
            examples=_examples_meta_pr,
            package_version=pkg_version,
            generation_date=generation_date,
            package_path=package_path,
            package_path_map=_pkg_path_map_pr if _pkg_path_map_pr else None,
        )
        readme_content = render_readme(ctx)
    except Exception as exc:
        print(f"ERROR: README render failed: {exc}")
        return 1

    # --- Audit ---
    readme_audit = audit_readme(readme_content, ctx)
    if not readme_audit.passed:
        print(f"ERROR: README audit FAILED for {family}: {readme_audit.warnings}")
        return 1

    # --- GitHub config ---
    github_cfg = getattr(cfg, "github", None)
    pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None) if github_cfg else None
    target_owner = getattr(pub_repo, "owner", None) if pub_repo else None
    target_repo_name = getattr(pub_repo, "repo", None) if pub_repo else None
    target_branch = getattr(pub_repo, "branch", "main") if pub_repo else "main"

    if target_owner is None or target_repo_name is None:
        print(f"ERROR: No publish target configured for family '{family}'")
        return 1

    # --- NO_CHANGE detection via GitHub API ---
    import hashlib as _hashlib
    import base64 as _base64
    import requests as _requests

    remote_readme_sha: str | None = None
    remote_readme_content: str | None = None
    no_change = False
    github_token_for_check = os.environ.get("GITHUB_TOKEN", "")
    headers_for_check: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
    if github_token_for_check:
        headers_for_check["Authorization"] = f"token {github_token_for_check}"
    try:
        _resp = _requests.get(
            f"https://api.github.com/repos/{target_owner}/{target_repo_name}/contents/README.md",
            headers=headers_for_check,
            timeout=15,
        )
        if _resp.status_code == 200:
            _rdata = _resp.json()
            remote_readme_sha = _rdata.get("sha", "")
            _raw = _base64.b64decode(_rdata.get("content", "").replace("\n", ""))
            remote_readme_content = _raw.decode("utf-8", errors="replace")
            # Compare normalized content
            if remote_readme_content.strip() == readme_content.strip():
                no_change = True
        elif _resp.status_code == 404:
            remote_readme_sha = None
            remote_readme_content = None
    except Exception:
        pass  # proceed without NO_CHANGE detection if network unavailable

    if no_change:
        print(f"publish-readme: {family} — NO_CHANGE (remote README matches pipeline-generated content)")
        _ev = {
            "result_type": "readme_backfill_result",
            "date": generation_date,
            "family": family,
            "target_repo": f"{target_owner}/{target_repo_name}",
            "action": "NO_CHANGE",
            "remote_readme_sha": remote_readme_sha,
            "readme_bytes": len(readme_content),
            "audit_passed": True,
            "no_remote_write_performed": True,
        }
        _ev_path = verification_dir / "latest" / f"{family}-readme-backfill-result.json"
        _ev_path.write_text(_json.dumps(_ev, indent=2), encoding="utf-8")
        _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
        return 0

    # --- Approval check ---
    approval_token = getattr(args, "approval_token", None)
    approved, approval_blocked = check_approval(approval_token)

    branch_name = f"plugin-examples/{family}/readme/{run_ts}"
    pr_title = f"Add pipeline-generated README for {ctx.display_name} LowCode Examples"
    pr_body = (
        f"## README Backfill — {ctx.display_name} LowCode Examples\n\n"
        f"This PR adds the pipeline-generated `README.md` to the repository root.\n\n"
        f"**Why this PR exists:** The initial PR #1 was created before the README Sprint, "
        f"so it did not include a README. The repository currently has a 40-byte GitHub auto-init stub.\n\n"
        f"**Package version:** `{pkg_version}`\n"
        f"**Examples covered:** {len(example_dirs)} ({', '.join(f'`{e}`' for e in example_dirs)})\n"
        f"**README bytes:** {len(readme_content)}\n"
        f"**Audit status:** PASS\n\n"
        f"Generated by the lowcode-example-generator pipeline on {generation_date}.\n"
    )

    if dry_run:
        # Dry-run simulation: no remote write
        sim = {
            "result_type": "readme_backfill_simulation",
            "date": generation_date,
            "family": family,
            "dry_run": True,
            "target_repo": f"{target_owner}/{target_repo_name}",
            "branch_name": branch_name,
            "pr_title": pr_title,
            "readme_bytes": len(readme_content),
            "audit_passed": readme_audit.passed,
            "remote_readme_sha": remote_readme_sha,
            "remote_readme_is_stub": bool(remote_readme_content and len(remote_readme_content.strip()) < 60),
            "no_change": False,
            "approval_granted": approved,
            "no_remote_write_performed": True,
            "simulation_verdict": "SIMULATION_READY" if approved else "SIMULATION_BLOCKED_NO_APPROVAL",
        }
        ev_path = verification_dir / "latest" / f"{family}-readme-backfill-simulation.json"
        ev_path.write_text(_json.dumps(sim, indent=2), encoding="utf-8")
        print(f"publish-readme (dry-run): {family}")
        print(f"  Target: {target_owner}/{target_repo_name} (base: {target_branch})")
        print(f"  Branch: {branch_name}")
        print(f"  PR title: {pr_title}")
        print(f"  README bytes: {len(readme_content)}")
        print(f"  Audit: PASS")
        print(f"  Remote stub SHA: {remote_readme_sha or 'unknown'}")
        print(f"  Simulation verdict: {sim['simulation_verdict']}")
        print(f"  Evidence: {ev_path}")
        print("  No remote write performed (dry-run).")
        _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
        return 0

    # --- LIVE MODE ---
    if not approved:
        print(f"ERROR: Live publish blocked: {approval_blocked}")
        print("  Set PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR or pass --approval-token APPROVE_LIVE_PR")
        return 1
    if not github_token_for_check:
        print("ERROR: --publish requires GITHUB_TOKEN environment variable")
        return 1

    from plugin_examples.publisher.github_pr_publisher import (
        create_github_pr,
        PublishingError as _GHError,
    )

    # Create a temp dir containing only README.md
    with _tempfile.TemporaryDirectory() as _tmpdir:
        _tmp_readme = _Path(_tmpdir) / "README.md"
        _tmp_readme.write_text(readme_content, encoding="utf-8")

        print(f"publish-readme LIVE: {family}")
        print(f"  Target: {target_owner}/{target_repo_name} (branch: {target_branch})")
        print(f"  New branch: {branch_name}")
        print(f"  PR title: {pr_title}")
        print(f"  README bytes: {len(readme_content)}")
        print("  Approval: GRANTED")
        print("  Creating README-only PR... (GITHUB_TOKEN is not logged)")

        try:
            pr_result = create_github_pr(
                owner=target_owner,
                repo=target_repo_name,
                base_branch=target_branch,
                branch_name=branch_name,
                pr_title=pr_title,
                pr_body=pr_body,
                package_path=_Path(_tmpdir),
                labels=["automated", "readme"],
                github_token=github_token_for_check,
            )
        except _GHError as exc:
            print(f"ERROR: GitHub PR creation failed: {exc}")
            return 1

    pr_url = pr_result["pr_url"]
    pr_number = pr_result["pr_number"]
    files_count = pr_result.get("files_count", 1)

    live_ev = {
        "result_type": "readme_backfill_result",
        "date": generation_date,
        "family": family,
        "dry_run": False,
        "live_pr_created": True,
        "pr_url": pr_url,
        "pr_number": pr_number,
        "branch_name": branch_name,
        "target_repo": f"{target_owner}/{target_repo_name}",
        "pr_title": pr_title,
        "files_committed": files_count,
        "readme_bytes": len(readme_content),
        "package_version": pkg_version,
        "audit_passed": True,
        "remote_stub_sha_replaced": remote_readme_sha,
    }
    ev_path = verification_dir / "latest" / f"{family}-readme-backfill-result.json"
    ev_path.write_text(_json.dumps(live_ev, indent=2), encoding="utf-8")

    print(f"  PR created: {pr_url}")
    print(f"  PR number: #{pr_number}")
    print(f"  Files committed: {files_count}")
    print(f"  Evidence: {ev_path}")
    _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
    return 0

