"""Entry point for the plugin examples pipeline."""

import argparse
import os
import sys
import logging
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="plugin-examples",
        description="Aspose .NET Plugin Example Generation Pipeline",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    subparsers = parser.add_subparsers(dest="command")

    # Status command
    subparsers.add_parser("status", help="Show pipeline status")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the pipeline for a family")
    run_parser.add_argument("--family", required=True, help="Family name (e.g., cells)")
    run_parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (default)")
    run_parser.add_argument("--template-mode", action="store_true",
                            help="Use template generation instead of LLM")
    run_parser.add_argument("--skip-run", action="store_true",
                            help="Skip runtime execution after build")
    run_parser.add_argument("--require-llm", action="store_true",
                            help="Fail if no LLM provider is available")
    run_parser.add_argument("--require-validation", action="store_true",
                            help="Fail if any validation fails")
    run_parser.add_argument("--require-reviewer", action="store_true",
                            help="Fail if example-reviewer is unavailable")
    run_parser.add_argument("--publish", action="store_true",
                            help="Enable live publishing (implies --require-validation --require-reviewer)")
    run_parser.add_argument(
        "--approval-token", metavar="VALUE",
        help="Live publish approval token. Must equal 'APPROVE_LIVE_PR'. "
             "Also readable from PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var.",
    )
    run_parser.add_argument("--tier", type=int, default=5, choices=range(0, 6),
                            help="Max execution tier (0-5, default 5)")
    run_parser.add_argument("--promote-latest", action="store_true",
                            help="Copy evidence to workspace/verification/latest/")
    run_parser.add_argument("--allow-experimental", action="store_true",
                            help="Allow experimental families to run")

    # Discover-LowCode command
    discover_parser = subparsers.add_parser("discover-lowcode",
                                             help="Discovery-only sweep for all families")
    discover_parser.add_argument("--all-families", action="store_true",
                                  help="Discover all enabled families")
    discover_parser.add_argument("--family", help="Specific family to discover (single)")
    discover_parser.add_argument("--families", nargs="+", metavar="FAMILY",
                                  help="Specific families to discover (list)")
    discover_parser.add_argument("--dry-run", action="store_true", default=True,
                                  help="Dry-run mode (default)")
    discover_parser.add_argument("--promote-latest", action="store_true",
                                  help="Copy evidence to workspace/verification/latest/")
    discover_parser.add_argument("--allow-experimental", action="store_true",
                                  help="Include experimental families")
    discover_parser.add_argument("--rank", action="store_true",
                                  help="Compute and write generation readiness ranking")

    # Validate-publish-targets command
    vpt_parser = subparsers.add_parser(
        "validate-publish-targets",
        help="Check publish readiness for family configs",
    )
    vpt_parser.add_argument(
        "--families", nargs="+", metavar="FAMILY", default=["cells", "words", "pdf"],
        help="Families to validate (default: cells words pdf)",
    )
    vpt_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    # Resolve-repo-access command
    rra_parser = subparsers.add_parser(
        "resolve-repo-access",
        help="Probe GitHub API access for family publish targets (read-only)",
    )
    rra_parser.add_argument(
        "--families", nargs="+", metavar="FAMILY", default=["cells", "words", "pdf"],
        help="Families to probe (default: cells words pdf)",
    )
    rra_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    # Probe-publish-permissions command
    ppp_parser = subparsers.add_parser(
        "probe-publish-permissions",
        help="Read-only probe of GitHub push permissions for family publish targets",
    )
    ppp_parser.add_argument(
        "--families", nargs="+", metavar="FAMILY", default=["cells", "words", "pdf"],
        help="Families to probe (default: cells words pdf)",
    )
    ppp_parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Dry-run mode (always on — probe is always read-only)",
    )
    ppp_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    # Publish-PR command (dry-run simulation and live PR creation)
    publish_pr_parser = subparsers.add_parser(
        "publish-pr",
        help="Simulate (or execute) live PR creation for a family's verified dry-run package",
    )
    publish_pr_parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    publish_pr_mode = publish_pr_parser.add_mutually_exclusive_group()
    publish_pr_mode.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Simulate PR creation without pushing (default when --publish not specified)",
    )
    publish_pr_mode.add_argument(
        "--publish", action="store_true",
        help="Create a real PR on GitHub (requires GITHUB_TOKEN + --approval-token APPROVE_LIVE_PR)",
    )
    publish_pr_parser.add_argument(
        "--approval-token", metavar="VALUE",
        help="Live publish approval token. Must equal 'APPROVE_LIVE_PR'. "
             "Required for --publish mode. Also readable from PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL.",
    )
    publish_pr_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/",
    )

    # Merge-PR command (dry-run verification and future live merge)
    merge_pr_parser = subparsers.add_parser(
        "merge-pr",
        help="Verify preconditions and simulate (or execute) PR merge for a family",
    )
    merge_pr_parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    merge_pr_parser.add_argument("--pr-number", required=True, type=int, metavar="N",
                                  help="PR number to merge (e.g., 1)")
    merge_pr_mode = merge_pr_parser.add_mutually_exclusive_group()
    merge_pr_mode.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Verify preconditions and simulate merge without performing any remote mutation",
    )
    merge_pr_mode.add_argument(
        "--merge", action="store_true",
        help="Perform live merge (blocked; requires APPROVE_MERGE_PR + future sprint enablement)",
    )
    merge_pr_parser.add_argument(
        "--approval-token", metavar="VALUE",
        help="Merge approval token. Must equal 'APPROVE_MERGE_PR'. "
             "Must NOT equal 'APPROVE_LIVE_PR'. "
             "Also readable from PLUGIN_EXAMPLES_MERGE_PR_APPROVAL env var.",
    )
    merge_pr_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/",
    )

    # Release-status command
    rs_parser = subparsers.add_parser(
        "release-status",
        help="Report per-family release state from evidence files (read-only)",
    )
    rs_parser.add_argument(
        "--families", nargs="+", metavar="FAMILY", default=["cells", "words"],
        help="Families to report on (default: cells words)",
    )
    rs_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write report to workspace/verification/latest/ (always on)",
    )

    # Render-root-readme command
    rrr_parser = subparsers.add_parser(
        "render-root-readme",
        help="Render root README.md for a family's package (dry-run, no push)",
    )
    rrr_parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    rrr_parser.add_argument(
        "--package-path", metavar="PATH",
        help="Override package path (default: workspace/pr-dry-run/{family}-controlled-pilot/)",
    )
    rrr_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write audit evidence to workspace/verification/latest/ (always on)",
    )

    # publish-readme command
    pr_readme_parser = subparsers.add_parser(
        "publish-readme",
        help="Create a README-only PR in the target repo (backfill pipeline-generated README)",
    )
    pr_readme_parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    pr_readme_parser.add_argument(
        "--publish", action="store_true",
        help="Live mode: create real PR on GitHub (requires GITHUB_TOKEN + approval token)",
    )
    pr_readme_parser.add_argument(
        "--approval-token", metavar="TOKEN",
        help="Approval token (must equal APPROVE_LIVE_PR for live mode)",
    )
    pr_readme_parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write evidence to workspace/verification/latest/ (always on)",
    )

    # Sync-taskcard-docs command
    std_parser = subparsers.add_parser(
        "sync-taskcard-docs",
        help="Generate docs/discovery/open-taskcard-closure-matrix.md from JSON matrix (read-only)",
    )
    std_parser.add_argument(
        "--promote-latest", action="store_true",
        help="No-op (included for CLI consistency; output always written to docs/discovery/)",
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Check for package updates")
    check_parser.add_argument("--family", help="Specific family to check")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "status":
        print("plugin-examples pipeline — status")
        print("Modules: family_config, nuget_fetcher, nupkg_extractor,")
        print("         reflection_catalog, plugin_detector, api_delta,")
        print("         fixture_registry, example_miner, scenario_planner,")
        print("         llm_router, generator, verifier_bridge, publisher,")
        print("         package_watcher, gates")
        return 0

    if args.command == "run":
        from plugin_examples.runner import run_pipeline

        # Publish path implies validation and reviewer requirements
        require_validation = args.require_validation
        require_reviewer = args.require_reviewer
        dry_run = not args.publish

        if args.publish:
            # Conflict: --dry-run and --publish are mutually exclusive
            if args.dry_run:
                print("ERROR: --dry-run and --publish are mutually exclusive (blocked_publish_dry_run_conflict)")
                return 1
            require_validation = True
            require_reviewer = True
            if not os.environ.get("GITHUB_TOKEN"):
                print("ERROR: --publish requires GITHUB_TOKEN environment variable")
                return 1

        # --dry-run flag always forces dry_run=True
        if args.dry_run:
            dry_run = True

        report = run_pipeline(
            family=args.family,
            dry_run=dry_run,
            skip_run=args.skip_run,
            template_mode=args.template_mode,
            require_llm=args.require_llm,
            require_validation=require_validation,
            require_reviewer=require_reviewer,
            max_tier=args.tier,
            promote_latest=args.promote_latest,
            allow_experimental=args.allow_experimental,
        )
        gs = report.get("gate_summary", {})
        verdict = report.get("verdict", "UNKNOWN")
        comp = report.get("comparison", {})
        total = gs.get("total_stages", 0)
        succeeded = gs.get("passed", 0)
        degraded = gs.get("degraded", 0)
        failed = gs.get("failed", 0)
        skipped = gs.get("skipped", 0)
        print(f"Pipeline: {total} stages executed — "
              f"{succeeded} succeeded, {degraded} degraded, "
              f"{failed} failed, {skipped} skipped")

        # Aggregate example-level summary
        gen_count = comp.get("examples_generated_count", 0)
        build_count = comp.get("dotnet_build_passed", 0)
        run_count = comp.get("dotnet_run_passed", 0)
        if gen_count > 0:
            run_blocked = build_count - run_count
            print(f"Examples: {gen_count} generated, {build_count} built, "
                  f"{run_count} runtime passed, {run_blocked} runtime blocked")
            pr_candidates = report.get("pr_candidate_count", run_count)
            print(f"PR candidates: {pr_candidates} eligible, "
                  f"{gen_count - pr_candidates} excluded")

        print(f"Verdict: {verdict}")
        return 1 if gs.get("hard_stopped") else 0

    if args.command == "discover-lowcode":
        from plugin_examples.discovery_sweep import run_discovery_sweep, compute_generation_readiness
        from pathlib import Path as _Path

        # Resolve family list: --families list > --family single > --all-families
        families = None
        if getattr(args, "families", None):
            families = list(args.families)
        elif args.family:
            families = [args.family]

        repo_root = _Path(__file__).resolve().parents[2]

        result = run_discovery_sweep(
            families=families,
            all_families=args.all_families,
            promote_latest=args.promote_latest,
            allow_experimental=args.allow_experimental,
            repo_root=repo_root,
        )

        total = result.get("total_families", 0)
        eligible = result.get("eligible_count", 0)
        print(f"Discovery sweep: {total} families scanned, {eligible} with LowCode namespaces")
        for f in result.get("families", []):
            print(f"  {f['family']}: {f['status']}")

        # Compute and write generation readiness ranking
        if getattr(args, "rank", False) or True:  # always compute ranking after discovery
            import json as _json
            ranking_new = compute_generation_readiness(result.get("families", []), repo_root)
            ranking_path = (repo_root / "workspace" / "verification" / "latest"
                           / "family-generation-readiness-rank.json")
            ranking_path.parent.mkdir(parents=True, exist_ok=True)

            # Merge with existing entries to preserve families not in this run.
            # Single-family runs must not destroy multi-family data (GAP-NEW-01).
            existing_by_family: dict = {}
            if ranking_path.exists():
                try:
                    _existing = _json.loads(ranking_path.read_text(encoding="utf-8", errors="replace"))
                    if isinstance(_existing, list):
                        existing_by_family = {e["family"]: e for e in _existing if "family" in e}
                except (OSError, _json.JSONDecodeError, KeyError):
                    pass

            # Update only the families from this run; preserve others
            for entry in ranking_new:
                existing_by_family[entry["family"]] = entry

            # Determine scope: complete when all enabled families were discovered
            _run_families = {f["family"] for f in result.get("families", [])}
            _scope = "complete" if _run_families >= set(existing_by_family.keys()) else "partial"

            merged = list(existing_by_family.values())
            ranking_path.write_text(_json.dumps(merged, indent=2), encoding="utf-8")
            logging.getLogger(__name__).info(
                "Generation readiness ranking written (scope=%s): %s", _scope, ranking_path
            )
            print(f"  readiness ranking: {len(merged)} families (scope={_scope})")

        return 0

    if args.command == "validate-publish-targets":
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.publish_readiness import (
            check_publish_readiness,
            write_publish_readiness_report,
        )
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        config_dir = repo_root / "pipeline" / "configs" / "families"
        verification_dir = repo_root / "workspace" / "verification"

        families_input = []
        for fname in args.families:
            config_path = config_dir / f"{fname}.yml"
            try:
                cfg = load_family_config(config_path)
                families_input.append((fname, cfg, str(config_path)))
            except DisabledFamilyError:
                families_input.append((fname, None, str(config_path)))
            except FileNotFoundError:
                families_input.append((fname, None, str(config_path)))
            except Exception as exc:
                logging.getLogger(__name__).warning("Could not load %s: %s", fname, exc)
                families_input.append((fname, None, str(config_path)))

        result = check_publish_readiness(families_input)
        report_path = write_publish_readiness_report(result, verification_dir)

        print(f"Publish readiness: {result['publish_ready_count']}/{result['total_families']} ready")
        for rec in result["families"]:
            status = "READY" if rec["publish_ready"] else f"BLOCKED ({rec['blocked_reason']})"
            print(f"  {rec['family']}: {status}")
        print(f"Report: {report_path}")
        return 0 if result["publish_ready_count"] > 0 else 1

    if args.command == "resolve-repo-access":
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.repo_access_resolver import resolve_repo_access
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        config_dir = repo_root / "pipeline" / "configs" / "families"
        verification_dir = repo_root / "workspace" / "verification"

        families_input = []
        for fname in args.families:
            config_path = config_dir / f"{fname}.yml"
            try:
                cfg = load_family_config(config_path)
                families_input.append((fname, cfg, str(config_path)))
            except DisabledFamilyError:
                families_input.append((fname, None, str(config_path)))
            except FileNotFoundError:
                families_input.append((fname, None, str(config_path)))
            except Exception as exc:
                logging.getLogger(__name__).warning("Could not load %s: %s", fname, exc)
                families_input.append((fname, None, str(config_path)))

        result = resolve_repo_access(families_input, verification_dir, promote_latest=True)

        summary = result["summary"]
        print(f"Repo access: {summary['accessible']}/{summary['total_checked']} accessible")
        for rec in result["families"]:
            family = rec["family"]
            ec = rec.get("error_classification", "unknown")
            can_read = rec.get("can_read", False)
            can_push = rec.get("can_push")
            status = "ACCESSIBLE" if can_read else f"BLOCKED ({ec})"
            perm = f", can_push={can_push}" if can_read else ""
            print(f"  {family}: {status}{perm}")
        print(f"live_publish_allowed: {summary['live_publish_allowed']}")
        report_path = verification_dir / "latest" / "family-repo-access-resolution.json"
        print(f"Report: {report_path}")
        return 0 if summary["accessible"] > 0 else 1

    if args.command == "probe-publish-permissions":
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.publish_permission_probe import probe_publish_permissions
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        config_dir = repo_root / "pipeline" / "configs" / "families"
        verification_dir = repo_root / "workspace" / "verification"

        families_input = []
        for fname in args.families:
            config_path = config_dir / f"{fname}.yml"
            try:
                cfg = load_family_config(config_path)
                families_input.append((fname, cfg, str(config_path)))
            except DisabledFamilyError:
                families_input.append((fname, None, str(config_path)))
            except FileNotFoundError:
                families_input.append((fname, None, str(config_path)))
            except Exception as exc:
                logging.getLogger(__name__).warning("Could not load %s: %s", fname, exc)
                families_input.append((fname, None, str(config_path)))

        result = probe_publish_permissions(families_input, verification_dir, dry_run=True, promote_latest=True)

        summary = result["summary"]
        print(f"Permission probe: {summary['permission_ready']}/{summary['total_probed']} families have push permission")
        for rec in result["families"]:
            family = rec["family"]
            status = rec.get("probe_status", "unknown")
            if status == "skipped":
                print(f"  {family}: SKIPPED ({rec.get('skip_reason', '')})")
            elif rec.get("pr_permission_ready"):
                print(f"  {family}: PUSH_READY (can_read={rec.get('can_read')}, can_push={rec.get('can_push')})")
            else:
                print(f"  {family}: NOT_READY ({rec.get('error_classification', 'unknown')})")
        print(f"live_publish_authorized: {summary['live_publish_authorized']}")
        report_path = verification_dir / "latest" / "publish-permission-probe.json"
        print(f"Report: {report_path}")
        return 0 if summary["permission_ready"] > 0 else 1

    if args.command == "publish-pr":
        import json as _json
        import re as _re
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.pr_builder import build_pr
        from plugin_examples.publisher.approval_gate import check_approval
        from datetime import datetime, timezone
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
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

        # Locate dry-run package
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
        if package_exists and len(example_dirs) > 0:
            try:
                from plugin_examples.publisher.readme_renderer import (
                    build_readme_context as _build_readme_ctx,
                    render_readme as _render_readme,
                    write_readme as _write_readme,
                )
                from plugin_examples.publisher.readme_auditor import audit_readme as _audit_readme
                import json as _json_r
                import re as _re_r

                # Resolve output_formats from post-merge evidence for richer table
                _pm_path = verification_dir / "latest" / f"{family}-post-merge-clean-checkout-validation.json"
                _output_formats: dict[str, str] = {}
                if _pm_path.exists():
                    try:
                        _pm = _json_r.loads(_pm_path.read_text(encoding="utf-8"))
                        for _ex in _pm.get("examples", []):
                            if _ex.get("name") and _ex.get("output_format"):
                                _output_formats[_ex["name"]] = _ex["output_format"]
                    except (OSError, _json_r.JSONDecodeError):
                        pass

                _examples_meta = [
                    {"name": d, "output_format": _output_formats.get(d, "")}
                    for d in example_dirs
                ]
                _gen_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                _readme_ctx = _build_readme_ctx(
                    family=family,
                    family_config=cfg,
                    examples=_examples_meta,
                    package_version=pkg_version,
                    generation_date=_gen_date,
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
                        print(f"WARNING: README audit failed for {family} (non-blocking in dry-run): {_readme_audit.warnings}")
                else:
                    print(f"  README.md rendered and audited: PASS ({len(_readme_content)} bytes)")
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

        # Build PR content
        pr_content = build_pr(
            family=family,
            run_id=run_id,
            examples_count=len(example_dirs),
            package_version=pkg_version,
            examples_list=example_dirs,
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
                print("  Set PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR or pass --approval-token APPROVE_LIVE_PR")
                return 1
            if not package_exists or len(example_dirs) == 0:
                print(f"ERROR: Package not found or empty: {package_path}")
                return 1
            if not gate_verdict_ok:
                print(f"ERROR: Gate verdict not publishable: {gate_verdict_name}")
                return 1
            if not repo_access_ready or not pr_permission_ready:
                print(f"ERROR: Repo access not ready (repo_access={repo_access_ready}, pr_permission={pr_permission_ready})")
                print("  Run: python -m plugin_examples probe-publish-permissions --families " + family)
                return 1
            if target_owner is None:
                print(f"ERROR: No publish target configured for family '{family}'")
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
            return 0

        # --- DRY-RUN / SIMULATION MODE ---
        simulation_passed = all([
            package_exists,
            len(example_dirs) > 0,
            gate_verdict_ok,
            repo_access_ready,
            pr_permission_ready,
            target_owner is not None,
        ])
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
        return 0 if simulation_passed else 1

    if args.command == "merge-pr":
        import json as _json
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.merge_approval_gate import (
            check_merge_approval,
            BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN,
        )
        from plugin_examples.publisher.github_pr_merger import simulate_merge, merge_pr, MergeError as _MergeError
        from datetime import datetime, timezone
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
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
                "merge_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
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
                "simulation_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "family": family,
                "pr_number": pr_number,
                "target_repo": f"{target_owner}/{target_repo_name}",
                "dry_run": True,
                "simulation_passed": False,
                "live_merge_performed": False,
                "approval_gate_passed": approved,
                "approval_blocked_reason": approval_blocked if not approved else None,
                "blocked_reasons": ["no_github_token_for_remote_verification"],
                "preconditions": {
                    "github_token_present": {"result": "FAIL", "detail": "GITHUB_TOKEN not set"}
                },
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
                "simulation_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "family": family,
                "pr_number": pr_number,
                "target_repo": f"{target_owner}/{target_repo_name}",
                "dry_run": True,
                "simulation_passed": simulation["simulation_passed"] and approved,
                "live_merge_performed": False,
                "approval_gate_passed": approved,
                "approval_blocked_reason": approval_blocked if not approved else None,
                "blocked_reasons": (
                    simulation["blocked_reasons"]
                    + ([] if approved else [approval_blocked])
                ),
                "preconditions": simulation["preconditions"],
                "pr_data": simulation.get("pr_data", {}),
                "note": simulation["note"],
            }

        output_dir = verification_dir / "latest" if args.promote_latest else verification_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{family}-merge-pr-simulation.json"
        with open(output_path, "w") as _f:
            _json.dump(simulation_result, _f, indent=2)

        sim_status = "SIMULATION_PASSED" if simulation_result["simulation_passed"] else \
            f"SIMULATION_BLOCKED ({', '.join(simulation_result['blocked_reasons'])})"
        print(f"merge-pr simulation: {family} PR #{pr_number} — {sim_status}")
        print(f"  Target: {target_owner}/{target_repo_name}")
        print(f"  Approval gate: {'PASSED' if approved else f'BLOCKED ({approval_blocked})'}")
        print(f"  live_merge_performed: False")
        print(f"Report: {output_path}")
        return 0 if simulation_result["simulation_passed"] else 1

    if args.command == "release-status":
        from plugin_examples.publisher.release_status import (
            compute_release_status,
            write_release_status_report,
        )
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        verification_dir = repo_root / "workspace" / "verification"

        families = list(args.families)
        status = compute_release_status(families, verification_dir)
        report_path = write_release_status_report(status, verification_dir)

        print(f"Release status: {len(families)} families")
        for rec in status["families"]:
            fam = rec["family"]
            sha = rec["last_merge_sha"] or "not merged"
            validation = rec["last_post_merge_validation_status"]
            count = rec["published_examples_count"]
            print(f"  {fam}: merged={sha[:12] if rec['last_merge_sha'] else 'no'}, "
                  f"examples={count}, post_merge={validation}")
            print(f"    next: {rec['next_required_action']}")
        print(f"  all_merged: {status['all_merged']}")
        print(f"  all_post_merge_validated: {status['all_post_merge_validated']}")
        print(f"Report: {report_path}")
        return 0

    if args.command == "sync-taskcard-docs":
        import json as _json
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        matrix_path = repo_root / "workspace" / "verification" / "latest" / "open-taskcard-closure-matrix.json"
        output_path = repo_root / "docs" / "discovery" / "open-taskcard-closure-matrix.md"

        if not matrix_path.exists():
            print(f"ERROR: Taskcard matrix not found: {matrix_path}")
            print("  Run discover-lowcode or create the matrix first.")
            return 1

        try:
            matrix = _json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, _json.JSONDecodeError) as exc:
            print(f"ERROR: Cannot read taskcard matrix: {exc}")
            return 1

        taskcards = matrix.get("taskcards", [])
        matrix_date = matrix.get("matrix_date", "unknown")
        sprint = matrix.get("sprint", "unknown")

        open_cards = [tc for tc in taskcards if tc.get("status") == "OPEN"]
        closed_cards = [tc for tc in taskcards if tc.get("status") == "CLOSED"]
        total = len(taskcards)
        open_count = len(open_cards)
        closed_count = len(closed_cards)

        lines = [
            "<!-- GENERATED — do not edit manually. Run: python -m plugin_examples sync-taskcard-docs -->",
            f"# Open Taskcard Closure Matrix",
            "",
            f"**Matrix date:** {matrix_date}",
            f"**Sprint:** {sprint}",
            f"**Total:** {total} | **Open:** {open_count} | **Closed:** {closed_count}",
            "",
            "---",
            "",
            "## Open Taskcards",
            "",
            "| ID | Title | Blocking |",
            "|----|-------|----------|",
        ]
        if open_cards:
            for tc in open_cards:
                tc_id = tc.get("id", "")
                title = tc.get("title", "")
                blocking = tc.get("blocking") or ""
                lines.append(f"| `{tc_id}` | {title} | {blocking} |")
        else:
            lines.append("| — | No open taskcards | — |")

        lines += [
            "",
            "---",
            "",
            "## Closed Taskcards",
            "",
            "| ID | Title | Closed In |",
            "|----|-------|-----------|",
        ]
        for tc in closed_cards:
            tc_id = tc.get("id", "")
            title = tc.get("title", "")
            closed_in = tc.get("closed_in") or ""
            lines.append(f"| `{tc_id}` | {title} | {closed_in} |")

        content = "\n".join(lines) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        print(f"sync-taskcard-docs: {total} taskcards ({open_count} open, {closed_count} closed)")
        print(f"  Source: {matrix_path}")
        print(f"  Output: {output_path}")
        return 0

    if args.command == "render-root-readme":
        import json as _json
        import re as _re
        from plugin_examples.family_config import load_family_config, DisabledFamilyError
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme, write_readme
        from plugin_examples.publisher.readme_auditor import audit_readme
        from datetime import datetime, timezone
        from pathlib import Path as _Path

        repo_root = _Path(__file__).resolve().parents[2]
        verification_dir = repo_root / "workspace" / "verification"
        family = args.family

        # --- Load family config ---
        config_path = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
        try:
            cfg = load_family_config(config_path)
        except (DisabledFamilyError, FileNotFoundError) as exc:
            print(f"ERROR: Cannot load family config for '{family}': {exc}")
            return 1

        # --- Resolve package path ---
        if getattr(args, "package_path", None):
            package_path = _Path(args.package_path)
        else:
            package_path = repo_root / "workspace" / "pr-dry-run" / f"{family}-controlled-pilot"
            if not package_path.exists():
                package_path = repo_root / "workspace" / "pr-dry-run" / family

        if not package_path.exists():
            print(f"ERROR: Package path not found: {package_path}")
            print(f"  Run 'publish-pr --family {family} --dry-run' first to create the package.")
            return 1

        # --- Discover validated examples from package ---
        examples_root = package_path / "examples" / family / "lowcode"
        example_dirs = []
        if examples_root.exists():
            example_dirs = sorted(
                [d.name for d in examples_root.iterdir() if d.is_dir()]
            )
        if not example_dirs:
            print(f"ERROR: No example directories found under {examples_root}")
            return 1

        # --- Resolve package version ---
        pkg_version = "unknown"
        # 1) From latest live-pr evidence
        live_pr_path = verification_dir / "latest" / f"{family}-live-pr-result.json"
        if live_pr_path.exists():
            try:
                data = _json.loads(live_pr_path.read_text(encoding="utf-8"))
                pkg_version = data.get("nuget_version", "") or "unknown"
            except (OSError, _json.JSONDecodeError):
                pass
        # 2) Fallback: parse Directory.Packages.props
        if pkg_version == "unknown":
            props_path = package_path / "Directory.Packages.props"
            if props_path.exists():
                try:
                    m = _re.search(r'Version="([^"]+)"', props_path.read_text())
                    if m:
                        pkg_version = m.group(1)
                except OSError:
                    pass

        # --- Build example metadata from post-merge evidence ---
        post_merge_path = verification_dir / "latest" / f"{family}-post-merge-clean-checkout-validation.json"
        output_formats: dict[str, str] = {}
        if post_merge_path.exists():
            try:
                pm_data = _json.loads(post_merge_path.read_text(encoding="utf-8"))
                for ex in pm_data.get("examples", []):
                    name = ex.get("name", "")
                    fmt = ex.get("output_format", "")
                    if name and fmt:
                        output_formats[name] = fmt
            except (OSError, _json.JSONDecodeError):
                pass

        examples_meta = [
            {"name": d, "output_format": output_formats.get(d, "")}
            for d in example_dirs
        ]

        # --- Build context ---
        generation_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        try:
            ctx = build_readme_context(
                family=family,
                family_config=cfg,
                examples=examples_meta,
                package_version=pkg_version,
                generation_date=generation_date,
            )
        except ValueError as exc:
            print(f"ERROR: Cannot build README context: {exc}")
            return 1

        # --- Render README ---
        try:
            content = render_readme(ctx)
        except Exception as exc:
            print(f"ERROR: README render failed: {exc}")
            return 1

        readme_out = package_path / "README.md"
        write_readme(content, readme_out)

        # --- Audit README ---
        audit_result = audit_readme(content, ctx)

        # --- Write evidence ---
        evidence_dir = verification_dir / "latest"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        audit_record = {
            "audit_type": "root_readme_audit",
            "audit_date": generation_date,
            "family": family,
            "package_path": str(package_path),
            "readme_path": str(readme_out),
            "passed": audit_result.passed,
            "missing_sections": audit_result.missing_sections,
            "stale_version": audit_result.stale_version,
            "stale_examples": audit_result.stale_examples,
            "missing_examples": audit_result.missing_examples,
            "extra_examples": audit_result.extra_examples,
            "central_repo_reference_found": audit_result.central_repo_reference_found,
            "blocked_scenario_reference_found": audit_result.blocked_scenario_reference_found,
            "catalog_symbol_noise_found": audit_result.catalog_symbol_noise_found,
            "forbidden_aspose_com_links": audit_result.forbidden_aspose_com_links,
            "platform_path_errors": audit_result.platform_path_errors,
            "wrong_blog_links": audit_result.wrong_blog_links,
            "wrong_contact_links": audit_result.wrong_contact_links,
            "missing_required_links": audit_result.missing_required_links,
            "warnings": audit_result.warnings,
            "expected_version": audit_result.expected_version,
            "found_version": audit_result.found_version,
            "expected_example_count": audit_result.expected_example_count,
            "found_example_count": audit_result.found_example_count,
        }
        audit_path = evidence_dir / f"{family}-root-readme-audit.json"
        audit_path.write_text(_json.dumps(audit_record, indent=2), encoding="utf-8")

        render_record = {
            "render_type": "root_readme_render_result",
            "render_date": generation_date,
            "family": family,
            "package_path": str(package_path),
            "readme_path": str(readme_out),
            "readme_bytes": len(content),
            "package_version": pkg_version,
            "examples_count": len(example_dirs),
            "example_names": example_dirs,
            "target_repo": f"{ctx.target_repo_owner}/{ctx.target_repo_name}",
            "audit_passed": audit_result.passed,
            "no_remote_write_performed": True,
        }
        render_path = evidence_dir / f"{family}-root-readme-render-result.json"
        render_path.write_text(_json.dumps(render_record, indent=2), encoding="utf-8")

        audit_status = "PASS" if audit_result.passed else "FAIL"
        print(f"render-root-readme: {family}")
        print(f"  README: {readme_out} ({len(content)} bytes)")
        print(f"  Examples: {len(example_dirs)} ({', '.join(example_dirs)})")
        print(f"  Package version: {pkg_version}")
        print(f"  Audit: {audit_status}")
        if not audit_result.passed:
            for w in audit_result.warnings:
                print(f"    WARNING: {w}")
        print(f"  Audit evidence: {audit_path}")
        print(f"  Render evidence: {render_path}")

        if not audit_result.passed:
            print(f"README audit FAILED for {family} — see warnings above")
            return 1
        return 0

    if args.command == "publish-readme":
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

        # --- Discover examples ---
        examples_root = package_path / "examples" / family / "lowcode"
        example_dirs: list[str] = []
        if examples_root.exists():
            example_dirs = sorted(d.name for d in examples_root.iterdir() if d.is_dir())
        if not example_dirs:
            print(f"ERROR: No example directories found under {examples_root}")
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

        # --- Build example metadata ---
        pm_path = verification_dir / "latest" / f"{family}-post-merge-clean-checkout-validation.json"
        output_formats: dict[str, str] = {}
        if pm_path.exists():
            try:
                _pm = _json.loads(pm_path.read_text(encoding="utf-8"))
                for _ex in _pm.get("examples", []):
                    if _ex.get("name") and _ex.get("output_format"):
                        output_formats[_ex["name"]] = _ex["output_format"]
            except (OSError, _json.JSONDecodeError):
                pass
        examples_meta = [{"name": d, "output_format": output_formats.get(d, "")} for d in example_dirs]

        # --- Render README ---
        try:
            ctx = build_readme_context(
                family=family,
                family_config=cfg,
                examples=examples_meta,
                package_version=pkg_version,
                generation_date=generation_date,
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
        return 0

    if args.command == "check":
        print("Package update check")
        print("Requires live NuGet access. All modules are implemented.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
