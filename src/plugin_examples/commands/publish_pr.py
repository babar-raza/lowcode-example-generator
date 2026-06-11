"""Command: publish-pr."""

from __future__ import annotations

import os

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the publish-pr subcommand."""
    # Publish-PR command (dry-run simulation and live PR creation)
    parser = subparsers.add_parser(
        "publish-pr",
        help="Simulate (or execute) live PR creation for a family's verified dry-run package",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    publish_pr_mode = parser.add_mutually_exclusive_group()
    publish_pr_mode.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate PR creation without pushing (default when --publish not specified)",
    )
    publish_pr_mode.add_argument(
        "--publish",
        action="store_true",
        help="Create a real PR on GitHub (requires GITHUB_TOKEN + --approval-token APPROVE_LIVE_PR)",
    )
    parser.add_argument(
        "--approval-token",
        metavar="VALUE",
        help="Live publish approval token. Must equal 'APPROVE_LIVE_PR'. "
        "Required for --publish mode. Also readable from PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL.",
    )
    parser.add_argument(
        "--package-path",
        metavar="PATH",
        help="Override package path (default: workspace/pr-dry-run/{family}-controlled-pilot/). "
        "Use to publish PR groups with separate packages without manual swapping, e.g. "
        "pdf-controlled-pilot-pr5 for Jpeg/Tiff/Png or pdf-controlled-pilot-pr6 for "
        "TableGenerator/TocGenerator/ImageExtractor.",
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
    """Handle the publish-pr command."""
    import json as _json
    import re as _re
    from plugin_examples.family_config import load_family_config, DisabledFamilyError
    from plugin_examples.publisher.pr_builder import build_pr
    from plugin_examples.publisher.approval_gate import check_approval
    from datetime import datetime, timezone
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[3]
    msession, mcollector = _create_metrics_session(
        args,
        command="publish-pr",
        family=args.family,
        repo_root=repo_root,
    )
    config_dir = repo_root / "pipeline" / "configs" / "families"
    verification_dir = repo_root / "workspace" / "verification"
    family = args.family

    # Determine mode: live publish requires --publish flag
    live_mode = getattr(args, "publish", False)
    dry_run = not live_mode

    # Load family config
    config_path = config_dir / f"{family}.yml"
    try:
        cfg = load_family_config(config_path)
    except (DisabledFamilyError, FileNotFoundError) as exc:
        print(f"ERROR: Cannot load family config for '{family}': {exc}")
        return 1

    # Load publish readiness from evidence
    readiness_path = verification_dir / "latest" / "family-publish-readiness.json"
    repo_access_ready = False
    pr_permission_ready = False
    if readiness_path.exists():
        try:
            with open(readiness_path) as _f:
                readiness_data = _json.load(_f)
            for fam_rec in readiness_data.get("families", []):
                if fam_rec.get("family") == family:
                    repo_access_ready = fam_rec.get("repo_access_ready", False)
                    pr_permission_ready = fam_rec.get("pr_permission_ready", False)
        except (OSError, _json.JSONDecodeError):
            pass

    # Fallback: check family-repo-access-resolution.json (authoritative source
    # written by resolve-repo-access command) if readiness flags are still False
    if not repo_access_ready or not pr_permission_ready:
        resolver_path = verification_dir / "latest" / "family-repo-access-resolution.json"
        if resolver_path.exists():
            try:
                with open(resolver_path) as _f:
                    resolver_data = _json.load(_f)
                for fam_rec in resolver_data.get("families", []):
                    if fam_rec.get("family") == family:
                        if fam_rec.get("repo_access_ready", False):
                            repo_access_ready = True
                        if fam_rec.get("pr_permission_ready", False):
                            pr_permission_ready = True
            except (OSError, _json.JSONDecodeError):
                pass

    # Load gate verdict
    gate_path = verification_dir / "latest" / "gate-results.json"
    gate_verdict_ok = False
    gate_verdict_name = "UNKNOWN"
    if gate_path.exists():
        try:
            with open(gate_path) as _f:
                gate_data = _json.load(_f)
            gate_verdict_ok = gate_data.get("publishable", False) or gate_data.get("all_required_passed", False)
            gate_verdict_name = gate_data.get("verdict", "UNKNOWN")
        except (OSError, _json.JSONDecodeError):
            pass

    # Locate dry-run package — honour explicit --package-path if provided
    _explicit_pkg = getattr(args, "package_path", None)
    if _explicit_pkg:
        package_path = _Path(_explicit_pkg)
    else:
        package_path = repo_root / "workspace" / "pr-dry-run" / f"{family}-controlled-pilot"
    package_exists = package_path.exists()
    example_dirs = []
    if package_exists:
        examples_root = package_path / "examples" / family / "lowcode"
        if examples_root.exists():
            example_dirs = [d.name for d in sorted(examples_root.iterdir()) if d.is_dir()]

    # Get NuGet version from Directory.Packages.props
    pkg_version = "unknown"
    props_path = package_path / "Directory.Packages.props"
    if props_path.exists():
        try:
            props_text = props_path.read_text()
            m = _re.search(r'Version="([^"]+)"', props_text)
            if m:
                pkg_version = m.group(1)
        except OSError:
            pass

    # --- Render and write README.md into package root (both dry-run and live) ---
    # Uses cumulative inventory: repo_actual (post-merge) + current package
    # so the README lists all examples that will exist in the repo after merge.
    if package_exists and len(example_dirs) > 0:
        try:
            from plugin_examples.publisher.readme_renderer import (
                build_readme_context as _build_readme_ctx,
                render_readme as _render_readme,
                write_readme as _write_readme,
            )
            from plugin_examples.publisher.readme_auditor import (
                audit_readme as _audit_readme,
                audit_readme_staleness as _audit_staleness,
            )
            from plugin_examples.publisher.readme_inventory import (
                discover_family_inventory as _discover_inv,
                build_cumulative_examples_meta as _build_cum_meta,
                build_package_path_map as _build_pkg_map,
            )
            import json as _json_r

            # Discover cumulative inventory: repo base + this package
            _inv_entries, _inv_trail = _discover_inv(
                family=family,
                repo_root=repo_root,
                inventory_mode="current_package_overlay",
                current_package_path=package_path,
            )
            _examples_meta = _build_cum_meta(_inv_entries)
            _pkg_path_map = _build_pkg_map(_inv_entries)

            _gen_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            _readme_ctx = _build_readme_ctx(
                family=family,
                family_config=cfg,
                examples=_examples_meta,
                package_version=pkg_version,
                generation_date=_gen_date,
                package_path=package_path,
                package_path_map=_pkg_path_map if len(_pkg_path_map) > 0 else None,
            )
            _readme_content = _render_readme(_readme_ctx)
            _write_readme(_readme_content, package_path / "README.md")

            # Audit the rendered README
            _readme_audit = _audit_readme(_readme_content, _readme_ctx)
            if not _readme_audit.passed:
                if live_mode:
                    print(f"ERROR: README audit FAILED for {family} — blocking live publish: {_readme_audit.warnings}")
                    return 1
                else:
                    print(
                        f"WARNING: README audit failed for {family} (non-blocking in dry-run): {_readme_audit.warnings}"
                    )
            else:
                print(
                    f"  README.md rendered and audited: PASS ({len(_readme_content)} bytes, {len(_inv_entries)} examples)"
                )

            # Staleness gate: fail closed if README is stale against intended branch content
            _expected_names = [e.name for e in _inv_entries]
            _staleness = _audit_staleness(_readme_content, _expected_names)
            if _staleness.is_stale:
                _stale_msg = (
                    f"README staleness FAILED for {family}: "
                    f"missing={_staleness.missing_from_readme}, "
                    f"extra={_staleness.extra_in_readme}"
                )
                if live_mode:
                    print(f"ERROR: {_stale_msg}")
                    return 1
                else:
                    print(f"WARNING: {_stale_msg}")
        except Exception as _readme_exc:
            # README rendering is non-blocking for dry-run; block for live publish
            if live_mode:
                print(f"ERROR: README render failed (blocking for live publish): {_readme_exc}")
                return 1
            else:
                print(f"WARNING: README render failed (non-blocking in dry-run): {_readme_exc}")

    # Build run_id for branch name
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = run_ts  # used in branch: plugin-examples/{family}/{run_id}

    # Load excluded scenario summaries for PR body
    from plugin_examples.publisher.publisher import _load_excluded_scenario_summaries

    excluded_scenario_lines = _load_excluded_scenario_summaries(verification_dir, family)

    # Build PR content
    pr_content = build_pr(
        family=family,
        run_id=run_id,
        examples_count=len(example_dirs),
        package_version=pkg_version,
        examples_list=example_dirs,
        excluded_scenarios=excluded_scenario_lines or None,
    )

    # Check approval token (always evaluate — blocks live mode if missing)
    approval_token = getattr(args, "approval_token", None)
    approved, approval_blocked = check_approval(approval_token)

    # GitHub config
    github_cfg = getattr(cfg, "github", None)
    pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None) if github_cfg else None
    target_owner = getattr(pub_repo, "owner", None) if pub_repo else None
    target_repo_name = getattr(pub_repo, "repo", None) if pub_repo else None
    target_branch = getattr(pub_repo, "branch", "main") if pub_repo else None

    # --- LIVE MODE ---
    if live_mode:
        # All guards must pass for live mode
        github_token = os.environ.get("GITHUB_TOKEN", "")
        if not github_token:
            print("ERROR: --publish requires GITHUB_TOKEN environment variable")
            return 1
        if not approved:
            print(f"ERROR: Live publish blocked: {approval_blocked}")
            print(
                "  Set PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR or pass --approval-token APPROVE_LIVE_PR"
            )
            return 1
        if not package_exists or len(example_dirs) == 0:
            print(f"ERROR: Package not found or empty: {package_path}")
            return 1
        if not gate_verdict_ok:
            print(f"ERROR: Gate verdict not publishable: {gate_verdict_name}")
            return 1
        if not repo_access_ready or not pr_permission_ready:
            print(
                f"ERROR: Repo access not ready (repo_access={repo_access_ready}, pr_permission={pr_permission_ready})"
            )
            print("  Run: python -m plugin_examples probe-publish-permissions --families " + family)
            return 1
        if target_owner is None:
            print(f"ERROR: No publish target configured for family '{family}'")
            return 1

        # README audit gate — must have a content-based, passing audit before live publish
        from plugin_examples.publisher.readme_audit_gate import (
            check_readme_audit_gate as _check_readme_gate,
            README_AUDIT_ENV_VAR as _README_ENV,
            README_AUDIT_EXPECTED_VALUE as _README_EXPECTED,
        )

        _readme_push_approval = os.environ.get(_README_ENV, getattr(args, "approval_token", None))
        _gate_result = _check_readme_gate(
            family=family,
            verification_dir=verification_dir,
            run_id=run_id,
            readme_push_approval=_readme_push_approval,
        )
        if not _gate_result.get("gate_passed"):
            print(f"ERROR: README audit gate blocked live publish: {_gate_result.get('blocked_reason')}")
            print(f"  Set {_README_ENV}={_README_EXPECTED} to override if audit is valid")
            return 1

        from plugin_examples.publisher.github_pr_publisher import (
            create_github_pr,
            PublishingError as _GHError,
        )

        branch_name = pr_content.branch  # plugin-examples/{family}/{run_id}
        if branch_name == target_branch:
            print(f"ERROR: blocked_publish_to_main: branch '{branch_name}' equals target branch '{target_branch}'")
            return 1

        print(f"publish-pr LIVE: {family}")
        print(f"  Target: {target_owner}/{target_repo_name} (branch: {target_branch})")
        print(f"  New branch: {branch_name}")
        print(f"  Package: {package_path} ({len(example_dirs)} examples)")
        print(f"  PR title: {pr_content.title}")
        print("  Approval: GRANTED")
        print("  Creating PR... (GITHUB_TOKEN is not logged)")

        try:
            # IMPORTANT: github_token is never logged
            pr_result = create_github_pr(
                owner=target_owner,
                repo=target_repo_name,
                base_branch=target_branch,
                branch_name=branch_name,
                pr_title=pr_content.title,
                pr_body=pr_content.body,
                package_path=package_path,
                labels=pr_content.labels,
                github_token=github_token,
            )
        except _GHError as exc:
            print(f"ERROR: GitHub PR creation failed: {exc}")
            return 1

        pr_url = pr_result["pr_url"]
        pr_number = pr_result["pr_number"]
        files_count = pr_result["files_count"]

        live_result = {
            "simulation_type": "publish_pr_live_result",
            "publish_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "family": family,
            "dry_run": False,
            "live_pr_created": True,
            "live_push_performed": True,
            "pr_url": pr_url,
            "pr_number": pr_number,
            "branch_name": branch_name,
            "files_committed": files_count,
            "pr_title": pr_content.title,
            "examples_count": len(example_dirs),
            "example_names": example_dirs,
            "nuget_version": pkg_version,
            "target_owner": target_owner,
            "target_repo": target_repo_name,
            "target_branch": target_branch,
            "gate_verdict": gate_verdict_name,
            "repo_access_ready": repo_access_ready,
            "pr_permission_ready": pr_permission_ready,
            # token is NEVER included
        }

        output_dir = verification_dir / "latest" if args.promote_latest else verification_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{family}-live-pr-result.json"
        with open(output_path, "w") as _f:
            _json.dump(live_result, _f, indent=2)

        print(f"PR CREATED: #{pr_number} {pr_url}")
        print(f"  Branch: {branch_name}")
        print(f"  Files committed: {files_count}")
        print(f"  DO NOT MERGE without human review")
        print(f"Report: {output_path}")
        _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
        return 0

    # --- DRY-RUN / SIMULATION MODE ---
    simulation_passed = all(
        [
            package_exists,
            len(example_dirs) > 0,
            gate_verdict_ok,
            repo_access_ready,
            pr_permission_ready,
            target_owner is not None,
        ]
    )
    blocked_reasons = []
    if not package_exists:
        blocked_reasons.append(f"dry_run_package_not_found: {package_path}")
    if len(example_dirs) == 0:
        blocked_reasons.append("no_examples_in_package")
    if not gate_verdict_ok:
        blocked_reasons.append(f"gate_verdict_not_publishable: {gate_verdict_name}")
    if not repo_access_ready:
        blocked_reasons.append("repo_access_not_ready")
    if not pr_permission_ready:
        blocked_reasons.append("pr_permission_not_ready")
    if not approved:
        blocked_reasons.append(f"approval_gate: {approval_blocked} (required for live publish only)")
    if target_owner is None:
        blocked_reasons.append("no_publish_target_in_config")

    simulation_result = {
        "simulation_type": "publish_pr_dry_run_simulation",
        "simulation_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "family": family,
        "dry_run": True,
        "simulation_passed": simulation_passed,
        "blocked_reasons": blocked_reasons,
        "pr_content": {
            "title": pr_content.title,
            "branch": pr_content.branch,
            "labels": pr_content.labels,
            "body_preview": pr_content.body[:400],
        },
        "package_path": str(package_path),
        "package_exists": package_exists,
        "examples_count": len(example_dirs),
        "example_names": example_dirs,
        "nuget_version": pkg_version,
        "target_owner": target_owner,
        "target_repo": target_repo_name,
        "target_branch": target_branch,
        "gate_verdict": gate_verdict_name,
        "gate_verdict_ok": gate_verdict_ok,
        "repo_access_ready": repo_access_ready,
        "pr_permission_ready": pr_permission_ready,
        "approval_gate_passed": approved,
        "approval_blocked_reason": approval_blocked if not approved else None,
        "live_push_performed": False,
        "live_pr_created": False,
        "note": (
            "Simulation only. No branch created, no commit pushed, no PR opened. "
            "For live PR: python -m plugin_examples publish-pr "
            f"--family {family} --publish --approval-token APPROVE_LIVE_PR"
        ),
    }

    output_dir = verification_dir / "latest" if args.promote_latest else verification_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{family}-live-pr-simulation.json"
    with open(output_path, "w") as _f:
        _json.dump(simulation_result, _f, indent=2)

    sim_status = "SIMULATION_PASSED" if simulation_passed else f"SIMULATION_BLOCKED ({', '.join(blocked_reasons)})"
    print(f"publish-pr simulation: {family} — {sim_status}")
    print(f"  Package: {package_path} ({'exists' if package_exists else 'MISSING'})")
    print(f"  Examples: {len(example_dirs)}")
    print(f"  Target: {target_owner}/{target_repo_name} (branch: {target_branch})")
    print(f"  Gate verdict: {gate_verdict_name}")
    print(f"  repo_access_ready: {repo_access_ready}, pr_permission_ready: {pr_permission_ready}")
    print(f"  Approval gate: {'PASSED' if approved else f'BLOCKED ({approval_blocked})'}")
    print(f"  PR title: {pr_content.title}")
    print(f"  live_push_performed: False")
    print(f"Report: {output_path}")
    _finalize_metrics_session(
        msession,
        items_discovered=1,
        items_succeeded=1 if simulation_passed else 0,
        items_failed=0 if simulation_passed else 1,
    )
    return 0 if simulation_passed else 1
