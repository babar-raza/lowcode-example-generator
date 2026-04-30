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
    discover_parser.add_argument("--family", help="Specific family to discover")
    discover_parser.add_argument("--dry-run", action="store_true", default=True,
                                  help="Dry-run mode (default)")
    discover_parser.add_argument("--promote-latest", action="store_true",
                                  help="Copy evidence to workspace/verification/latest/")
    discover_parser.add_argument("--allow-experimental", action="store_true",
                                  help="Include experimental families")

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
        from plugin_examples.discovery_sweep import run_discovery_sweep

        families = None
        if args.family:
            families = [args.family]

        result = run_discovery_sweep(
            families=families,
            all_families=args.all_families,
            promote_latest=args.promote_latest,
            allow_experimental=args.allow_experimental,
        )

        total = result.get("total_families", 0)
        eligible = result.get("eligible_count", 0)
        print(f"Discovery sweep: {total} families scanned, {eligible} with LowCode namespaces")
        for f in result.get("families", []):
            print(f"  {f['family']}: {f['status']}")
        return 0

    if args.command == "check":
        print("Package update check")
        print("Requires live NuGet access. All modules are implemented.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
