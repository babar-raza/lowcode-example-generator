"""Command: render-root-readme."""

from __future__ import annotations

from plugin_examples.commands._metrics import _add_metrics_flags, _create_metrics_session, _finalize_metrics_session


def add_parser(subparsers):
    """Register the render-root-readme subcommand."""
    # Render-root-readme command
    parser = subparsers.add_parser(
        "render-root-readme",
        help="Render root README.md for a family's package (dry-run, no push)",
    )
    parser.add_argument("--family", required=True, help="Family name (e.g., cells, words)")
    parser.add_argument(
        "--package-path", metavar="PATH",
        help="Override package path (default: workspace/pr-dry-run/{family}-controlled-pilot/)",
    )
    parser.add_argument(
        "--promote-latest", action="store_true",
        help="Write audit evidence to workspace/verification/latest/ (always on)",
    )
    parser.add_argument(
        "--cumulative", action="store_true",
        help="Use cumulative inventory (all packages + post-merge evidence) instead of single package",
    )
    
    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the render-root-readme command."""
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
    msession, mcollector = _create_metrics_session(
        args, command="render-root-readme", family=family, repo_root=repo_root,
    )

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

    # --- Cumulative example discovery via readme_inventory ---
    from plugin_examples.publisher.readme_inventory import (
        discover_family_inventory as _discover_inv_rr,
        build_cumulative_examples_meta as _build_cum_meta_rr,
        build_package_path_map as _build_pkg_map_rr,
    )

    _cumulative = getattr(args, "cumulative", False)
    if _cumulative:
        _inv_entries_rr, _inv_trail_rr = _discover_inv_rr(
            family=family,
            repo_root=repo_root,
            inventory_mode="repo_actual",
        )
    else:
        _inv_entries_rr, _inv_trail_rr = _discover_inv_rr(
            family=family,
            repo_root=repo_root,
            inventory_mode="current_package_overlay",
            current_package_path=package_path,
        )
    _examples_meta_rr = _build_cum_meta_rr(_inv_entries_rr)
    _pkg_path_map_rr = _build_pkg_map_rr(_inv_entries_rr)
    example_dirs = [e["name"] for e in _examples_meta_rr]

    if not example_dirs:
        print(f"ERROR: No examples discovered for family '{family}'")
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

    # --- Build context ---
    generation_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        ctx = build_readme_context(
            family=family,
            family_config=cfg,
            examples=_examples_meta_rr,
            package_version=pkg_version,
            generation_date=generation_date,
            package_path=package_path,
            package_path_map=_pkg_path_map_rr if _pkg_path_map_rr else None,
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
        _finalize_metrics_session(msession, items_discovered=1, items_succeeded=0, items_failed=1)
        return 1
    _finalize_metrics_session(msession, items_discovered=1, items_succeeded=1, items_failed=0)
    return 0

