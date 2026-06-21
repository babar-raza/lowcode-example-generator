"""Command: run."""

from __future__ import annotations

import os
from pathlib import Path

from plugin_examples.commands._metrics import _add_metrics_flags


def add_parser(subparsers):
    """Register the run subcommand."""
    # Run command
    parser = subparsers.add_parser("run", help="Run the pipeline for a family")
    parser.add_argument("--family", required=True, help="Family name (e.g., cells)")
    parser.add_argument(
        "--family-config",
        metavar="PATH",
        default=None,
        help="Custom family config YAML path. Defaults to pipeline/configs/families/{family}.yml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (default)")
    parser.add_argument("--template-mode", action="store_true", help="Use template generation instead of LLM")
    parser.add_argument("--skip-run", action="store_true", help="Skip runtime execution after build")
    parser.add_argument("--require-llm", action="store_true", help="Fail if no LLM provider is available")
    parser.add_argument("--require-validation", action="store_true", help="Fail if any validation fails")
    parser.add_argument("--require-reviewer", action="store_true", help="Fail if example-reviewer is unavailable")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Enable live publishing (implies --require-validation --require-reviewer)",
    )
    parser.add_argument(
        "--approval-token",
        metavar="VALUE",
        help="Live publish approval token. Must equal 'APPROVE_LIVE_PR'. "
        "Also readable from PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var.",
    )
    parser.add_argument("--tier", type=int, default=5, choices=range(0, 6), help="Max execution tier (0-5, default 5)")
    parser.add_argument("--promote-latest", action="store_true", help="Copy evidence to workspace/verification/latest/")
    parser.add_argument("--allow-experimental", action="store_true", help="Allow experimental families to run")
    parser.add_argument(
        "--compare-run",
        metavar="PRIOR_RUN_ID",
        help="Compare current run results against a prior run to detect regressions",
    )
    parser.add_argument(
        "--replay-from",
        metavar="STEP",
        choices=["generation", "validation", "reviewer", "publisher"],
        default=None,
        help=(
            "Replay pipeline from STEP, reusing artifacts from a prior run for earlier stages. "
            "Valid values: generation, validation, reviewer, publisher. "
            "Infra stages (nuget_fetch, extraction, reflection) are always skipped and "
            "catalog restored from the prior run. scenario_planning always re-runs (denominator safety). "
            "Requires a prior pilot-{family}-* run (auto-detected or specified via --reuse-run)."
        ),
    )
    parser.add_argument(
        "--reuse-run",
        metavar="RUN_ID",
        default=None,
        help=(
            "Prior run ID to load reusable artifacts from (e.g., pilot-pdf-20260513-180040). "
            "If omitted with --replay-from, the most recent pilot-{family}-* run is used. "
            "Must be a pilot run; discovery- and multi-family- prefixed runs are rejected."
        ),
    )

    parser.add_argument(
        "--no-strict-output",
        action="store_true",
        help=(
            "Disable strict output validation (default: strict mode ON). "
            "When set, advisory_no_output and advisory_failed are treated as advisory-only "
            "and do not block publication. Use for families with known output limitations."
        ),
    )

    parser.add_argument(
        "--allow-low-quality",
        action="store_true",
        help=(
            "Allow examples with quality_score < 0.6 to proceed to PR creation (TC-SRHP-13). "
            "By default, LOW-quality examples block PR creation (quality hard gate). "
            "Use for families where known limitations prevent high quality scores."
        ),
    )

    # Agent metrics flags (shared across commands)
    _add_metrics_flags(parser)
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the run command."""
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

    # Metrics initialization (lazy — only when --metrics flag is set)
    metrics_collector = None
    metrics_config = None
    metrics_enabled = getattr(args, "metrics", False) or os.environ.get("AGENT_METRICS_ENABLED", "").lower() == "true"

    if metrics_enabled:
        from plugin_examples.metrics.config import load_metrics_config
        from plugin_examples.metrics.models import MetricsCollector

        metrics_collector = MetricsCollector()
        config_path = None
        if getattr(args, "metrics_config", None):
            config_path = Path(args.metrics_config)
        metrics_config = load_metrics_config(config_path=config_path)
        # run command uses run_pipeline's built-in finalize_metrics
        # which has access to full PipelineContext for accurate counts

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
        compare_run=getattr(args, "compare_run", None),
        replay_from=getattr(args, "replay_from", None),
        reuse_run_id=getattr(args, "reuse_run", None),
        metrics_collector=metrics_collector,
        metrics_config=metrics_config,
        metrics_post=getattr(args, "metrics_post", False),
        metrics_job_type=getattr(args, "metrics_job_type", None),
        metrics_strict=getattr(args, "metrics_strict", False),
        metrics_force_repost=getattr(args, "metrics_force_repost", False),
        family_config_path=getattr(args, "family_config", None),
        strict_output_validation=not getattr(args, "no_strict_output", False),
        allow_low_quality=getattr(args, "allow_low_quality", False),
    )
    gs = report.get("gate_summary", {})
    verdict = report.get("verdict", "UNKNOWN")
    comp = report.get("comparison", {})
    total = gs.get("total_stages", 0)
    succeeded = gs.get("passed", 0)
    degraded = gs.get("degraded", 0)
    failed = gs.get("failed", 0)
    skipped = gs.get("skipped", 0)
    print(
        f"Pipeline: {total} stages executed — "
        f"{succeeded} succeeded, {degraded} degraded, "
        f"{failed} failed, {skipped} skipped"
    )

    # Aggregate example-level summary
    gen_count = comp.get("examples_generated_count", 0)
    build_count = comp.get("dotnet_build_passed", 0)
    run_count = comp.get("dotnet_run_passed", 0)
    if gen_count > 0:
        run_blocked = build_count - run_count
        print(
            f"Examples: {gen_count} generated, {build_count} built, "
            f"{run_count} runtime passed, {run_blocked} runtime blocked"
        )
        pr_candidates = report.get("pr_candidate_count", run_count)
        print(f"PR candidates: {pr_candidates} eligible, " f"{gen_count - pr_candidates} excluded")

    print(f"Verdict: {verdict}")

    # Metrics finalization (only when --metrics enabled)
    if metrics_enabled and metrics_config:
        metrics_result = report.get("_metrics_result")
        if metrics_result:
            if metrics_result.get("post_result", {}).get("posted"):
                print("Metrics: posted successfully")
            elif metrics_result.get("error"):
                print(f"Metrics: error — {metrics_result['error']}")
            else:
                reason = metrics_result.get("post_result", {}).get("reason", "dry_run")
                print(f"Metrics: not posted ({reason})")

    return 1 if gs.get("hard_stopped") else 0
